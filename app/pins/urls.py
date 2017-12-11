from .views import (
                    PinsView,
                    AddCommentView,
                    AddPhotoView,
                    CommentView,
                    PinCommentsView,
                    PinPhotosView,
                    PhotoCommentsView,
                    LikeView
                    )

routes = [
    dict(method='*', path='/api/pins', handler=PinsView, name='pins'),
    dict(method='*', path='/api/pins/{pin_id}/comments', handler=PinCommentsView, name='pin-comments'),
    dict(method='*', path='/api/pins/{pin_id}/photos', handler=PinPhotosView, name='pin-photos'),
    dict(method='*', path='/api/photos/{photo_id}', handler=PhotoCommentsView, name='photo-comments'),
    dict(method='POST', path='/api/photos', handler=AddPhotoView, name='photos'),
    dict(method='POST', path='/api/comments', handler=AddCommentView, name='comments'),
    dict(method='*', path='/api/comments/{comment_id}', handler=CommentView, name='comment'),
    dict(method='GET', path='/api/comments/{comment_id}/like', handler=LikeView, name='like'),
]
