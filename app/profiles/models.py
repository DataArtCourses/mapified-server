import datetime
import logging
import jwt

from peewee import (
                    PrimaryKeyField,
                    CharField,
                    TextField,
                    TimeField,
                    SmallIntegerField,
                    ForeignKeyField
                    )


from app.base.settings import Settings
from app.base.models import BaseModel
from app.profiles import utils

settings = Settings()

log = logging.getLogger('application')


class UserModel(BaseModel):

    """ User model"""

    user_id = PrimaryKeyField()
    email = CharField(max_length=255, unique=True, null=False)
    password = CharField(max_length=32, null=False)
    first_name = CharField(max_length=255, default='')
    last_name = CharField(max_length=255, default='')
    phone = CharField(max_length=20, default='')
    bio = TextField(default='')
    avatar_url = CharField(max_length=255, default='')
    created = TimeField(default=datetime.datetime.now())
    confirm_key = CharField(max_length=255, default='')
    registered = SmallIntegerField(default=0)

    @classmethod
    async def confirm_registration(cls, objects, confirm_key):
        user = await objects.get(cls, confirm_key=confirm_key)
        user.registered = 1
        user.confirm_key = ''
        await objects.update(user)
        log.info("User %s successfuly confirmed registration", user.email)
        return

    @classmethod
    async def create_new(cls, objects, email, password):
        password = utils.encrypt_password(email=email, password=password)
        register_link = utils.create_register_link(password, email, settings.SALT)
        await objects.create(cls, email=email, password=password, confirm_key=register_link)
        return register_link

    @classmethod
    async def login(cls, objects, email, password):
        password = utils.encrypt_password(email=email, password=password)
        user = await objects.get(cls.select().where((cls.email == email) & (cls.password == password)))
        payload = {
            'user_id': user.user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60000)
        }
        jwt_token = jwt.encode(payload, settings.SALT, 'HS256')
        log.info('User %s has logged in', user.email)
        return dict(token=jwt_token.decode('utf-8'), user_id=user.user_id)

    @classmethod
    async def update_profile(cls, objects, user_id, profile):
        user = await objects.get(cls, user_id=user_id)
        user.first_name = profile.get('first_name', '')
        user.last_name = profile.get('last_name', '')
        user.phone = profile.get('phone', '')
        user.bio = profile.get('bio', '')
        user.avatar_url = profile.get('avatar_url', '')
        await objects.update(user)
        return None

    @classmethod
    async def get_profile(cls, objects, user_id):
        user = await objects.get(cls, user_id=user_id)
        return dict(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=user.phone,
                    bio=user.bio,
                    avatar_url=user.avatar_url,
                    )

    @classmethod
    async def get_all(cls, objects):
        users = await objects.execute(cls.select())
        response = [dict(
                        user_id=user.user_id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        avatar_url=user.avatar_url
                        ) for user in users]
        return response

    async def get_friends(self, objects):
        pass


class Friends(BaseModel):

    """ Friends relationships """

    user = ForeignKeyField(UserModel, related_name="user")
    friend = ForeignKeyField(UserModel, related_name="friend")

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('user', 'friend'), True),
        )