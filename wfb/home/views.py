from django.shortcuts import render


from wfb.users.models import Professional


def index(request):
    best_professionals = Professional.objects.order_by("balance")[:6]
    context = {"title": "index page", "best_professionals": best_professionals}
    from time import sleep
    sleep(0.05)
    return render(request, "home/index.html", context)
