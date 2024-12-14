from django.contrib.auth.models import User
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #fields = ('id', 'username', 'email')
        fields = ('username', 'email')

class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForLike(UserSerializerForTweet):
    pass


class UserSerializerForComment(UserSerializerForTweet):
    pass


class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        validated_data = dict(data)
        validated_data['username'] = validated_data['username'].lower()
        validated_data['email'] = validated_data['email'].lower()

        if User.objects.filter(username=data['username']).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })
        elif User.objects.filter(email=data['email']).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        return validated_data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        # Create UserProfile object
        user.profile
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                "username": "User does not exist."
            })
        return data