from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


# You can add extra fields to a ModelSerializer
# or override the default fields by declaring fields on the class,
# just as you would for a Serializer class by using source=xx.
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.from_user)


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.to_user)


class FriendshipCreateSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself!',
            })

        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user!',
            })

        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow a non-existent user.',
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )