from django.shortcuts import render
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db.models import OuterRef, Exists, Q
import logging
from wfb.feedbacks.models import FeedbackQuestion, Rating, FeedbackResponse, Feedback
from wfb.core.services import CoreService
from wfb.core.pagination import paginate_objects
from wfb.core.decorators import profile_complete_required
from wfb.users.exceptions import TotalPointsNotEnoughException
from .forms import (
    JobForm,
    ProposalForm,
    ContractForm,
    AcceptContractForm,
    SubmitWorkForm,
    AcceptWorkForm,
    JobSearchForm,
    FlagJobForm,
)
from .models import Job, Proposal, Contract, FlaggedJob, ProfessionalSavedJob
from .services import JobService
from wfb.users.models import Professional
from wfb.users.services import ProfessionalService
from wfb.notifications.services import NotificationService

logger = logging.getLogger(__name__)


@login_required()
def job_proposals(request, idjob):
    job = get_object_or_404(Job, id=idjob)
    qs_proposals = job.proposal_set.select_related("created_by", "created_by__user")
    context = {
        "is_proposal_listing": True,
        "title": "job proposals",
        "job": job,
    }
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
        qs_proposals = qs_proposals.filter(created_by=request.user.professional)
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    context.update({"proposals": qs_proposals})
    return render(request, f"{template_prefix}/jobs/proposals/list.html", context)


@login_required()
def proposals(request):
    qs_proposals = request.user.professional.proposal_set.select_related(
        "created_by", "created_by__user"
    ).order_by("-created_date")
    context = {
        "is_proposal_listing": True,
        "title": "my proposals",
        "proposals": qs_proposals,
    }
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/jobs/proposals/list.html", context)


@login_required()
def proposal_detail(request, idjob: str, proposal_id: str):
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
        Q_qs = Q(created_by=request.user.professional)

    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
        Q_qs = Q(job__created_by=request.user.client)

    try:
        job = Job.objects.get(id=idjob)
        proposal = Proposal.objects.filter(Q_qs).get(id=proposal_id)
        context = {
            "is_proposal_listing": False,
            "title": "proposal detail",
            "job": job,
            "proposal": proposal,
            "show_full_coverletter": True,
            "is_proposal_detail": True,
        }
        if request.user.client:
            proposal.viewed_date = timezone.now()
            proposal.save()
            try:
                NotificationService.proposal_viewed(proposal)
            except Exception as e:
                logger.exception(f"Could not send notification: {e}")
        return render(request, f"{template_prefix}/jobs/proposals/detail.html", context)
    except (Job.DoesNotExist, Proposal.DoesNotExist):
        raise Http404()


@login_required()
def contracts(request):
    qs_contracts = Contract.obs.with_feedback(request.user)
    if request.user.professional and request.session.get("is_professional"):
        qs_contracts = qs_contracts.filter(
            proposal__created_by=request.user.professional
        )
    elif request.user.client and request.session.get("is_client"):
        qs_contracts = qs_contracts.filter(job__created_by=request.user.client)
    context = {
        "contracts": qs_contracts,
        "title": "contracts list",
        "job_status_choices": Job.Status,
        "job_type_choices": Job.Type,
        "contract_status_choices": Contract.Status,
    }
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/jobs/contracts/list.html", context)


@login_required()
def contracts_close(request, cid: str):
    contract = get_object_or_404(Contract, pk=cid)
    if request.method == "POST":
        if contract.status == Contract.Status.CLOSED:
            messages.info(
                request,
                _(
                    "Contract is already closed by {}".format(
                        contract.closed_by.get_full_name()
                    )
                ),
            )
        data = request.POST
        contract = JobService.close_contract(contract, request.user, data)
        messages.info(request, _("Closed the Contract successfully!"))
        return HttpResponseRedirect(
            reverse("jobs:contracts-detail", args=(contract.id,))
        )


@login_required()
def contracts_detail(request, cid: str):
    try:
        contract = Contract.obs.with_feedback(request.user).get(pk=cid)
        context = {
            "title": "contract detail",
            "is_detail": "true",
            "contract": contract,
            "job_status_choices": Job.Status,
            "job_type_choices": Job.Type,
            "contract_status_choices": Contract.Status,
        }
        if request.user.professional and request.session["is_professional"]:
            template_prefix = "professional"
        elif request.user.client and request.session["is_client"]:
            template_prefix = "client"
        return render(request, f"{template_prefix}/jobs/contracts/detail.html", context)
    except Contract.DoesNotExist:
        raise Http404(_("Contract not found"))


