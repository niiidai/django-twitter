from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet

class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin,):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        This list method needs to include user_id to filter tweet contents.
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # equals to
        # select * from twitter_tweets
        # where user_id = xx
        # order by created_at DESC
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # return response in JSON format (hash format)
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        This create method needs current user as tweet.user
        """
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)

        # serializer.save() will call create method in TweetCreateSerializer
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)