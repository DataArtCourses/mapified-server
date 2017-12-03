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
        user = self.request.user.get('user_id')
        try:
            pin_id = await Pin.add_pin(self.request.app.objects, credentials, user=user)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response({"pinId": pin_id}, status=200)


class PinInfoView(BaseView):

    """ Pin info view """

    @login_required
    async def get(self):
        try:
            pin = await Pin.get_info(self.request.app.objects)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error read pin'}, status=400)
        return json_response(pin, status=200)


class PinCommentsView(BaseView):
    pass


class PhotosView(BaseView):
    pass


class PhotoCommentsView(BaseView):
    pass


class LikeView(BaseView):
    pass
