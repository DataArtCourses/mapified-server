import datetime
import logging

from peewee import (
                    PrimaryKeyField,
                    CharField,
                    TextField,
                    DecimalField,
                    TimeField,
                    ForeignKeyField,
                    )

from app.base.settings import Settings
from app.base.models import BaseModel
from app.profiles.models import UserModel as User

settings = Settings()

log = logging.getLogger('application')


class PinModel(BaseModel):

    """ Pin model """

    pin_id = PrimaryKeyField()
    pin_info = CharField(max_length=400, default='')
    pin_lat = DecimalField(max_digits=10, decimal_places=8)
    pin_lng = DecimalField(max_digits=11, decimal_places=8)
    created = TimeField(default=datetime.datetime.now)

    @classmethod
    async def add_pin(cls, objects, info):
        print(info)

    @classmethod
    async def get_all(cls, objects):
        pins = await objects.execute(cls.select())
        response = [dict(
            pin_id=pin.pin_id,
            pin_info=pin.pin_info,
            pin_lat=pin.lat,
            pin_lng=pin.lng
        ) for pin in pins]
        return response


class PhotoModel(BaseModel):

    """ Photo model """

    photo_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name="photo")
    pin = ForeignKeyField(PinModel, related_name="photo")
    photo_url = TextField()
    created = TimeField(default=datetime.datetime.now)


class CommentModel(BaseModel):

    """ Comment model """

    comment_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name="comment")
    pin = ForeignKeyField(PinModel, related_name="comment")
    photo = ForeignKeyField(PhotoModel, related_name="comment", null=True)
    body = CharField(max_length=400, null=False)
    created = TimeField(default=datetime.datetime.now)


class CommentLikes(BaseModel):

    """ Comment likes """

    comment = ForeignKeyField(CommentModel, related_name="who_like_comment")
    user = ForeignKeyField(User, related_name="liked_comment")

    class Meta:
        indexes = (
            # Specify a unique multi-column index on comment/user.
            (('comment', 'user'), True),
        )


class PhotoLikes(BaseModel):

    """ Photo likes """

    photo = ForeignKeyField(CommentModel, related_name="who_like_photo")
    user = ForeignKeyField(User, related_name="liked_photo")

    class Meta:
        indexes = (
            # Specify a unique multi-column index on comment/user.
            (('photo', 'user'), True),
        )
