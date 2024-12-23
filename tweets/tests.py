from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase


class TweetTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.tweet = self.create_tweet(self.user1, content = "I'm Hanpi.")

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        user2 = self.create_user('user2')
        self.create_like(user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)