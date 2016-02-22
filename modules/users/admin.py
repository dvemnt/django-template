# coding=utf-8

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models, forms


class UserAdmin(BaseUserAdmin):

    """User model admin interface."""

    form = forms.UserAdminChangeForm
    add_form = forms.UserAdminCreationForm

    list_display = ('email', 'name', 'surname')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'phone', 'surname', 'specialty')
    ordering = ('email',)
    filter_horizontal = tuple()

    fieldsets = (
        (_('Personal information'), {
            'fields': ('email', 'name', 'surname')
        }),
        (_('Permissions'), {
            'fields': ('is_superuser', 'is_active', 'is_staff')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'password', 'confirm_password'
            )
        }),
    )

    def has_module_permission(self, request):
        """Has module permission."""
        return request.user.is_superuser

admin.site.register(models.User, UserAdmin)
