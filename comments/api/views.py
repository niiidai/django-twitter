from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from comments.api.permissions import IsObjectOwner


class CommentViewSet(viewsets.GenericViewSet):
    """
    This viewset provides `list`, `create`, `update` and `destroy` actions.
    It does not provide the `retrieve` action.
    """
    serializer_class = CommentCreateSerializer
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        if 'tweet_id' not in request.query_params:
            return Response({
                    'message': 'missing tweet_id in request',
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')
        #tweet_id = request.query_params['tweet_id']
        #comments = Comment.objects.filter(tweet_id=tweet_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

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

    def update(self, request, *args, **kwargs):
        # get_object() is a function of Django Rest Framework.
        # If the object is not found, DRF will automatically raise 404 error.
        comment = self.get_object()
        serializer = CommentUpdateSerializer(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # Here, save() will call the update method in serializer.
        # save() will call create or update depending on
        # whether the instance parameter is passed to serializer.
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    # DELETE
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # In DRF, the default return status of destroy is
        # status code = 204 no content.
        # Here, we return success=True for the front end user
        # and HTTP_200_OK is more appropriate.
        return Response({'success': True}, status=status.HTTP_200_OK)