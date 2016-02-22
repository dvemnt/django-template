# coding=utf-8

from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string

from . import emails


def send_email(email, subject, message):
    """Send email."""
    send_mail(
        subject=subject, message=message, html_message=message,
        recipient_list=[email], from_email=settings.DEFAULT_FROM_EMAIL
    )


def send_verification_email(verification):
    """Send verification email."""
    url = '{}{}'.format(
        settings.HOST,
        reverse_lazy('users:verification', kwargs={'code': verification.code})
    )
    message = render_to_string(
        emails.VERIFICATION['template'], {'verification_url': url}
    )
    send_email(
        subject=emails.VERIFICATION['subject'], message=message,
        email=verification.user.email
    )


def send_restore_password_email(verification):
    """Send email with instructions for restore password."""
    url = '{}{}'.format(
        settings.HOST,
        reverse_lazy(
            'users:password.restore.change',
            kwargs={'code': verification.code}
        )
    )
    message = render_to_string(
        emails.RESTORE_PASSWORD['template'], {'verification_url': url}
    )
    send_email(
        subject=emails.RESTORE_PASSWORD['subject'], message=message,
        email=verification.user.email
    )
