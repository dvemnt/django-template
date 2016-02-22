# coding=utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model

from . import models, tasks


class RegistrationForm(forms.ModelForm):

    """Registration form."""

    EMAIL_ALREADY_USED = _('Such email already used')
    PASSWORDS_MUST_MATCH = _('Passwords must match')

    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'surname')

    def clean_email(self):
        """Clean email."""
        email = self.cleaned_data['email']

        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(self.EMAIL_ALREADY_USED)

        return email

    def clean_confirm_password(self):
        """Clean passwords."""
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError(self.PASSWORDS_MUST_MATCH)

        return password

    def save(self, *args, **kwargs):
        """Save form."""
        del self.cleaned_data['confirm_password']
        user = get_user_model().objects.create_user(**self.cleaned_data)
        verification = models.Verification.objects.create(user=user)
        tasks.send_verification_email(verification)
        return user


class AuthenticationForm(forms.Form):

    """Authentication form."""

    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)


class RestorePasswordRequestForm(forms.Form):

    """Form for create request to restore password."""

    email = forms.EmailField()

    def save(self, *args, **kwargs):
        """Save form."""
        user = get_user_model().objects.get(email=self.cleaned_data['email'])
        verification = models.Verification.objects.create(user=user)
        tasks.send_restore_password_email(verification)

class RestorePasswordChangeForm(forms.Form):

    """Form for change password after restore."""

    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput
    )

    def clean_confirm_password(self):
        """Clean passwords."""
        form = RegistrationForm()
        form.cleaned_data = self.cleaned_data
        return form.clean_confirm_password()

    def save(self, *args, **kwargs):
        """Save form."""
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()


class PasswordChangeForm(RestorePasswordChangeForm):

    """Form for change password."""

    PASSWORD_INCORRECT = _('Password incorrect.')

    current_password = forms.CharField(
        label=_('Current password'), widget=forms.PasswordInput
    )

    def clean_current_password(self):
        """Clean current password."""
        current_password = self.cleaned_data['current_password']

        if not self.user.check_password(current_password):
            raise forms.ValidationError(self.PASSWORD_INCORRECT)


class UserAdminCreationForm(forms.ModelForm):

    """A form for creating new users."""

    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label=_('Password confirmation'), widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'surname')

    def clean_confirm_password(self):
        """Clean passwords."""
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError(self.PASSWORDS_MUST_MATCH)

        return password

    def save(self, *args, **kwargs):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        return super(UserAdminCreationForm, self).save(*args, **kwargs)


class UserAdminChangeForm(forms.ModelForm):

    """A form for updating users."""

    password = ReadOnlyPasswordHashField(
        label=_('Password'), help_text=_('<a href="../password/">Change</a>')
    )

    class Meta:
        model = get_user_model()
        exclude = tuple()

    def clean_password(self):
        """Clean password."""
        return self.initial['password']


class ReverificationForm(forms.Form):

    """For for resend verification email."""

    email = forms.EmailField(label=_('Email'))

    def save(self, *args, **kwargs):
        """Save form."""
        user = get_user_model().objects.get(email=self.cleaned_data['email'])
        verification = models.Verification.objects.create(user=user)
        tasks.send_verification_email(verification)
