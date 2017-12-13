import logging

from aiohttp.web_response import json_response

from app.base.decorators import login_required
from app.base.views import BaseView

from app.messenger.models import (
                                  MessagesModel,
                                  ChatsModel,
                                  )

log = logging.getLogger('application')


class ChatsView(BaseView):

    """ Chats view """

    @login_required
    async def get(self):
        user = self.request.user.get('user_id')
        try:
            pins = await ChatsModel.get_chats(self.request.app.objects, user)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response(pins, status=200)


class ChatView(BaseView):

    """ Chat view """

    @login_required
    async def get(self):
        user = self.request.user.get('user_id')
        chat = self.request.match_info['pin_id']
        try:
            pins = await MessagesModel.get_chat(self.request.app.objects, user, chat_id=chat)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response(pins, status=200)

    @login_required
    async def post(self):
        user = self.request.user.get('user_id')
        chat = self.request.match_info['pin_id']
        try:
            pins = await MessagesModel.get_chat(self.request.app.objects, user, chat_id=chat)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response(pins, status=200)