@login_required()
def submit_work(request):
    if request.method == "POST":
        form = SubmitWorkForm(request.POST)
        if form.is_valid():
            contract_id = form.cleaned_data["contract_id"]
            contract = Contract.objects.select_related("proposal", "job").get(
                id=contract_id
            )
            contract = JobService.submit_work(contract, form.cleaned_data)
            messages.success(
                request, _("Work submitted! We notify the client to review the work.")
            )
        if form.errors:
            for k, err in form.errors.items():
                messages.error(request, err)
        return HttpResponseRedirect(
            reverse("jobs:contracts-detail", args=(contract.id,))
        )

    return HttpResponseNotAllowed(permitted_methods=("POST",))


@login_required()
def accept_work(request):
    if request.method == "POST":
        form = AcceptWorkForm(request.POST)
        if form.is_valid():
            contract_id = form.cleaned_data["contract_id"]
            contract = Contract.objects.select_related("proposal", "job").get(
                id=contract_id
            )
            contract = JobService.accept_work(contract)
            messages.success(request, _("Work accepted! We notify the professional."))
        if form.errors:
            for k, err in form.errors.items():
                messages.error(request, err)
        return HttpResponseRedirect(
            reverse("jobs:contracts-detail", args=(contract.id,))
        )

    return HttpResponseNotAllowed(permitted_methods=("POST",))


@login_required()
def accept_contract(request):
    if request.method == "POST":
        form = AcceptContractForm(request.POST)
        if form.is_valid():
            contract_id = form.cleaned_data["contract_id"]
            contract = Contract.objects.select_related("proposal", "job").get(
                id=contract_id
            )
            contract = JobService.accept_contract(contract)
            messages.success(
                request,
                _("You accepted the contract. Now you can work for the client."),
            )
            return HttpResponseRedirect(contract.job.get_absolute_url())
    return HttpResponseRedirect(reverse("jobs:contracts"))


@login_required()
def create_contract(request):
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            job = data.pop("job")
            contract = JobService.create_contract(job=job, validated_data=data)
            try:
                NotificationService.contract_created(contract)
            except Exception as e:
                logger.exception(f"Could not send notification: {e}")
            messages.success(request, _("Created contract successfully"))
            return HttpResponseRedirect(
                reverse("jobs:contracts-detail", args=(contract.id,))
            )

        for k, err in form.errors.items():
            messages.error(request, err)
        return HttpResponseRedirect(
            reverse(
                "jobs:proposal-detail",
                args=(request.POST["job"], request.POST["proposal"]),
            )
        )
    return HttpResponseNotAllowed(permitted_methods=("POST",))


@profile_complete_required
def job_list(request):
    context = {"is_list_page": True}
    page = request.GET.get("page")
    limit = request.GET.get("limit", 4)
    context.update({"AVAILABILITY_POINT": settings.AVAILABILITY_POINT})

    qs_jobs = Job.objects.select_related("created_by")
    template_prefix = "professional"

    if "query" in request.GET:
        form = JobSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            qs_jobs = JobService.search(qs_jobs, query)
            context.update(
                {
                    "query": query,
                }
            )

    if request.user.is_authenticated:
        if request.user.client and request.session.get("is_client"):
            qs_jobs = qs_jobs.filter(created_by=request.user.client)
            template_prefix = "client"

        if request.user.professional and request.session.get("is_professional"):
            # Subquery to check if professional has submitted a proposal for the job
            qs_sub_proposal = Proposal.objects.filter(
                job=OuterRef("pk"), created_by=request.user.professional
            )
            qs_flagged_job = FlaggedJob.objects.filter(
                job=OuterRef("pk"), reported_by=request.user
            )
            qs_saved_job = ProfessionalSavedJob.objects.filter(
                job=OuterRef("pk"), saved_by=request.user.professional
            )

            # Add subquery result as new field
            qs_jobs = qs_jobs.annotate(
                is_applied_before=Exists(qs_sub_proposal),
                is_flagged=Exists(qs_flagged_job),
                is_saved=Exists(qs_saved_job),
            )

            context.update(
                {
                    "is_platform_only": request.user.professional.visibility
                    == Professional.VisibilityChoices.PLATFORM_ONLY,
                    "is_public_only": request.user.professional.visibility
                    == Professional.VisibilityChoices.PUBLIC,
                    "is_private_only": request.user.professional.visibility
                    == Professional.VisibilityChoices.PRIVATE,
                    "saved_jobs": qs_jobs.filter(is_saved=True),
                }
            )

    paginated_jobs = paginate_objects(qs_jobs, page, per_page=limit)
    context.update({"title": "job list", "paginated_jobs": paginated_jobs})

    return render(request, f"{template_prefix}/jobs/list.html", context)


