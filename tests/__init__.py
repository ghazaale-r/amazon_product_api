import pytest
from django.core.cache import cache

@pytest.mark.django_db
def test_redis_cache():
    # Set a value in the cache
    cache.set('test_key', 'test_value', timeout=30)
    # Retrieve the value from the cache
    assert cache.get('test_key') == 'test_value'
