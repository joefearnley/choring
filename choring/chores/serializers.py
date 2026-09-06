from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Chore


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ChoreSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField()

    class Meta:
        model = Chore
        fields = ('id', 'title', 'description', 'assigned_to', 'start_date', 'due_date', 'recurrence', 'active')