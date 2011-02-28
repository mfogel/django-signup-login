from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

from .decorators import login_required
from .generic_views import MultipleFormMixin, MultipleFormView
from .utils import redirect_to_security_check


class SignupMultipleFormMixin(MultipleFormMixin):
    form_class = UserCreationForm
    context_form_name = 'signup_form'
    success_url_name = 'accounts_dashboard'
    submit_url_name = 'accounts_signup'

    # see the form_valid logic in registration.views.register
    def form_valid(self, form):
        form.save()
        return super(SignupMultipleFormMixin, self).form_valid(form)


class LoginMultipleFormMixin(MultipleFormMixin):
    form_class = AuthenticationForm
    context_form_name = 'login_form'
    success_url_name = 'accounts_dashboard'
    submit_url_name = 'accounts_login'

    # see the form_valid logic in django.contrib.auth.views.login
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(LoginMultipleFormMixin, self).form_valid(form)


class SignupLoginView(MultipleFormView):
    multiple_form_mixin_classes = \
            (SignupMultipleFormMixin, LoginMultipleFormMixin)
    template_name = 'signup_login/signup_login.html'

    def __init__(self, *args, **kwargs):
        super(SignupLoginView, self).__init__(*args, **kwargs)


class LogoutView(RedirectView):
    permanent = False

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        redirect_to = self.request.GET.get(settings.REDIRECT_FIELD_NAME)
        if not redirect_to or \
                not redirect_to_security_check(redirect_to, self.request):
            redirect_to = settings.LOGOUT_REDIRECT_URL
        return redirect_to
