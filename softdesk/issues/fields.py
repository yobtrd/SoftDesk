from rest_framework.serializers import Field


class ProjectNameField(Field):
    def to_internal_value(self, name):
        return name

    def to_representation(self, project):
        return project.name


class UsernameField(Field):
    def to_internal_value(self, username):
        return username

    def to_representation(self, user):
        return user.username


class AssignmentUsernameField(Field):
    def to_internal_value(self, username):
        return username

    def to_representation(self, value):
        return value.user.username
