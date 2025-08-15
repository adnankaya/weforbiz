from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


from .models import Feedback


def feedbacks(request):
    feedbacks = Feedback.objects.select_related(
        "contract",
        "contract__job",
        "contract__job__created_by",
        "contract__proposal",
        "contract__proposal__created_by",
    )
    context = {"title": "Feedback List", "feedbacks": feedbacks}
    if request.method == "POST":
        
        pass

    return render(request, "feedbacks/index.html", context)
