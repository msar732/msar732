from datetime import datetime

def global_settings(request):
	return {
		"now": datetime.now(),
	}