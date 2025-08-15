from django.urls import path, include

from . import views

app_name = "address"

urlpatterns = [
    path("create/", views.address_create, name="create"),
    path("<str:aid>/update", views.address_update, name="update"),
    path("<str:aid>", views.address_detail, name="detail"),
   
    
]
