from .views import (
                    ChatsView,
                    ChatView
                    )

routes = [
    dict(method='GET', path='/api/chats', handler=MessagesView, name='chats'),
    dict(method='*', path='/api/chats/{chat_id}', handler=MessageView, name='chat'),
]