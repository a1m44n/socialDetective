from django.db import models

class SocialMediaPost(models.Model):
    platform = models.CharField(max_length=50)  # e.g., Twitter or Instagram
    content = models.TextField()  # Post text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.platform} Post at {self.created_at}"
