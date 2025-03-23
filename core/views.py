from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import torch
from transformers import pipeline
from rest_framework.generics import ListCreateAPIView
from .models import SocialMediaPost
from .serializers import SocialMediaPostSerializer
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

# Load sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Define `AnalyzeTextView`
class AnalyzeTextView(View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get("text", "")
        if text:
            result = sentiment_pipeline(text)
            return JsonResponse(result, safe=False)
        return JsonResponse({"error": "No text provided"}, status=400)

# Define `SocialMediaPostListCreateView`
class SocialMediaPostListCreateView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Fetching social media posts..."})

    def post(self, request, *args, **kwargs):
        return JsonResponse({"message": "Creating a social media post..."})

# Define `home`
def home(request):
    return render(request, "core/home.html")

# Define `analyze_sentiment`
def analyze_sentiment(request):
    text = request.GET.get("text", "")
    if text:
        result = sentiment_pipeline(text)
        return JsonResponse(result, safe=False)
    return JsonResponse({"error": "No text provided"}, status=400)
