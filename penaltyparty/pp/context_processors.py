from django.conf import settings

def version(request):
    return {
        'version': settings.VERSION,
    }
