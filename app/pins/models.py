import datetime
import logging

from peewee import (
                    PrimaryKeyField,
                    IntegerField,
                    CharField,
                    DecimalField,
                    DateTimeField,
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
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-pin_id',)

    @classmethod
    async def add_pin(cls, objects, info, user):
        await objects.create(cls, author=user, pin_lat=info['location']['lat'], pin_lng=info['location']['lng'])
        pin = await objects.get(cls, author=user)
        pin = pin.pin_id
        await objects.create(CommentModel, author=user, body=info['comment'], pin_id=int(pin))
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

    @classmethod
    async def get_info(cls, objects, pin):
        pin = await objects.get(cls, pin_id=pin)
        return dict(
            pinId=pin.pin_id,
            pinInfo=pin.pin_info,
            location={
                "lat": float(pin.pin_lat),
                'lng': float(pin.pin_lng)
            },
            totalComments=pin.total_comments,
            totalPhotos=pin.total_photos,
            pinStatus=pin.pin_status
        )


class PhotoModel(BaseModel):

    """ Photo model """

    photo_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name="photo") # on_delete='CASCADE'
    photo_info = CharField(max_length=400, default='')
    pin = ForeignKeyField(PinModel, related_name="photo")
    photo_url = CharField(max_length=400, unique=True)
    total_comments = IntegerField(default=0)
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-photo_id', )

    @classmethod
    async def add_photo(cls, objects, info, user, pin):
        await objects.create(cls,
                             author=user,
                             photo_url=info.get('photo_url'),
                             pin=pin,
                             photo_info=info.get('photo_info', ''))
        photo = await objects.get(cls, author=user)
        pin = await objects.get(PinModel, pin_id=pin)
        total = pin.total_photos
        pin.total_photos = total + 1
        await objects.update(pin)
        return photo.photo_id

    @classmethod
    async def get_pin_gallery(cls, objects, pin):
        query = cls.select(cls, User).join(User).switch(cls)
        try:
            photos = await objects.execute(query.where(cls.pin == pin))
            request = [dict(
                author={
                    'userId': photo.author.user_id,
                    'userName': f"{photo.author.first_name} {photo.author.last_name}",
                    'avatarUrl': photo.author.avatar_url
                },
                photoId=photo.photo_id,
                photoUrl=photo.photo_url,
                photoInfo=photo.photo_info,
                created=str(photo.created)
            ) for photo in photos]
        except PhotoModel.DoesNotExist:
            request = []
        return request


class CommentModel(BaseModel):

    """ Comment model """

    comment_id = PrimaryKeyField()
    author = ForeignKeyField(User, related_name="comment")
    pin = ForeignKeyField(PinModel, related_name="comment")
    photo = ForeignKeyField(PhotoModel, related_name="comment", null=True)
    body = CharField(max_length=400, null=False)
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-comment_id', )

    @classmethod
    async def get_comments(cls, objects, pin_id=None, photo_id=None):
        query = cls.select(cls, User).join(User).switch(cls)
        try:
            if photo_id:
                comments = await objects.execute(query.where(cls.photo == photo_id))
            else:
                comments = await objects.execute(query.where(cls.pin == pin_id))
        except CommentModel.DoesNotExist:
            comments = []
        response = []
        if comments:
            response = [dict(
                commentId=comment.comment_id,
                commentBody=comment.body,
                author={
                    'userId': comment.author.user_id,
                    'userName': f"{comment.author.first_name} {comment.author.last_name}",
                    'avatarUrl': comment.author.avatar_url
                },
                created=str(comment.created)
            ) for comment in comments]
        return response

    @classmethod
    async def add_comment(cls, objects, info,  user):
        if info['pin_id']:
            await objects.create(cls, author=user, body=info['body'], pin=int(info['pin_id']))
            pin = await objects.get(PinModel, pin_id=info['pin_id'])
            total = pin.total_comments
            pin.total_comments = total + 1
            await objects.update(pin)
        elif info['photo_id']:
            await objects.create(cls, author=user, body=info['body'], pin=int(info['pin_id']), photo=int(info['photo_id']))
        else:
            raise Exception("Please enter correct id for pin or photo")
        comment = await objects.get(cls, author=user)
        return dict(commentId=comment.comment_id, created=str(comment.created))

# http://docs.peewee-orm.com/en/latest/peewee/querying.html#multiple-foreign-keys-to-the-same-model


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