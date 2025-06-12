import os
from django.core.cache import cache
from rest_framework.exceptions import Throttled
from tenacity import retry, stop_after_attempt, wait_exponential
import tweepy
from datetime import datetime
import hashlib
import json

# Twitter API Configuration
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def rate_limit(key, limit=180, period=900):  # 180 requests per 15 minutes
    """
    Implement rate limiting for Twitter API calls
    """
    cache_key = f'rate_limit_{key}'
    count = cache.get(cache_key, 0)
    if count >= limit:
        raise Throttled(detail="Twitter API rate limit exceeded. Please try again later.")
    cache.set(cache_key, count + 1, period)

def get_cache_key(query, page, filters=None):
    """
    Generate a unique cache key for the search query
    """
    key_parts = [query, str(page)]
    if filters:
        key_parts.append(json.dumps(filters, sort_keys=True))
    return f'tweets_{hashlib.md5("_".join(key_parts).encode()).hexdigest()}'

def get_cached_tweets(query, page, filters=None, cache_time=300):
    """
    Get tweets from cache or fetch from Twitter API
    """
    cache_key = get_cache_key(query, page, filters)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    return None

def set_cached_tweets(query, page, results, filters=None, cache_time=300):
    """
    Cache the Twitter search results
    """
    cache_key = get_cache_key(query, page, filters)
    cache.set(cache_key, results, cache_time)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_tweets_with_retry(query, max_results=10, pagination_token=None):
    """
    Fetch tweets with retry mechanism
    """
    try:
        rate_limit(query)  # Apply rate limiting
        
        # Prepare parameters
        params = {
            "query": query,
            "max_results": max_results
        }
        
        # Only add pagination_token if it's not None
        if pagination_token:
            params["pagination_token"] = pagination_token
            
        return twitter_client.search_recent_tweets(**params)
        
    except tweepy.TooManyRequests as e:
        raise Throttled(detail="Twitter API rate limit exceeded. Please try again later.")
    except Exception as e:
        raise Exception(f"Error fetching tweets: {str(e)}")

def format_tweet_data(tweet, include_metadata=True):
    """
    Format tweet data for response
    """
    tweet_data = {
        'id': tweet.id,
        'text': tweet.text,
        'created_at': tweet.created_at,
        'author_id': tweet.author_id,
    }
    
    if include_metadata:
        tweet_data.update({
            'retweet_count': getattr(tweet, 'public_metrics', {}).get('retweet_count', 0),
            'reply_count': getattr(tweet, 'public_metrics', {}).get('reply_count', 0),
            'like_count': getattr(tweet, 'public_metrics', {}).get('like_count', 0),
            'quote_count': getattr(tweet, 'public_metrics', {}).get('quote_count', 0),
        })
    
    return tweet_data 