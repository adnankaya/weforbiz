from django.urls import path, include

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="list"),
    path("post", views.job_post, name="post"),
    path("contracts", views.contracts, name="contracts"),
    path("contracts/accept-contract", views.accept_contract, name="accept-contract"),
    path("contracts/<str:cid>/close", views.contracts_close, name="contracts-close"),
    path("contracts/<str:cid>", views.contracts_detail, name="contracts-detail"),
    path("contracts/<str:cid>/create-feedback", views.create_feedback, name="contracts-create-feedback"),
    path("proposals", views.proposals, name="proposals"),
    path("submit-work", views.submit_work, name="submit-work"),
    path("accept-work", views.accept_work, name="accept-work"),
    # this path should be latest
    path("<str:slug>", views.job_detail, name="detail"),
    path("<str:idjob>/flag", views.flag_job, name="flag-job"),
    path("<str:idjob>/save", views.save_job, name="save-job"),
    path("<str:idjob>/unsave", views.unsave_job, name="unsave-job"),
    path("<str:idjob>/proposals", views.job_proposals, name="job-proposals"),
    path("<str:idjob>/proposals/<str:proposal_id>", views.proposal_detail, name="proposal-detail"),
    path("create-contract/", views.create_contract, name="create-contract"),
    path("<str:idjob>/send-proposal", views.send_proposal, name="send-proposal"),
    
]
