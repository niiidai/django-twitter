from django.contrib.auth.models import User
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipCreateSerializer
)
from friendships.models import Friendship
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.paginations import FriendshipPagination

class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipCreateSerializer
    queryset = User.objects.all()
    # Different views may need different pagination settings.
    pagination_class = FriendshipPagination

    # We would like to use POST /api/friendships/1/follow
    # to follow the user with user_id = 1.
    # detail = True will call get_object() first to check
    # if the queryset.filter(pk=x) object exists.
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # repeat follow will be silenced
        # check if user with id=pk exists
        self.get_object()

        # /api/friendships/<pk>/follow/
        serializer = FriendshipCreateSerializer(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # raise 404 if no user with id=pk
        # here "pk" has a string type
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself!',
            }, status=status.HTTP_400_BAD_REQUEST)

        # delete() will return two values: 1. how much data was deleted;
        # 2. how much was deleted for each type of data
        # Do not use on_delete=models.SET.CASCADE in models.py
        # as all the related data will also be deleted.
        # Use on_deleted=models.SET_NULL instead.
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message': 'this is friendships homepage.'})