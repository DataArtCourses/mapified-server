import logging
import asyncio
import datetime

import aiohttp_jinja2
import jwt

from aiohttp import web
from aiohttp.web_response import json_response
from peewee import (
                    DoesNotExist,
                    IntegrityError
                    )

from app.profiles import utils
from app.base.settings import Settings
from app.base.views import BaseView
from app.base.decorators import login_required
from .mailer import Mailer
from .models import UserModel as User


log = logging.getLogger('application')

settings = Settings()


class RegistrationView(BaseView):

    async def get(self):
        confirm_key = self.request.query.get('confirm')
        objects = self.request.app.objects
        try:
            user = await objects.get(User, confirm_key=confirm_key)
        except DoesNotExist:
            log.info("Somebody tried to register once again with %s key", confirm_key)
            error = "Registration link expired"
            return web.Response(body=error, status=400)
        else:
            user.registered = 1
            user.confirm_key = ''
            await objects.update(user)
            log.info("User %s successfuly confirmed registration", user.email)
        return web.Response(body="Thanks for registration!", status=200)

    async def post(self):
        new_user = await self.request.json()
        password = utils.encrypt_password(new_user.get('password'), new_user.get('email'))
        register_link = utils.create_register_link(password, new_user.get('email'), settings.SALT)
        new_user = dict(email=new_user.get('email'), password=password, confirm_key=register_link)
        try:
            await self.request.app.objects.create(User, **new_user)
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

    async def post(self):
        credentials = await self.request.json()
        try:
            user = await self.request.app.objects.get(User.select().where(
                (User.email == credentials.get('email')) & (User.password == utils.encrypt_password(**credentials))))
        except DoesNotExist as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Wrong credentials'}, status=400)
        else:
            payload = {
                'user_id': user.user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60000)
            }
            jwt_token = jwt.encode(payload, settings.SALT, 'HS256')
            log.info('User %s has logged in', user.email)
            print(payload)
            return json_response(
                {'token': jwt_token.decode('utf-8'), 'user': user.user_id, 'user_email': user.email}
            )


class ProfileView(BaseView):

    @login_required
    async def get(self):
        user_id = self.request.match_info['user_id']
        try:
            user = await self.request.app.objects.get(User, user_id=user_id)
        except DoesNotExist as e:
            log.exception("Encountered error in %s (%s)", self.__class__, e)
            return json_response({'error': 'Such user does not exist'}, status=400)
        return json_response(dict(
                                  user_id=user.user_id,
                                  first_name=user.first_name,
                                  last_name=user.last_name,
                                  email=user.email,
                                  phone=user.phone,
                                  bio=user.bio,
                                  avatar_url=user.avatar_url
                                  ), status=200)

    @login_required
    async def put(self):
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
        user = await self.request.app.objects.get(User, user_id=user_id)
        user.first_name = user_data.get('first_name', '')
        user.last_name = user_data.get('last_name', '')
        user.phone = user_data.get('phone', '')
        user.bio = user_data.get('bio', '')
        user.avatar_url = user_data.get('avatar_url', '')
        await self.request.app.objects.update(user)
        return json_response('Success', status=200)
