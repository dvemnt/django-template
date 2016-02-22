# coding=utf-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^registration/$',
        views.RegistrationView.as_view(),
        name='registration'
    ),
    url(
        r'^authentication/$',
        views.AuthenticationView.as_view(),
        name='authentication'
    ),
    url(
        r'^verification/(?P<code>\w+)/$',
        views.VerificationView.as_view(),
        name='verification'
    ),
    url(
        r'^reverification/$',
        views.ReverificationView.as_view(),
        name='reverification'
    ),
    url(
        r'^password/restore$',
        views.RestorePasswordRequestView.as_view(),
        name='password.restore'
    ),
    url(
        r'^password/restore/(?P<code>\w+)/$',
        views.RestorePasswordChangeView.as_view(),
        name='password.restore.change'
    ),
]
