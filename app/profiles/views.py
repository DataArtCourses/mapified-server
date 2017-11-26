import logging
import asyncio
import aiohttp_jinja2

from aiohttp import web
from aiohttp.web_response import json_response

from .exceptions import UserAlreadyExist, RegistrationLinkExpired
from .mailer import Mailer
from .models import UserModel as User
from app.base.views import BaseView

log = logging.getLogger('application')


class RegistrationView(BaseView):

    async def get(self):
        confirm_key = self.request.query.get('confirm')
        objects = self.request.app.objects
        try:
            await User.confirm_registration(objects, confirm_key)
        except RegistrationLinkExpired:
            log.info("Somebody tried to register once again with %s key", confirm_key)
            error = "Registration link expired"
            return web.Response(body=error, status=400)
        return web.Response(body="Thanks for registration!", status=200)

    async def post(self):
        new_user = await self.request.json()
        print(new_user)
        try:
            register_link = await User.create_new_user(self.request.app.objects, **new_user)
        except UserAlreadyExist as e:
            return json_response({'error': str(e)}, status=400)
        else:
            link = f'http://{self.request.host}{self.request.path}?confirm={register_link}'
            tpl = aiohttp_jinja2.render_string('letter.html', request=self.request, context={'link': link})
            asyncio.ensure_future(Mailer.send_mail(receiver=new_user['email'],
                                                   subject='Mapified registration',
                                                   body=tpl))
        return json_response({'error': None})


class LoginView(BaseView):
    pass


class ProfileView(BaseView):
    pass
