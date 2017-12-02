import datetime
import logging

from peewee import (
                    PrimaryKeyField,
                    IntegerField,
                    CharField,
                    TextField,
                    DecimalField,
                    TimeField,
                    ForeignKeyField,
                    SmallIntegerField
                    )

from app.base.settings import Settings
from app.base.models import BaseModel
from app.profiles.models import UserModel as User

settings = Settings()

log = logging.getLogger('application')


class PinModel(BaseModel):

    """ Pin model """

    pin_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name='pin')
    pin_info = CharField(max_length=400, default='')
    pin_lat = DecimalField(max_digits=10, decimal_places=8, )
    pin_lng = DecimalField(max_digits=11, decimal_places=8, )
    total_comments = IntegerField(default=1)
    total_photos = IntegerField(default=0)
    pin_status = SmallIntegerField(default=0)
    created = TimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-pin_id',)

    @classmethod
    async def add_pin(cls, objects, info, user):
        await objects.create(cls, author=user, pin_lat=info['location']['lat'], pin_lng=info['location']['lng'])
        pin = await objects.execute(cls.select(author=user))
        pin = pin[0].pin_id
        await objects.create(CommentModel, author=user, body=info['comment'], pin_id=pin)
        return pin

    @classmethod
    async def get_all(cls, objects):
        pins = await objects.execute(cls.select())
        response = [dict(
            pinId=pin.pin_id,
            pinInfo=pin.pin_info,
            location={
                "lat": float(pin.pin_lat),
                'lng': float(pin.pin_lng)
            },
            totalComments=pin.total_comments,
            totalPhotos=pin.total_photos,
            pinStatus=pin.pin_status
        ) for pin in pins]
        return response


class PhotoModel(BaseModel):

    """ Photo model """

    photo_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name="photo")
    photo_info = CharField(max_length=400, default='')
    pin = ForeignKeyField(PinModel, related_name="photo")
    photo_url = TextField()
    total_comments = IntegerField(default=0)
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


class PhotoLikes(BaseModel):

    """ Photo likes """

    photo = ForeignKeyField(CommentModel, related_name="who_like_photo")
    user = ForeignKeyField(User, related_name="liked_photo")
