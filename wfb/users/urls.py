from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view

from . import views

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),

    path("professionals/", views.professionals, name="professionals"),
    path("me/update/", views.update, name="update"),
    path("switch-profile/", views.switch_profile, name="switch-profile"),
    path("settings/points/", views.settings_points, name="settings-points"),
    path("settings/membership/", views.settings_membership, name="settings-membership"),
    path("settings/contact-info/", views.settings_contact_info, name="settings-contact-info"),
    path("settings/phone/", views.settings_phone, name="settings-phone"),
    path("settings/billing/", views.settings_billing, name="settings-billing"),
    path("settings/security/", views.settings_security, name="settings-security"),
    path("settings/get-paid/", views.settings_get_paid, name="settings-get-paid"),
    path("settings/notifications/", views.settings_notifications, name="settings-notifications"),
    path("settings/id-verification/", views.settings_id_verification, name="settings-id-verification"),
    path("profiles/create", views.profile_create, name="profile-create"),
    path("professionals/<str:fid>/visibility/", views.professional_visibility, name="professional-visibility"),
    path("professionals/<str:fid>/availability/", views.professional_availability, name="professional-availability"),
    path("professionals/<str:fid>/hoursperweek/", views.professional_hoursperweek, name="professional-hoursperweek"),
    path("professionals/<str:fid>/update-hourly-rate/", views.update_hourly_rate, name="update-hourly-rate"),
    path("professionals/<str:fid>/update-profile/", views.professionals_profile_update, name="professionals-update-profile"),
    path("professionals/<str:fid>/stats/", views.professional_stats, name="professional-stats"),
    path("professionals/<str:fid>", views.professionals_detail, name="professionals-detail"),
    path("clients/<str:cid>", views.clients_detail, name="clients-detail"),
]
