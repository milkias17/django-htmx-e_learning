from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class GroupRequiredMixin(AccessMixin):
    group_required = None

    def get_group_required(self):
        """
        Override this method to override the group_required attribute.
        Must return an iterable.
        """
        if self.group_required is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the "
                f"group_required attribute. Define "
                f"{self.__class__.__name__}.group_required, or override "
                f"{self.__class__.__name__}.get_group_required()."
            )

        if isinstance(self.group_required, str):
            groups = (self.group_required,)
        else:
            groups = self.group_required

        return groups

    def has_group(self):
        groups = self.get_group_required()
        user_groups = self.request.user.groups.values_list("name", flat=True)
        return all(group in user_groups for group in groups)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_group():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


def group_required(group, login_url=None, raise_exception=False):
    def check_groups(user):
        if isinstance(group, str):
            groups = (group,)
        else:
            groups = group

        user_groups = user.groups.values_list("name", flat=True)
        if all(group in user_groups for group in groups):
            return True

        if raise_exception:
            raise PermissionDenied

        return False

    return user_passes_test(check_groups, login_url=login_url)
