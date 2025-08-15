from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

# internals
from wfb.users.models import Professional
from wfb.users.models import Client
from wfb.jobs.models import Job, Proposal

from .models import ChatRoom
from .utils import generate_room_name, decode_room_name


def index(request):
    current = None
    client_chat_rooms = None
    professional_chat_rooms = None
    if request.user.client and request.session.get("is_client"):
        current = request.user.client
        client_chat_rooms = current.client_chatrooms.all()
    if request.user.professional and request.session.get("is_professional"):
        current = request.user.professional
        professional_chat_rooms = current.professional_chatrooms.all()
    ctx = {
        "client_chat_rooms": client_chat_rooms,
        "professional_chat_rooms": professional_chat_rooms,
        "current": current,
    }

    return render(request, "chats/index.html", ctx)


def start_chat(request):
    if request.method == "POST":
        proposal = Proposal.objects.select_related(
            "job",
            "job__created_by",
            "job__created_by__user",
            "created_by",
            "created_by__user",
        ).get(id=request.POST.get("proposal_id"))

        room_name = generate_room_name(proposal.job.id.hex, proposal.id.hex)
        chatroom, created = ChatRoom.objects.get_or_create(
            job=proposal.job,
            room_name=room_name,
            client=proposal.job.created_by,
            professional=proposal.created_by,
        )
        return HttpResponseRedirect(
            reverse("chats:room", kwargs={"room_name": chatroom.room_name})
        )


def room(request, room_name):
    jobid, proposalid = decode_room_name(room_name)
    job = Job.objects.get(id=jobid)
    proposal = job.proposal_set.get(id=proposalid)

    chat_room = ChatRoom.objects.get(room_name=room_name)
    ctx = {
        "room_name": room_name,
        "client": job.created_by,
        "professional": proposal.created_by,
        "job": job,
        "chat_room": chat_room,
    }
    return render(request, "chats/room.html", ctx)
