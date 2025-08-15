from django.urls import reverse


class CoreMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        if request.path == reverse("users:switch-profile"):
            if (
                "is_professional" in request.session
                and request.session["is_professional"]
            ):
                request.session["is_client"] = True
                request.session["is_professional"] = False
            elif "is_client" in request.session and request.session["is_client"]:
                request.session["is_client"] = False
                request.session["is_professional"] = True
            else:
                pass
        response = self.get_response(request)
        # Code to be executed for each request/response after the view is called.
        # When user logs in after successfull authentication we set profile type in session
        if request.path == reverse("account_login") and request.user.is_authenticated:
            if request.user.professional:
                request.session["is_professional"] = True
                request.session["is_client"] = False
            elif request.user.client:
                request.session["is_client"] = True
                request.session["is_professional"] = False
            else:
                pass

        return response
