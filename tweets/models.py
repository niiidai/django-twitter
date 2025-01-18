from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from utils.time_helpers import utc_now

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who tweeted this tweet",
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at',)

    @property
    def hours_to_now(self):
        # datetime.now() does not contain time zone info,
        # therefore we can't use datetime.now() minus self.created_at
        return (utc_now() - self.created_at).seconds // (60 * 60)

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # will show tweet contents when run print(tweet instance) in python manage.py shell
        return f'{self.created_at} {self.user}: {self.content}'


class TweetPhoto(models.Model):
    # The photo will be shown in this tweet
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)

    # Can be convenient when we want to flag/monitor a certain users'
    # newly-uploaded photos or ban all the photos this user has uploaded.
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # Photo files
    file = models.FileField()
    order = models.IntegerField(default=0)

    # Photo status; initially pending for review
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # Soft delete a photo. When deleting, we mark it as has_deleted=True first,
    # then permanently delete it after a certain amount of time.
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'