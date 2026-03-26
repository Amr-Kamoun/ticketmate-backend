from rest_framework import serializers

from users.models import UserRole
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "client",
            "project_type",
            "project_owner",
            "team_members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_project_owner(self, value):
        if value.role != UserRole.PROJECT_OWNER:
            raise serializers.ValidationError("Project owner must have PROJECT_OWNER role.")
        return value

    def validate_team_members(self, value):
        invalid_users = [user.username for user in value if user.role != UserRole.EMPLOYEE]
        if invalid_users:
            raise serializers.ValidationError(
                f"All team members must have EMPLOYEE role. Invalid users: {', '.join(invalid_users)}"
            )
        return value


class AssignProjectMembersSerializer(serializers.Serializer):
    team_members = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )
