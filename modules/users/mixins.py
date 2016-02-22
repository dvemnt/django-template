# coding=utf-8

from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy


class AnonymousOnlyViewMixin(object):

    """Redirect authenticated users to authenticated-only area."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse_lazy('$CHANGE'))

        return super(AnonymousOnlyViewMixin, self).dispatch(
            request, *args, **kwargs
        )


class AuthenticatedOnlyViewMixin(object):

    """Redirect anonymous users to authentication page."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse_lazy('users:authentication'))

        return super(AuthenticatedOnlyViewMixin, self).dispatch(
            request, *args, **kwargs
        )
