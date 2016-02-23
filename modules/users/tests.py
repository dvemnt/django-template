# coding=utf-8

from django import test
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from . import models

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'


class CompositeDocstringTestCase(test.TestCase):

    """Test case with composite docstring."""

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Override create class."""
        cls = super(CompositeDocstringTestCase, cls).__new__(*args, **kwargs)
        tests = [attr for attr in dir(cls) if attr.startswith('test_')]
        for test_name in tests:
            test_method = getattr(cls, test_name)
            if cls.__doc__ not in test_method.__doc__:
                test_method.__func__.__doc__ = '{}: {}'.format(
                    cls.__doc__, test_method.__func__.__doc__
                )
        return cls

@test.override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class RegistrationTest(CompositeDocstringTestCase):

    """Test registration"""

    url = reverse('users:registration')
    client = test.Client()

    def test_without_unique_email(self):
        """Without unique email."""
        payload = {
            'email': 'test@mail.com', 'name': 'Test', 'surname': 'Test',
            'password': 'pass'
        }
        get_user_model().objects.create_user(**payload)
        payload['confirm_password'] = payload['password']

        self.client.post(self.url, data=payload)

        self.assertEqual(get_user_model().objects.all().count(), 1)

    def test_success(self):
        """Success."""
        payload = {
            'email': 'test@mail.com', 'name': 'Test', 'surname': 'Test',
            'password': 'pass', 'confirm_password': 'pass'
        }

        self.client.post(self.url, data=payload)
        user = get_user_model().objects.get(email=payload['email'])

        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class VerificationTest(CompositeDocstringTestCase):

    """Test verification"""

    client = test.Client()

    def test_with_wrong_code(self):
        """With wrong code."""
        user = get_user_model().objects.create_user(
            email='test@mail.com', password='pass', name='Name', surname='Test'
        )
        models.Verification.objects.create(user=user)
        url = reverse('users:verification', kwargs={'code': 'wrong'})

        self.client.get(url)
        user.refresh_from_db()

        self.assertFalse(user.is_active)

    def test_success(self):
        """Success."""
        user = get_user_model().objects.create_user(
            email='test@mail.com', password='pass', name='Name', surname='Test'
        )
        code = models.Verification.objects.create(user=user).code
        url = reverse('users:verification', kwargs={'code': code})

        self.client.get(url)
        user.refresh_from_db()

        self.assertTrue(user.is_active)


@test.override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class ReverificationTest(CompositeDocstringTestCase):

    """Test reverification"""

    url = reverse('users:reverification')
    client = test.Client()

    def test_success(self):
        """Success."""
        user = get_user_model().objects.create_user(
            email='test@mail.com', password='pass', name='Name', surname='Test'
        )

        self.client.post(self.url, data={'email': user.email})

        self.assertTrue(models.Verification.objects.filter(user=user).exists())


@test.override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
class RestorePasswordRequestTest(CompositeDocstringTestCase):

    """Test create request to restore password"""

    url = reverse('users:password.restore')
    client = test.Client()

    def test_success(self):
        """Success."""
        user = get_user_model().objects.create_user(
            email='test@mail.com', password='pass', name='Name', surname='Test'
        )

        self.client.post(self.url, data={'email': user.email})

        self.assertTrue(models.Verification.objects.filter(user=user).exists())


class RestorePasswordChangeTest(CompositeDocstringTestCase):

    """Test change password after restore"""

    client = test.Client()

    def test_success(self):
        """Success."""
        user = get_user_model().objects.create_user(
            email='test@mail.com', password='pass', name='Name', surname='Test'
        )
        code = models.Verification.objects.create(user=user).code
        url = reverse('users:password.restore.change', kwargs={'code': code})
        payload = {'password': 'pass', 'confirm_password': 'pass'}

        self.client.post(url, data=payload)
        user.refresh_from_db()

        self.assertTrue(user.check_password(payload['password']))
