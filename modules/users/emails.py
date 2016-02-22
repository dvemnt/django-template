# coding=utf-8

from django.conf import settings

VERIFICATION = {
    'subject': 'Confirm your registration on {}'.format(settings.HOST),
    'template': 'users/email/verification.html'
}

RESTORE_PASSWORD = {
    'subject': 'Restore password on {}'.format(settings.HOST),
    'template': 'users/email/restore_password.html'
}
