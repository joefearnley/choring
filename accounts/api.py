from rest_framework import generics, permissions, serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User(username=validated_data['username'], email=validated_data.get('email', ''))
        user.set_password(validated_data['password'])
        user.save()
        return user


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'username': user.username, 'email': user.email})
