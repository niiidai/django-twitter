from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentCreateSerializer,
)

class CommentViewSet(viewsets.GenericViewSet):
    """
    This viewset provides `list`, `create`, `update` and `destroy` actions.
    It does not provide the `retrieve` action.
    """
    serializer_class = CommentCreateSerializer
    queryset = Comment.objects.all()

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # must include 'data=' as the first parameter is an instance
        serializer = CommentCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # .save() will call the create method in serializer
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

