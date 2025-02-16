from accounts.api.serializers import (
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializerForUpdate,
    UserSerializer,
    UserSerializerWithProfile,
)
from accounts.models import UserProfile
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAdminUser,)


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        Default username is admin; default password is admin
        """
        #get username and password from request
        serializer = LoginSerializer(data=request.data)
        # in case of missing username or password fields in LoginSerializer
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                # the missing field won't be stored as a key in "error" dict
                "errors": serializer.errors,
            }, status=400)

        # username case insensitive
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        # in case username does not exit
        if not User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': "Please check input.",
                "errors": {
                    "username": [
                        "User does not exist."
                    ]
                }
            }, status=400)

        # in case of wrong username or password
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        #success
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        logout current user
        """
        django_logout(request)
        return Response({"success": True})

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        register with username, email, and password
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        check the login status of the current user
        """
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)


# Viewset for user_profile; PUT /api/profiles/<id>/
class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (permissions.IsAuthenticated, IsObjectOwner, )
    serializer_class = UserProfileSerializerForUpdate
