from django.db import models
from django.contrib.auth.models import User
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

    def __str__(self):
        # will show tweet contents when run print(tweet instance) in python manage.py shell
        return f"{self.created_at} {self.user}: {self.content}"