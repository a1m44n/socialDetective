from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from .models import Post, SocialMediaPost, AcquiredTweet
from .serializers import SocialMediaPostSerializer, PostSerializer
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_http_methods
import json
import re
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.conf import settings
import tweepy
import requests
from datetime import datetime
from django.core.cache import cache
import os
import hashlib
from textblob import TextBlob
from .twitter_utils import (
    fetch_tweets_with_retry,
    get_cached_tweets,
    set_cached_tweets,
    format_tweet_data,
    rate_limit
)

def analyze_sentiment_text(text):
    analysis = TextBlob(text)
    # Convert polarity to single dictionary format instead of list
    if analysis.sentiment.polarity > 0:
        return {"label": "LABEL_2", "score": analysis.sentiment.polarity}
    elif analysis.sentiment.polarity < 0:
        return {"label": "LABEL_0", "score": abs(analysis.sentiment.polarity)}
    return {"label": "LABEL_1", "score": 1.0}

# Map model output to human-readable labels
label_map = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE"
}

# Twitter API credentials
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Initialize Twitter client v2
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def generate_hash(data):
    """Generate SHA256 hash of the data"""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()

# Define `AnalyzeTextView`
class AnalyzeTextView(View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get("text", "")
        if text:
            result = analyze_sentiment_text(text)
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
    input_text = ""
    normalized_text = ""
    
    if request.method == "POST":
        input_text = request.POST.get("text", "")
        normalized_text = normalize_text(input_text)

    return render(request, "home.html", {
        "input_text": input_text,
        "normalized_text": normalized_text
    })

# Define `analyze_sentiment`
@csrf_exempt
def analyze_sentiment(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        if text:
            result = analyze_sentiment_text(text)
            return JsonResponse(result, safe=False)
        return JsonResponse({"error": "No text provided"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@require_POST
def normalize_text(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        normalized_text = ' '.join(text.lower().strip().split())
        return JsonResponse({'normalized_text': normalized_text})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
@csrf_exempt  # Disable CSRF just for testing (we'll secure this later)
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                return JsonResponse({'message': 'Login successful', 'role': role})
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'message': 'Server error', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)

# Initialize Twitter API client only if credentials are available
try:
    if all([
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    ]):
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )
        auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        twitter_api = tweepy.API(auth)
    else:
        twitter_api = None
except Exception as e:
    print(f"Error initializing Twitter API: {str(e)}")
    twitter_api = None

@api_view(['GET'])
def search_twitter(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    filters = request.GET.get('filters', {})
    
    if not query:
        return Response({"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Check cache first
        cached_results = get_cached_tweets(query, page, filters)
        if cached_results:
            return Response(cached_results)
        
        # Fetch from Twitter API
        tweets = fetch_tweets_with_retry(
            query=query,
            max_results=page_size,
            pagination_token=None if page == 1 else request.GET.get('next_token')
        )
        
        results = []
        for tweet in tweets.data:
            # Format tweet data
            tweet_data = format_tweet_data(tweet)
            
            # Analyze sentiment
            sentiment = analyze_sentiment_text(tweet.text)
            tweet_data['sentiment'] = label_map[sentiment['label']]
            tweet_data['sentiment_score'] = sentiment['score']
            
            results.append(tweet_data)
        
        response_data = {
            'results': results,
            'meta': tweets.meta,
            'page': page,
            'page_size': page_size
        }
        
        # Cache the results
        set_cached_tweets(query, page, response_data, filters)
        
        return Response(response_data)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def search_social_media(request):
    data = request.data
    platform = data.get('platform', 'twitter')
    query = data.get('query', '')
    filters = data.get('filters', {})

    if not query:
        return Response({'error': 'Query is required'}, status=400)

    results = []

    if platform == 'twitter':
        try:
            # Check cache first
            cached_results = get_cached_tweets(query, 1, filters)
            if cached_results:
                return Response(cached_results)
            
            # Fetch from Twitter API
            tweets = fetch_tweets_with_retry(
                query=query,
                max_results=10
            )
            
            for tweet in tweets.data:
                tweet_data = format_tweet_data(tweet)
                
                # Save to database
                post_data = {
                    'platform': 'Twitter',
                    'username': tweet.author_id,
                    'text': tweet.text,
                    'timestamp': tweet.created_at,
                    'metadata': tweet_data
                }
                post_hash = generate_hash(post_data)
                
                AcquiredTweet.objects.create(
                    tweet_id=tweet.id,
                    username=tweet.author_id,
                    text=tweet.text,
                    raw_data=post_data,
                    hash=post_hash,
                    created_at=tweet.created_at,
                    read_only=True
                )
                
                # Add sentiment analysis
                sentiment = analyze_sentiment_text(tweet.text)
                tweet_data['sentiment'] = label_map[sentiment['label']]
                tweet_data['sentiment_score'] = sentiment['score']
                
                results.append(tweet_data)
            
            response_data = {
                'results': results,
                'meta': tweets.meta
            }
            
            # Cache the results
            set_cached_tweets(query, 1, response_data, filters)
            
            return Response(response_data)
                
        except Exception as e:
            print("Error in search_social_media:", e)
            return Response({'error': str(e)}, status=500)

    return Response({'results': results})

class SocialSearchView(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        platform = request.data.get('platform', '').lower()
        posts = Post.objects.all()

        if platform in ['twitter', 'instagram']:
            posts = posts.filter(platform__iexact=platform)
        if query:
            posts = posts.filter(
                text__icontains=query
            )  # You can expand this to search username/hashtags

        serializer = PostSerializer(posts[:50], many=True)  # Limit results
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)

@csrf_exempt
def test_api(request):
    return JsonResponse({"message": "It works!"})

@require_http_methods(["POST"])
@permission_classes([IsAdminUser])
def update_acquired_tweet(request, tweet_id):
    tweet = AcquiredTweet.objects.get(tweet_id=tweet_id)
    if tweet.read_only:
        return JsonResponse({'error': 'This record is write-protected.'}, status=403)
    # ...proceed with update...

@require_http_methods(["DELETE"])
@permission_classes([IsAdminUser])
def delete_acquired_tweet(request, tweet_id):
    tweet = AcquiredTweet.objects.get(tweet_id=tweet_id)
    if tweet.read_only:
        return JsonResponse({'error': 'This record is write-protected.'}, status=403)
    tweet.delete()
    return JsonResponse({'success': True})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def lock_acquired_tweet(request, tweet_id):
    tweet = AcquiredTweet.objects.get(tweet_id=tweet_id)
    tweet.read_only = True
    tweet.save()
    return Response({'success': True, 'read_only': tweet.read_only})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def unlock_acquired_tweet(request, tweet_id):
    tweet = AcquiredTweet.objects.get(tweet_id=tweet_id)
    tweet.read_only = False
    tweet.save()
    return Response({'success': True, 'read_only': tweet.read_only})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_tweets(request):
    query = request.data.get('query', '')
    if not query:
        return Response({'error': 'Query is required'}, status=400)
        
    try:
        tweets = twitter_client.search_recent_tweets(
            query=query,
            max_results=100
        )
        
        results = []
        for tweet in tweets.data:
            sentiment = analyze_sentiment_text(tweet.text)
            results.append({
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'sentiment': label_map[sentiment['label']],
                'score': sentiment['score']
            })
            
        return Response({'results': results})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)