@login_required()
def send_proposal(request, idjob):
    job = get_object_or_404(Job, id=idjob)
    context = {
        "title": "send proposal",
        "job": job,
        "show_full_description": True,
        "COMMISSION": settings.COMMISSION,
        "job_type_choices": Job.Type,
    }

    if job.proposal_set.filter(created_by=request.user.professional).exists():
        messages.info(request, _("Already applied this job"))
        return HttpResponseRedirect(job.get_absolute_url())

    if request.method == "POST":
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = JobService.create_proposal(job, request.user, form.cleaned_data)
            messages.success(
                request,
                _("Congrats you sent the proposal! We notified the client."),
            )
            return HttpResponseRedirect(job.get_absolute_url())
    return render(request, "professional/jobs/proposals/create.html", context)


@login_required()
def job_detail(request, slug):
    # Subquery to check if professional has submitted a proposal for the job
    qs_sub_proposal = Proposal.objects.filter(
        job=OuterRef("pk"), created_by=request.user.professional
    )
    qs_flagged_job = FlaggedJob.objects.filter(
        job=OuterRef("pk"), reported_by=request.user
    )
    qs_saved_job = ProfessionalSavedJob.objects.filter(
        job=OuterRef("pk"), saved_by=request.user.professional
    )
    job = (
        Job.objects.filter(slug=slug)
        .annotate(
            is_applied_before=Exists(qs_sub_proposal),
            is_flagged=Exists(qs_flagged_job),
            is_saved=Exists(qs_saved_job),
        )
        .first()
    )
    if not job:
        raise Http404()

    context = {
        "title": "job detail",
        "is_proposal_listing": True,
        "job": job,
        "show_full_description": True,
        "job_status_choices": Job.Status,
        "contract_status_choices": Contract.Status,
    }
    proposal = job.proposal_set.filter(created_by=request.user.professional).first()
    if proposal:
        is_proposal_sent = True
        context.update({"is_proposal_sent": is_proposal_sent, "proposal": proposal})
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/jobs/detail.html", context)


@login_required()
def job_post(request):
    context = {
        "title": "job post",
    }
    if request.user.professional and request.session["is_professional"]:
        messages.info(
            request,
            _("You can create a client profile or switch if exists for posting a job."),
        )
        return HttpResponseRedirect(
            reverse("users:professionals-detail", args=(request.user.professional.id,))
        )
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                try:
                    newjob = form.save(commit=False)
                    newjob.created_by = request.user.client
                    newjob.save()
                    skills = request.POST.get("skills").split(",")
                    CoreService.create_skills(newjob, skills)
                    messages.success(request, _("Your job posted successfully"))
                    return HttpResponseRedirect(newjob.get_absolute_url())
                except Exception as e:
                    raise e

    return render(request, "client/jobs/post.html", context)


@login_required()
def create_feedback(request, cid: str):
    contract = get_object_or_404(Contract, pk=cid)
    if Feedback.objects.filter(contract=contract, created_by=request.user).exists():
        messages.warning(request, _("This user already submitted the feedback..."))
        return HttpResponseRedirect(
            reverse("jobs:contracts-detail", args=(contract.id,))
        )
    questions = FeedbackQuestion.objects.all()
    context = {"contract": contract, "questions": questions, "rating_choices": Rating}
    if request.method == "POST":
        data = [
            {"question_id": k.split("-")[1], "rating": v}
            for k, v in request.POST.items()
            if k.startswith("feedbackquestion")
        ]

        with transaction.atomic():
            feedback = Feedback(
                contract=contract,
                created_by=request.user,
                comment=request.POST.get("comment"),
            )
            for i in data:
                fresponse = FeedbackResponse.objects.create(
                    question_id=i["question_id"], rating=i["rating"]
                )
                feedback.save()
                feedback.responses.add(fresponse)
                feedback.save()
            messages.success(request, _("Submitted feedback successfully..."))
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(
        request, f"{template_prefix}/jobs/contracts/create-feedback.html", context
    )


@login_required()
def flag_job(request, idjob):
    job = get_object_or_404(Job, pk=idjob)
    if request.method == "POST":
        form = FlagJobForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            JobService.flag_job(job, request.user.professional, data)
            messages.info(request, _("Thanks for reporting this job"))
            return HttpResponseRedirect(reverse("jobs:list"))


@login_required()
def save_job(request, idjob):
    job = get_object_or_404(Job, pk=idjob)
    ProfessionalSavedJob.objects.create(job=job, saved_by=request.user.professional)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required()
def unsave_job(request, idjob):
    job = get_object_or_404(Job, pk=idjob)
    fsj = ProfessionalSavedJob.objects.get(job=job, saved_by=request.user.professional)
    fsj.delete()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
