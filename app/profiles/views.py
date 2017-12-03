import logging
import asyncio

import aiohttp_jinja2

from aiohttp import web
from aiohttp.web_response import json_response
from peewee import (
                    DoesNotExist,
                    IntegrityError,
                    DataError
                    )

from app.base.settings import Settings
from app.base.views import BaseView
from app.base.decorators import login_required
from .mailer import Mailer
from .models import UserModel as User


log = logging.getLogger('application')

settings = Settings()


class RegistrationView(BaseView):

    """ Registration model"""

    async def get(self):
        confirm_key = self.request.query.get('confirm')
        objects = self.request.app.objects
        try:
            await User.confirm_registration(objects, confirm_key)
        except DoesNotExist:
            log.info("Somebody tried to register once again with %s key", confirm_key)
            error = "Registration link expired"
            return web.Response(body=error, status=400)
        return web.HTTPFound('https://mapified.netlify.com/')

    async def post(self):
        new_user = await self.request.json()
        try:
            register_link = await User.create_new(self.request.app.objects, **new_user)
        except IntegrityError as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'User with this email already exists'}, status=400)
        else:
            link = f'http://{self.request.host}{self.request.path}?confirm={register_link}'
            tpl = aiohttp_jinja2.render_string('letter.html', request=self.request, context={'link': link})
            asyncio.ensure_future(Mailer.send_mail(receiver=new_user['email'],
                                                   subject='Mapified registration',
                                                   body=tpl))
        return json_response('Success', status=200)


class LoginView(BaseView):

    """ Login model """

    async def post(self):
        credentials = await self.request.json()
        try:
            token = await User.login(self.request.app.objects, **credentials)
        except DoesNotExist as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Wrong email or password. Please, try again.'}, status=400)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Email is not verified'}, status=400)
        else:
            return json_response(token, status=200)


class ProfileView(BaseView):

    """ Profile model"""

    @login_required
    async def get(self):
        user_id = self.request.match_info['user_id']
        print(user_id)
        try:
            profile = await User.get_profile(self.request.app.objects, user_id)
        except DoesNotExist as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Such user does not exist'}, status=400)
        return json_response(profile, status=200)

    @login_required
    async def post(self):
        email = self.request.user['email']
        log.info(f"User {email} trying to modify self data")
        user_data = await self.request.json()
        if not set(user_data.keys()) == {'first_name', 'last_name', 'phone', 'bio', 'avatar_url'}:
            return json_response({'error': "Request must consist all this fields: "
                                           "'first_name', 'surname', 'phone', 'bio', 'avatar_url'"}, status=400)
        owner = self.request.user.get('user_id')
        user_id = self.request.match_info['user_id']
        if int(user_id) != int(owner):
            return json_response({'error': 'You don`t have permission for it'}, status=403)
        try:
            await User.update_profile(self.request.app.objects, user_id, user_data)
        except DataError as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response('Success', status=200)


class AllUsersView(BaseView):

    """ All user info model """

    @login_required
    async def get(self):
        try:
            users = await User.get_all(self.request.app.objects)
        except Exception as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Something wrong'}, status=400)
        return json_response(users, status=200)