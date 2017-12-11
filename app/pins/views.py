import logging

from aiohttp.web_response import json_response

from app.base.decorators import login_required
from app.base.views import BaseView
from app.pins.models import (
                            PinModel as Pin,
                            CommentModel as Comment,
                            PhotoModel as Photo,
                            )

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
        pin_id = self.request.match_info['pin_id']
        try:
            pin = await Pin.get_info(self.request.app.objects, pin_id)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error read pin'}, status=400)
        return json_response(pin, status=200)


class PinCommentsView(BaseView):

    """ Pin comments view """

    @login_required
    async def get(self):
        pin_id = self.request.match_info['pin_id']
        try:
            pin = await Comment.get_comments(self.request.app.objects, pin_id=pin_id)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error read pin'}, status=400)
        return json_response(pin, status=200)


class AddPhotoView(BaseView):

    """Add pin photo"""

    @login_required
    async def post(self):
        credentials = await self.request.json()
        user = self.request.user.get('user_id')
        pin = self.request.match_info['pin_id']
        try:
            photo = await Photo.add_photo(self.request.app.objects, info=credentials, user=user, pin=pin)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error add_photo, try again'}, status=400)
        return json_response(photo, status=200)


class PinPhotosView(BaseView):

    """ Pin photos gallery view """

    @login_required
    async def get(self):
        pin = self.request.match_info['pin_id']
        try:
            gallery = await Photo.get_pin_gallery(self.request.app.objects, pin=pin)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error read photo gallery'}, status=400)
        return json_response(gallery, status=200)


class AddCommentView(BaseView):

    """Comments view """

    @login_required
    async def post(self):
        credentials = await self.request.json()
        user = self.request.user.get('user_id')
        try:
            comment = await Comment.add_comment(self.request.app.objects, info=credentials, user=user)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error write comment, try again'}, status=400)
        return json_response(comment, status=200)


class CommentView(BaseView):
    pass


class PhotoCommentsView(BaseView):

    """ Photo comments view """

    @login_required
    async def get(self):
        photo = self.request.match_info['photo_id']
        try:
            pin = await Comment.get_comments(self.request.app.objects, photo_id=photo)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Error read pin'}, status=400)
        return json_response(pin, status=200)


class LikeView(BaseView):
    pass
