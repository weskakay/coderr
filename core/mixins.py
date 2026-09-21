class ActionConfigMixin:
    """Picks permissions and serializer per action, filters the list only.

    A ViewSet sets action_permissions and action_serializers as dicts keyed
    by action name. Actions without an entry fall back to permission_classes
    and serializer_class. Filters and ordering apply to the list alone, so
    query parameters never hide a single object.
    """

    action_permissions = {}
    action_serializers = {}

    def get_permissions(self):
        """Return the permissions of the current action."""
        classes = self.action_permissions.get(
            self.action, self.permission_classes,
        )
        return [permission() for permission in classes]

    def get_serializer_class(self):
        """Return the serializer of the current action."""
        return self.action_serializers.get(self.action, self.serializer_class)

    def filter_queryset(self, queryset):
        """Apply filters, search and ordering to the list only."""
        if self.action != 'list':
            return queryset
        return super().filter_queryset(queryset)
