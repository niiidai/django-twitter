from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    # if we don't add user = UserSerializer() here,
    # the 'user' in fields will be shown as user_id.
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'updated_at',
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    # need to add tweet_id and user_id manually
    # as restframework ModelSerializer only includes user and tweet
    # rather than user_id and tweet_id.

    # User is a name of Model; user is an instance of User;
    # user_id is the pk of User.
    # users => list of users or queryset of User
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'Tweet does not exist'})
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )