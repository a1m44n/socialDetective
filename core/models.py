from django.db import models

class SocialMediaPost(models.Model):
    content = models.TextField()
    platform = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} post at {self.created_at}"

class Post(models.Model):
    platform = models.CharField(max_length=20)  # e.g., 'Twitter', 'Instagram'
    username = models.CharField(max_length=150)
    text = models.TextField()
    timestamp = models.DateTimeField()
    sentiment_label = models.CharField(max_length=20, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.platform} post by {self.username} at {self.timestamp}"

class AcquiredTweet(models.Model):
    tweet_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    text = models.TextField()
    raw_data = models.JSONField()
    hash = models.CharField(max_length=64)  # SHA256 hash
    sentiment = models.JSONField(null=True)
    created_at = models.DateTimeField()
    acquired_at = models.DateTimeField(auto_now_add=True)
    read_only = models.BooleanField(default=False)

    def __str__(self):
        return f"Tweet {self.tweet_id} by {self.username}"

    class Meta:
        ordering = ['-created_at']


