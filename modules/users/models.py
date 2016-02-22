# coding=utf-8

from django.utils import timezone, crypto
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _

from . import tasks


class UserManager(BaseUserManager):

    """User database manager."""

    def create_user(self, email, password, **kwargs):
        """Create user."""
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **kwargs):
        """Create superuser."""
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        kwargs['is_active'] = True
        return self.create_user(**kwargs)


class User(AbstractBaseUser):

    """User database model."""

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(_('Name'), max_length=35)
    surname = models.CharField(_('Surname'), max_length=35)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def __unicode__(self):
        """Unicode representation."""
        return u'{}'.format(self.email)

    def get_short_name(self):
        """Get short name."""
        return u'{}'.format(self.name)

    def get_full_name(self):
        """Get full name."""
        return u'{0.name} {0.surname}'.format(self)

    def has_module_perms(self, *args, **kwargs):
        """Has moduel permissions."""
        return self.is_staff

    def has_perm(self, *args, **kwargs):
        """Has permission."""
        return self.is_staff


class VerificationManager(models.Manager):

    """Verification database manager."""

    def active(self):
        """Get active verifications."""
        return self.get_queryset().filter(expired__gt=timezone.now())


class Verification(models.Model):

    """Verification database model."""

    CODE_LENGTH = 32

    user = models.ForeignKey(User, related_name='verifications')
    code = models.CharField(max_length=CODE_LENGTH)
    expired = models.DateTimeField()

    objects = VerificationManager()

    def save(self, *args, **kwargs):
        """Save to database."""
        self.code = crypto.get_random_string(length=32)
        self.expired = timezone.now() + timezone.timedelta(hours=24)
        return super(Verification, self).save(*args, **kwargs)
