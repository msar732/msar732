from django.http import JsonResponse
from listings.models import State, District
from django.views.decorators.cache import cache_page


@cache_page(60 * 60)
def locations_json(request):
    states = list(State.objects.values('id', 'name'))
    districts = list(District.objects.values('id', 'name', 'state_id'))
    return JsonResponse({'states': states, 'districts': districts})

# Create your views here.
