import datetime
import logging

from peewee import (
                    PrimaryKeyField,
                    TextField,
                    DateTimeField,
                    ForeignKeyField,
                    SmallIntegerField
                    )

from app.base.settings import Settings
from app.base.models import BaseModel
from app.profiles.models import UserModel as User

settings = Settings()

log = logging.getLogger('application')


class MessagesModel(BaseModel):

    """ Messages Model """

    message_id = PrimaryKeyField()
    chat = ForeignKeyField(ChatsModel, related_name='chat')
    body = TextField()
    status = SmallIntegerField(default=0)
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-created',)

    @classmethod
    async def add_message(cls, objects, chat):
        pass

    @classmethod
    async def get_chat(cls, objects, user, chat_id):
        pass


class ChatsModel(BaseModel):

    """ Chat model """

    chat_id = PrimaryKeyField()
    user_form = ForeignKeyField(User, related_name='user_from')
    user_to = ForeignKeyField(User, related_name='user_to')
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-created',)

    @classmethod
    async def get_chats(cls, objects, user):
        query = cls.select(cls, User).join(User).switch(cls)
        try:
            chats = await objects.execute(query.where(cls.user_form == user))
        except ChatsModel.DoesNotExist:
            chats = []
        response = []
        if chats:
            response = [dict(
                commentId=chat.chat_id,
                userId={
                    'userId': chat.user_to.user_id,
                    'userName': f"{chat.user_to.first_name} {chat.user_to.last_name}",
                    'avatarUrl': chat.user_to.avatar_url
                },
            ) for chat in chats]
        return response
