from django.db import models
from django.contrib.auth.models import User
import uuid

# 1. Profile Model
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True, default='')
    profileimg = models.ImageField(upload_to='profile_images', default='dog.webp')
    location = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.user.username


# 2. Post Model
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


# 3. Like Model
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


# 4. Followers Model
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class Notification(models.Model):
    # NOTIFICATION TYPES: 1 = Like, 2 = Comment, 3 = Follow
    NOTIFICATION_TYPES = (
        (1, 'Like'),
        (2, 'Comment'),
        (3, 'Follow'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_sender')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_user')
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='notification_post', null=True, blank=True)
    text_preview = models.CharField(max_length=120, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.user.username} ({self.get_notification_type_display()})"
    
# models.py
from django.db import models
from django.contrib.auth.models import User

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.body[:20]}"