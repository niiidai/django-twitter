from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # One2One field will create a unique index to make sure
    # each UserProfile object is pointed to the corresponding User.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    avatar = models.FileField(null=True)
    # When a user has been created, a UserProfile object will also
    # be created. At this time, the user have not set up the nickname
    # and the avatar, and thus, we set null=True here.
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# Here, we define a property method for UserProfile in this User model.
# By doing this, we can use user_instance.profile to visit the profile
# object, rather than obtaining UserProfile.nickname and UserProfile.avatar
# separately from the database.
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    setattr(user, '_cached_user_profile', profile)
    return profile

# We add a property for user_profile for quick access in this User model.
User.profile = property(get_profile)