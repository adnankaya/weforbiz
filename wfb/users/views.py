from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from wfb.address.models import City, Country
from wfb.core.services import CoreService
from wfb.core.pagination import paginate_objects
from wfb.users.services import ProfessionalService
from wfb.users.models import User, Professional, Client, Profile
from wfb.users.forms import UserUpdateForm, PhoneForm, ProfessionalForm, ClientForm, ProfileForm
from wfb.core.forms import SearchForm


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None=None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("jobs:list")


user_redirect_view = UserRedirectView.as_view()




@login_required()
def settings_points(request):
    context = {"title": "points page", "is_settings_page": True}
    return render(request, "professional/settings/points.html", context)


@login_required()
def settings_membership(request):
    context = {"title": "membership", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/membership.html", context)


@login_required()
def settings_billing(request):
    context = {"title": "billing", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/billing.html", context)


@login_required()
def settings_contact_info(request):
    countries = Country.objects.all()
    cities = City.objects.all()
    context = {
        "title": "Contract Info",
        "countries": countries,
        "cities": cities,
        "is_settings_page": True,
    }
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/contact-info.html", context)


@login_required()
def settings_security(request):
    context = {"title": "security", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/security.html", context)


@login_required()
def settings_get_paid(request):
    context = {"title": "get paid", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/get-paid/index.html", context)


@login_required()
def settings_notifications(request):
    context = {"title": "notifications", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/notifications.html", context)


@login_required()
def settings_id_verification(request):
    context = {"title": "identity verification", "is_settings_page": True}
    if request.user.professional and request.session["is_professional"]:
        template_prefix = "professional"
    elif request.user.client and request.session["is_client"]:
        template_prefix = "client"
    return render(request, f"{template_prefix}/settings/id-verification.html", context)


@login_required()
def update_hourly_rate(request, fid):
    professional = get_object_or_404(Professional, id=fid)
    if request.method == "POST":
        professional.hourly_rate = request.POST.get("hourly_rate", professional.hourly_rate)
        professional.save()
        messages.info(request, _("Updated hourly rate!"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def update(request):
    """
    Authenticated user info update
    """
    ctx = {}
    current_email = request.user.email
    current_site = get_current_site(request)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        with transaction.atomic():
            if form.is_valid():
                ufcd = form.cleaned_data
                user_ob = form.save(commit=False)
                if ufcd["email"] and ufcd["email"] != current_email:
                    messages.info(
                        request,
                        _(
                            "Your email is changed. We sent verification email to your new email address"
                        ),
                    )
                    # UserService.send_email_verification(request.user, current_site)
                    user_ob.email_verified = False
                user_ob.save()
                messages.success(request, _("Successfully updated!"))
                return HttpResponseRedirect(reverse("users:settings-contact-info"))
            messages.error(request, form.errors)
            return HttpResponseRedirect(reverse("users:settings-contact-info"))


@login_required
def settings_phone(request):
    professional = request.user.professional
    client = request.user.client
    if request.method == "POST":
        form = PhoneForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                phone = form.cleaned_data["phone"]
                if professional and request.session["is_professional"]:
                    professional.phone = phone
                    professional.save()
                elif client and request.session["is_client"]:
                    client.phone = phone
                    client.save()
            messages.success(request, _("Updated phone successfully."))
            return HttpResponseRedirect(reverse("users:settings-contact-info"))
        messages.error(request, form.errors)
        return HttpResponseRedirect(reverse("users:settings-contact-info"))




def professionals(request):
    Q_available = Q(is_available=True)
    Q_visibility = Q(visibility__in=[Professional.VisibilityChoices.PUBLIC])
    if request.user.is_authenticated:
        Q_visibility = Q(
            visibility__in=[
                Professional.VisibilityChoices.PUBLIC,
                Professional.VisibilityChoices.PLATFORM_ONLY,
            ]
        )

    qs = Professional.objects.filter(Q_visibility & Q_available)
    context = {"is_list_page": True}
    page = request.GET.get("page")
    limit = request.GET.get("limit", 12)

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            qs = ProfessionalService.search(qs, query)
            context.update(
                {
                    "query": query,
                }
            )

    paginated_professionals = paginate_objects(qs, page, per_page=limit)
    context.update(
        {"title": "Browse Professionals", "paginated_professionals": paginated_professionals}
    )

    return render(request, "professional/browse-professionals.html", context)


@login_required()
def profile_create(request):
    context = {
        "title": "profile create",
    }
    user = request.user
    if user.client:
        if request.method == "POST":
            form = ProfessionalForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    professional = form.save(commit=False)
                    professional.user = user
                    professional.profile_type = Profile.Types.FREELANCER
                    professional.save()
                    skills = request.POST.get("skills").split(",")
                    CoreService.create_skills(professional, skills)
                    messages.success(
                        request, _("Created professional profile successfully!")
                    )
                    return HttpResponseRedirect(
                        reverse("users:professionals-detail", args=(professional.id,))
                    )
            for k, err in form.errors.items():
                messages.error(request, err)
        return render(request, "users/professionals/create.html", context)

    if user.professional:
        if request.method == "POST":
            form = ClientForm(request.POST)
            if form.is_valid():
                client = form.save(commit=False)
                client.user = user
                client.profile_type = Profile.Types.CLIENT
                client.save()
                messages.success(request, _("Created client profile successfully!"))
                return HttpResponseRedirect(
                    reverse("users:clients-detail", args=(client.id,))
                )
        return render(request, "users/clients/create.html", context)

    # if user signed up and has no profile
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile_type = form.cleaned_data["profile_type"]
            if profile_type == Profile.Types.FREELANCER:
                professional = Professional.objects.create(
                    user=user, profile_type=profile_type
                )
                messages.success(request, _("Created professional profile successfully!"))
                request.session["is_professional"] = True
                request.session["is_client"] = False
                return HttpResponseRedirect(
                    reverse("users:professionals-detail", args=(professional.id,))
                )
            if profile_type == Profile.Types.CLIENT:
                client = Client.objects.create(user=user, profile_type=profile_type)
                messages.success(request, _("Created client profile successfully!"))
                request.session["is_client"] = True
                request.session["is_professional"] = False
                return HttpResponseRedirect(
                    reverse("users:clients-detail", args=(client.id,))
                )
    context.update({"profile_type_choices": Profile.Types})
    return render(request, "users/profile-create.html", context)


@login_required()
def switch_profile(request):
    """
    when the user signs in we need to redirect professional or client profile and set is_professional or is_client
    then we can allow swtich operation
    """

    if request.session["is_professional"]:
        professional = request.user.professional
        return HttpResponseRedirect(
            reverse("users:professionals-detail", args=(professional.id,))
        )
    elif request.session["is_client"]:
        client = request.user.client
        return HttpResponseRedirect(reverse("users:clients-detail", args=(client.id,)))

    else:
        return Http404("This page not exist")


@login_required()
def professional_visibility(request, fid: str):
    professional = get_object_or_404(Professional, id=fid)
    if request.method == "POST":
        professional.visibility = request.POST.get("visibility", "PUBLIC")
        professional.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required()
def professional_availability(request, fid: str):
    professional = get_object_or_404(Professional, id=fid)
    if request.method == "POST":
        professional.is_available = bool(request.POST.get("availability", False))
        if professional.is_available:
            messages.success(request, _("Opened availability!"))
        else:
            messages.info(request, _("Closed availability."))

        professional.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required()
def professional_hoursperweek(request, fid: str):
    professional = get_object_or_404(Professional, id=fid)
    if request.method == "POST":
        professional.hoursperweek = request.POST.get(
            "hoursperweek", professional.hoursperweek
        )
        professional.save()
        messages.success(request, _("Updated hours per week!"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required()
def professional_stats(request, fid: str):
    professional = get_object_or_404(Professional, id=fid)
    context = {
        "title": "Professional Stats",
        "professional": professional,
    }
    return render(request, "users/professionals/stats.html", context)


@login_required()
def professionals_detail(request, fid: str):
    professional = get_object_or_404(Professional, id=fid)
    previous_contracts = professional.get_previous_contracts()

    is_owner = False

    if request.user.professional == professional:
        is_owner = True

    context = {
        "title": "Professional Detail",
        "professional": professional,
        "badges_choices": Professional.Badges,
        "previous_contracts": previous_contracts,  # TODO use in template professional.get_previous_contracts
        "is_owner": is_owner,
    }
    return render(request, "users/professionals/detail.html", context)


@login_required()
def professionals_profile_update(request, fid: str):
    professional = Professional.objects.get(pk=fid)
    if request.method == "POST":
        with transaction.atomic():
            professional.title = request.POST.get("title", professional.title)
            professional.bio = request.POST.get("bio", professional.bio)
            professional.save()
            skills = request.POST.get("skills").split(",")
            if skills and professional.skills.exists():
                professional.skills.clear()
            CoreService.create_skills(professional, skills)
            messages.success(request, _("Updated profile"))
            return HttpResponseRedirect(
                reverse("users:professionals-detail", args=(fid,))
            )


@login_required()
def clients_detail(request, cid: str):
    client = get_object_or_404(Client, id=cid)
    is_owner = False

    if request.user.client == client:
        is_owner = True

    context = {
        "title": "Client Detail",
        "client": client,
        "is_owner": is_owner,
    }
    return render(request, "users/clients/detail.html", context)

