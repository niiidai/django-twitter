from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now

class TweetTestCase(TestCase):
    def test_hours_to_now(self):
        nina = User.objects.create_user(username='nina')
        tweet = Tweet.objects.create(user=nina, content="I'm Hanpi.")
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
