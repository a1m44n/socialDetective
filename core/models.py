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


