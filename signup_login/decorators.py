from django.conf import settings
from django.contrib.auth.decorators import \
        login_required as auth_login_required

def login_required(*args, **kwargs):
    """
    Require login in order to display given view.

    Use instead of django.contrib.auth.decorators.login_required in order
    to use settings.REDIRECT_FIELD_NAME.

    Example usage:

    class SomeView(View):
        @method_decorator(login_required)
        def get(self, request, *args, **kwargs):
            return SomethingForLoggedInEyesOnly()

    """
    kwargs.update({
        'redirect_field_name': settings.REDIRECT_FIELD_NAME,
    })
    return auth_login_required(*args, **kwargs)
