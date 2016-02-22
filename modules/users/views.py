# coding=utf-8

from django.shortcuts import redirect
from django.views.generic import FormView, RedirectView
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from . import forms, mixins, models


class RegistrationView(mixins.AnonymousOnlyViewMixin, FormView):

    """Registration."""

    form_class = forms.RegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:authentication')

    SUCCESSFUL_REGISTRATION = _('Registration is successful')

    def form_valid(self, form):
        """Action if form is valid."""
        form.save()
        messages.success(self.request, self.SUCCESSFUL_REGISTRATION)
        return super(RegistrationView, self).form_valid(form)


class VerificationView(RedirectView):

    """Verification."""

    permanent = True
    pattern_name = 'users:authentication'

    def dispatch(self, *args, **kwargs):
        """Dispatch request."""
        code = self.kwargs.get('code', None)
        try:
            verification = models.Verification.objects.active().get(code=code)
            verification.user.is_active = True
            verification.user.save()
            verification.delete()
        except models.Verification.DoesNotExist:
            pass
        return redirect(reverse_lazy(self.pattern_name))


class RestorePasswordRequestView(mixins.AnonymousOnlyViewMixin, FormView):

    """Restore password view."""

    template_name = 'users/restore_password.html'
    form_class = forms.RestorePasswordRequestForm
    success_url = reverse_lazy('users:authentication')

    SUCCESSFUL_RESTORE_REQUEST = _('Instructions sent to your email')

    def form_valid(self, form):
        """Action if form is valid."""
        form.save()
        messages.success(self.request, self.SUCCESSFUL_RESTORE_REQUEST)
        return super(RestorePasswordRequestView, self).form_valid(form)


class RestorePasswordChangeView(FormView):

    """Change password after restore."""

    template_name = 'users/restore_password.html'
    form_class = forms.RestorePasswordChangeForm
    success_url = reverse_lazy('users:authentication')

    PASSWORD_CHANGED = _('Password successful changed')

    def dispatch(self, *args, **kwargs):
        """Dispatch request."""
        code = self.kwargs.get('code', None)
        try:
            self.verification = models.Verification.objects.active().get(
                code=code
            )
        except models.Verification.DoesNotExist:
            return redirect(reverse_lazy('users:authentication'))
        return super(RestorePasswordChangeView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Action if form is valid."""
        form.user = self.verification.user
        form.save()
        self.verification.delete()
        messages.success(self.request, self.PASSWORD_CHANGED)
        return super(RestorePasswordChangeView, self).form_valid(form)


class PasswordChangeView(mixins.AuthenticatedOnlyViewMixin, FormView):

    """Change password."""

    template_name = 'users/change_password.html'
    form_class = forms.PasswordChangeForm

    PASSWORD_CHANGED = _('Password successful changed')

    def form_valid(self, form):
        """Action if form is valid."""
        form.user = self.verification.user
        form.save()
        messages.success(self.request, self.PASSWORD_CHANGED)
        return super(PasswordChangeView, self).form_valid(form)


class AuthenticationView(mixins.AnonymousOnlyViewMixin, FormView):

    """Authentication view."""

    form_class = forms.AuthenticationForm
    template_name = 'users/authentication.html'
    success_url = reverse_lazy('')

    USER_IS_INACTIVE = _('User is inactive')
    AUTHENTICATION_ERROR = (
        'User with such email is not registered or password is incorrect'
    )

    def form_valid(self, form):
        """Action if form is valid."""
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = auth.authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                auth.login(self.request, user)
            else:
                messages.error(self.request, self.USER_IS_INACTIVE)
                return super(AuthenticationView, self).form_invalid(form)
        else:
            messages.error(self.request, self.AUTHENTICATION_ERROR,)
            return super(AuthenticationView, self).form_invalid(form)

        return super(AuthenticationView, self).form_valid(form)


class ReverificationView(mixins.AnonymousOnlyViewMixin, FormView):

    """Reverification."""

    form_class = forms.ReverificationForm
    template_name = 'users/reverification.html'
    success_url = reverse_lazy('users:reverification')

    USER_IS_ACTIVE = _('User already active')
    SUCCESS_REVERIFICATION = _('Instructions sent to your email')

    def form_valid(self, form):
        """Action if form is valid."""
        form.save()
        messages.success(self.request, self.SUCCESS_REVERIFICATION)
        return super(ReverificationView, self).form_valid(form)
