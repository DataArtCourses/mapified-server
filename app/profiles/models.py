import datetime
import logging

from peewee import (
                    PrimaryKeyField,
                    CharField,
                    TextField,
                    TimeField,
                    SmallIntegerField,
                    IntegrityError,
                    DoesNotExist
                    )

from app.base.settings import Settings
from app.base.models import BaseModel
from app.profiles import utils
from app.profiles.exceptions import UserAlreadyExist, RegistrationLinkExpired, UserDoesNotExist, PasswordDoesNotMatch

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
        try:
            user = await objects.get(cls, confirm_key=confirm_key)
        except DoesNotExist:
            error = "Registration link for this user has been already activated or user does not exist"
            raise RegistrationLinkExpired(error)

        else:
            user.registered = 1
            user.confirm_key = ''
            await objects.update(user)
            log.info("User %s successfuly confirmed registration", user.email)


