import pytest
from django.core.cache import cache

@pytest.mark.django_db
def test_redis_cache():
    cache.set('hello', 'world', timeout=30) # store data in cache
    result = cache.get('hello') # get data from cache
    assert result == 'world'
    
    # clear cache
    cache.delete('hello')
    result = cache.get('hello')
    assert result is None
