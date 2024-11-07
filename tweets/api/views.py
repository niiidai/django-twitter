from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetCreateSerializer,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from utils.decorators import required_params

class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin,):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

    @required_params(params=['user_id'])
    # GET request.query_params
    # POST request.data
    def list(self, request, *args, **kwargs):
        """
        This list method needs to include user_id to filter tweet contents.
        """
        # Equals to
        # select * from twitter_tweets
        # where user_id = xx
        # order by created_at DESC
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id'])\
            .prefetch_related('user')\
            .order_by('-created_at')
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,
        )
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
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )