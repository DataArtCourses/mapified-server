import logging

from aiohttp.web_response import json_response

from app.base.decorators import login_required
from app.base.views import BaseView
from app.pins.models import PinModel as Pin

log = logging.getLogger('application')


class PinsView(BaseView):

    """ Pins view """

    @login_required
    async def get(self):
        try:
            pins = await Pin.get_all(self.request.app.objects)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response(pins, status=200)

    @login_required
    async def post(self):
        credentials = await self.request.json()
        try:
            await Pin.add_pin(self.request.app.objects, credentials)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response("Success!", status=200)


class PinInfoView(BaseView):
    pass


class PinCommentsView(BaseView):
    pass


class PhotosView(BaseView):
    pass


class PhotoCommentsView(BaseView):
    pass


class LikeView(BaseView):
    pass
