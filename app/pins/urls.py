from .views import (
                    PinsView,
                    PinInfoView,
                    PinCommentsView,
                    PhotosView,
                    PhotoCommentsView
                    )

routes = [
    dict(method='*', path='/api/pins', handler=PinsView, name='pins'),
    dict(method='*', path='/api/pins/{pin_id}', handler=PinInfoView, name='pin-info'),
    dict(method='*', path='/api/pins/{pin_id}/comments', handler=PinCommentsView, name='pin-comments'),
    dict(method='*', path='/api/pins/{pin_id}/photos', handler=PhotosView, name='pin-photos'),
    dict(method='*', path='/api/photos/{photo_id}', handler=PhotoCommentsView, name='photo-comments'),
]
