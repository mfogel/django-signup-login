import copy

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin

from .utils import redirect_to_security_check


class MultipleFormMixin(FormMixin):
    """
    For each form you want to use in the MultipleFormView, define a
    MultipleFormMixin where you define:
      - form_class
      - submit_url_name
      - success_url_name
      - context_form_name (optional)
      - initial (optional)

    """
    context_form_name = None

    def get_success_url(self):
        """
        Where to send the user after successfully submitting this form.

        Security checks on the redirect_field_name GET param taken from
        django.contrib.auth.login

        """
        redirect_to = self.request.GET.get(settings.REDIRECT_FIELD_NAME)
        if not redirect_to or \
                not redirect_to_security_check(redirect_to, self.request):
            redirect_to = reverse(self.success_url_name)
        return redirect_to

    def get_submit_url(self):
        url = reverse(self.submit_url_name)
        if self.request.GET:
            url += '?' + self.request.GET.urlencode()
        return url

    def get_form_class(self):
        form_class = super(MultipleFormMixin, self).get_form_class()
        form_class.__unicode__ = lambda inst: unicode(inst.__name__)
        form_class.is_featured = False
        form_class.action = self.get_submit_url()
        return form_class

    def get_context_form_name(self):
        if self.context_form_name:
            return self.context_form_name
        return unicode(self.form_class)

    def form_invalid(self, form):
        raise ImproperlyConfigured("Don't call me - handle this case at a higher level.  What should be done here depends on my peers as well.")


class MultipleFormView(TemplateView):
    """
    Define multiple_form_mixin_classes as an iterable of MultipleFormMixin
    classes you've defined, overriding class vars as necessary.

    """
    multiple_form_mixin_classes = []
    featured_form_mixin_class = None

    def __init__(self, featured_form_mixin_class=None, *args, **kwargs):
        super(MultipleFormView, self).__init__(*args, **kwargs)
        self.featured_form_mixin_class = featured_form_mixin_class
        self.multiple_form_mixins = []
        for mfmc in self.multiple_form_mixin_classes:
            self.multiple_form_mixins.append(mfmc())

    def get_context_data(self, **kwargs):
        context = super(MultipleFormView, self).get_context_data(**kwargs)
        for mfm in self.multiple_form_mixins:
            form = mfm.get_form(mfm.get_form_class())
            if self.featured_form_mixin_class and \
                    isinstance(mfm, self.featured_form_mixin_class):
                form.is_featured = True
            context.update({mfm.get_context_form_name(): form})
        return context

    def get(self, request, *args, **kwargs):
        for mfm in self.multiple_form_mixins:
            mfm.request = self.request
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not self.featured_form_mixin_class:
            raise ValidationError("Form submission to wrong URL detected.  No featured form mixin defined.")

        # featured form mixin gets the real request, the rest get a dummy GET
        dummy_request = copy.copy(self.request)
        dummy_request.POST = self.request.POST.copy().clear()
        dummy_request.method = 'GET'
        for mfm in self.multiple_form_mixins:
            if isinstance(mfm, self.featured_form_mixin_class):
                mfm.request = request
                form = mfm.get_form(mfm.get_form_class())
                if form.is_valid():
                    return mfm.form_valid(form)
            else:
                mfm.request = dummy_request

        # re-render the view with all the others as normal
        # none of the blank forms get the real POST data
        return self.render_to_response(self.get_context_data())

