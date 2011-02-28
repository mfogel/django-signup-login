from django.conf.urls.defaults import *

from .views import *


urlpatterns = patterns('',
    url(r'^signup/$',
        view=SignupLoginView.as_view(
            featured_form_mixin_class=SignupMultipleFormMixin),
        name='accounts_signup'
    ),
    url(r'^login/$',
        view=SignupLoginView.as_view(
            featured_form_mixin_class=LoginMultipleFormMixin),
        name='accounts_login'
    ),
    url(r'^signup-login/$',
        view=SignupLoginView.as_view(),
        name='accounts_signup_login'
    ),

    url(r'^logout/$',
        view=LogoutView.as_view(),
        name='accounts_logout'
    ),
)
