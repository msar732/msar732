from django.http import JsonResponse
from django.core.cache import cache
from .data_loader import load_india_locations


def api_states_districts(request):
	cache_key = "india_states_districts_v1"
	data = cache.get(cache_key)
	if data is None:
		data = load_india_locations()
		cache.set(cache_key, data, 86400)
	return JsonResponse(data)