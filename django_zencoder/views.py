import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import signing
from .api import get_video

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def notification(request):
    if getattr(settings, 'ZENCODER_NOTIFICATION_SECRET', None) and (
            request.META.get('HTTP_X_ZENCODER_NOTIFICATION_SECRET') !=
            settings.ZENCODER_NOTIFICATION_SECRET):
        logger.warn('Invalid Zencoder notification secret', extra={'request': request})
        return HttpResponse('Invalid notification secret', status=400)  # BAD REQUEST

    try:
        data = signing.loads(request.META['QUERY_STRING'])
    except signing.BadSignature:
        logger.warn('Invalid payload for Zencoder notification',
                    extra={'request': request})
        return HttpResponse('Invalid payload', status=400)  # BAD REQUEST

    get_video(data['ct'], data['obj'], data['fld'], request.body)
    return HttpResponse(status=204)  # NO CONTENT
