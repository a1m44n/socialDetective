from django.urls import path
from .views import AnalyzeTextView, SocialMediaPostListCreateView
from .views import home, analyze_sentiment

urlpatterns = [
    path('analyze-text/', AnalyzeTextView.as_view(), name='analyze-text'),
    path('social-posts/', SocialMediaPostListCreateView.as_view(), name='social-posts'),
     path("", home, name="home"),
    path("analyze_sentiment/", analyze_sentiment, name="analyze_sentiment"),
]
