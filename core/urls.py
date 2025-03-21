from django.urls import path
from .views import AnalyzeTextView, SocialMediaPostListCreateView

urlpatterns = [
    path('analyze-text/', AnalyzeTextView.as_view(), name='analyze-text'),
    path('social-posts/', SocialMediaPostListCreateView.as_view(), name='social-posts'),
]
