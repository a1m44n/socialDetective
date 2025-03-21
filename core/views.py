from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import torch
from transformers import pipeline
from rest_framework.generics import ListCreateAPIView
from .models import SocialMediaPost
from .serializers import SocialMediaPostSerializer
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')
class AnalyzeTextView(APIView):
    def post(self, request):
        text = request.data.get('text', '')

        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Load NLP model (Hugging Face sentiment analysis)
        nlp_pipeline = pipeline("sentiment-analysis")

        # Perform analysis
        result = nlp_pipeline(text)[0]

        return Response({'text': text, 'analysis': result}, status=status.HTTP_200_OK)

# This class should NOT be inside AnalyzeTextView
class SocialMediaPostListCreateView(ListCreateAPIView):
    queryset = SocialMediaPost.objects.all()
    serializer_class = SocialMediaPostSerializer
