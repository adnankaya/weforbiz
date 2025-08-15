from django.urls import path, include

from . import views

app_name = "feedbacks"

urlpatterns = [
    path("", views.feedbacks, name="list"),
   
    
]
