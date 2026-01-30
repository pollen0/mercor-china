"""
Tests for cache service.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestCacheService:
    """Tests for Redis cache service."""

    def test_cache_service_initialization(self):
        """Test cache service initializes correctly."""
        from app.services.cache import CacheService

        service = CacheService()
        assert service._client is None
        assert service._available is False

    def test_make_key_single_arg(self):
        """Test key creation with single argument."""
        from app.services.cache import CacheService

        service = CacheService()
        key = service._make_key("prefix", "arg1")
        assert key == "prefix:arg1"

    def test_make_key_multiple_args(self):
        """Test key creation with multiple arguments."""
        from app.services.cache import CacheService

        service = CacheService()
        key = service._make_key("prefix", "arg1", "arg2", "arg3")
        assert key == "prefix:arg1:arg2:arg3"

    def test_make_key_with_none(self):
        """Test key creation ignores None values."""
        from app.services.cache import CacheService

        service = CacheService()
        key = service._make_key("prefix", "arg1", None, "arg3")
        assert key == "prefix:arg1:arg3"

    def test_serialize_dict(self):
        """Test serialization of dict."""
        from app.services.cache import CacheService

        service = CacheService()
        result = service._serialize({"key": "value", "number": 42})
        assert '"key"' in result
        assert '"value"' in result
        assert "42" in result

    def test_serialize_list(self):
        """Test serialization of list."""
        from app.services.cache import CacheService

        service = CacheService()
        result = service._serialize([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_deserialize(self):
        """Test deserialization."""
        from app.services.cache import CacheService

        service = CacheService()
        result = service._deserialize('{"key": "value"}')
        assert result == {"key": "value"}

    def test_get_when_unavailable(self):
        """Test get returns None when Redis is unavailable."""
        from app.services.cache import CacheService

        service = CacheService()
        service._available = False
        result = service.get("test_key")
        assert result is None

    def test_set_when_unavailable(self):
        """Test set returns False when Redis is unavailable."""
        from app.services.cache import CacheService

        service = CacheService()
        service._available = False
        result = service.set("test_key", {"data": "value"})
        assert result is False

    def test_delete_when_unavailable(self):
        """Test delete returns False when Redis is unavailable."""
        from app.services.cache import CacheService

        service = CacheService()
        service._available = False
        result = service.delete("test_key")
        assert result is False

    def test_delete_pattern_when_unavailable(self):
        """Test delete_pattern returns 0 when Redis is unavailable."""
        from app.services.cache import CacheService

        service = CacheService()
        service._available = False
        result = service.delete_pattern("test:*")
        assert result == 0


class TestCacheServiceWithMockedRedis:
    """Tests for cache service with mocked Redis."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mocked Redis client."""
        with patch("app.services.cache.redis") as mock:
            mock_client = MagicMock()
            mock.from_url.return_value = mock_client
            mock_client.ping.return_value = True
            yield mock_client

    def test_get_success(self, mock_redis):
        """Test successful cache get."""
        from app.services.cache import CacheService

        mock_redis.get.return_value = '{"cached": "data"}'

        service = CacheService()
        service._client = mock_redis
        service._available = True

        result = service.get("test_key")
        assert result == {"cached": "data"}
        mock_redis.get.assert_called_once_with("test_key")

    def test_get_miss(self, mock_redis):
        """Test cache miss."""
        from app.services.cache import CacheService

        mock_redis.get.return_value = None

        service = CacheService()
        service._client = mock_redis
        service._available = True

        result = service.get("nonexistent_key")
        assert result is None

    def test_set_success(self, mock_redis):
        """Test successful cache set."""
        from app.services.cache import CacheService

        service = CacheService()
        service._client = mock_redis
        service._available = True

        result = service.set("test_key", {"data": "value"}, ttl=60)
        assert result is True
        mock_redis.setex.assert_called_once()

    def test_delete_success(self, mock_redis):
        """Test successful cache delete."""
        from app.services.cache import CacheService

        service = CacheService()
        service._client = mock_redis
        service._available = True

        result = service.delete("test_key")
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")


class TestCacheServiceSpecificMethods:
    """Tests for specific cache methods (dashboard, questions, etc.)."""

    @pytest.fixture
    def mock_cache_service(self):
        """Create a cache service with mocked internals."""
        from app.services.cache import CacheService

        service = CacheService()
        service._available = True
        service._client = MagicMock()
        service._client.get.return_value = None
        return service

    def test_get_dashboard_stats(self, mock_cache_service):
        """Test dashboard stats cache key."""
        mock_cache_service._client.get.return_value = '{"total_interviews": 10}'

        result = mock_cache_service.get_dashboard_stats("employer_123")
        assert result == {"total_interviews": 10}
        mock_cache_service._client.get.assert_called_with("dashboard:employer_123")

    def test_set_dashboard_stats(self, mock_cache_service):
        """Test setting dashboard stats."""
        stats = {"total_interviews": 10, "pending": 5}
        mock_cache_service.set_dashboard_stats("employer_123", stats)

        mock_cache_service._client.setex.assert_called_once()

    def test_invalidate_dashboard(self, mock_cache_service):
        """Test dashboard cache invalidation."""
        mock_cache_service.invalidate_dashboard("employer_123")

        mock_cache_service._client.delete.assert_called_with("dashboard:employer_123")

    def test_get_questions_default(self, mock_cache_service):
        """Test getting default questions from cache."""
        mock_cache_service._client.get.return_value = '[{"text": "Q1"}]'

        result = mock_cache_service.get_questions()
        assert result == [{"text": "Q1"}]
        mock_cache_service._client.get.assert_called_with("questions:defaults")

    def test_get_questions_for_job(self, mock_cache_service):
        """Test getting job questions from cache."""
        mock_cache_service._client.get.return_value = '[{"text": "Job Q1"}]'

        result = mock_cache_service.get_questions("job_123")
        assert result == [{"text": "Job Q1"}]
        mock_cache_service._client.get.assert_called_with("questions:job_123")

    def test_get_top_candidates(self, mock_cache_service):
        """Test getting top candidates from cache."""
        mock_cache_service._client.get.return_value = '[{"candidate_id": "c1"}]'

        result = mock_cache_service.get_top_candidates("job_123", 10)
        assert result == [{"candidate_id": "c1"}]
        mock_cache_service._client.get.assert_called_with("top_candidates:job_123:10")

    def test_invalidate_top_candidates(self, mock_cache_service):
        """Test top candidates cache invalidation."""
        mock_cache_service._client.keys.return_value = [
            "top_candidates:job_123:5",
            "top_candidates:job_123:10"
        ]

        mock_cache_service.invalidate_top_candidates("job_123")

        mock_cache_service._client.keys.assert_called_with("top_candidates:job_123:*")

    def test_get_interview_session(self, mock_cache_service):
        """Test getting interview session from cache."""
        mock_cache_service._client.get.return_value = '{"id": "i123", "status": "COMPLETED"}'

        result = mock_cache_service.get_interview_session("i123")
        assert result["id"] == "i123"
        assert result["status"] == "COMPLETED"
