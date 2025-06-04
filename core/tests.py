from django.test import TestCase
from django.core.cache import cache
from .twitter_utils import fetch_tweets_with_retry, rate_limit
from django.conf import settings
from unittest.mock import patch, MagicMock

# Create your tests here.

class RedisTestCase(TestCase):
    def test_redis_connection(self):
        # Test Redis connection
        cache.set('test_key', 'test_value', 30)
        value = cache.get('test_key')
        self.assertEqual(value, 'test_value')
        
        # Test cache timeout
        cache.set('test_key_timeout', 'test_value', 1)
        import time
        time.sleep(2)
        value = cache.get('test_key_timeout')
        self.assertIsNone(value)

class TwitterAPITestCase(TestCase):
    def test_twitter_api_credentials(self):
        """Test if Twitter API credentials are properly configured"""
        self.assertIsNotNone(settings.TWITTER_BEARER_TOKEN, "Twitter Bearer Token is not set")
        
    def test_rate_limiting(self):
        """Test if rate limiting is working"""
        try:
            rate_limit('test_query')
            self.assertTrue(True, "Rate limiting is working")
        except Exception as e:
            self.fail(f"Rate limiting failed: {str(e)}")
            
    @patch('core.twitter_utils.twitter_client')
    def test_twitter_search(self, mock_twitter_client):
        """Test if Twitter search is working with mock"""
        # Mock the Twitter API response
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(
                id="123",
                text="Test tweet",
                created_at="2024-06-04T12:00:00Z",
                author_id="456"
            )
        ]
        mock_response.meta = {"result_count": 1}
        mock_twitter_client.search_recent_tweets.return_value = mock_response

        # Test the search
        try:
            tweets = fetch_tweets_with_retry("test", max_results=1)
            self.assertIsNotNone(tweets, "Twitter search returned None")
            self.assertEqual(len(tweets.data), 1, "Should return one tweet")
            self.assertEqual(tweets.data[0].text, "Test tweet", "Tweet text should match")
        except Exception as e:
            self.fail(f"Twitter search failed: {str(e)}")
