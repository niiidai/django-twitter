from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')
        self.user2_tweet = self.create_tweet(self.user2)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.user2_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.user1_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.user2_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)


class NotificationsAPITests(TestCase):

    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')
        self.user1_tweet = self.create_tweet(self.user1)

    def test_unread_count(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.user1_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.user1_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.user2_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.user1_tweet.id,
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        # GET is not allowed to mark all as read
        response = self.user1_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        # user 2 cannot mark user1's notifications as read
        response = self.user2_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # user 1 can mark their notifications as read and POST successfully
        response = self.user1_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.user1_tweet.id,
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # must log in to GET notification url
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # user 2 can't see any of these notifications
        response = self.user2_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # user 1 can see two notifications
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # marked the first notification as read
        notification = self.user1.notifications.first()
        notification.unread = False
        notification.save()
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.user1_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.user1_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.user2_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.user1_tweet.id,
        })
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.user1.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # Can't POST, must PUT
        response = self.user2_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)
        # the status of the notification can't changed by others
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)
        # the queryset requires current users, will return 404
        response = self.user2_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # Mark as read successfully
        response = self.user1_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # mark as unread again
        response = self.user1_client.put(url, {'unread': True})
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)
        # must include unread
        response = self.user1_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        # can't change other info
        response = self.user1_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')
