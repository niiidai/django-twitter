from friendships.models import Friendship

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # Wrong method 1:
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]
        # This method will cause N + 1 Queries. The first command will cost one query,
        # while the for loop in the second command will cost N queries.
        # DO NOT USE FOR LOOP + QUERIES

        # Wrong method 2:
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]
        # This method will use SQL JOIN and the temporal complexity will be N**2
        # DO NOT USE JOIN in webservices with many users.

        # Correct methods:
        # By using prefetch_related(), the next command is the same as:
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower.ids)
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]