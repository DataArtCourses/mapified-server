from .views import (
                RegistrationView,
                LoginView,
                ProfileView
                )

routes = [
    dict(method='*', path='/api/register', handler=RegistrationView, name='registration'),
    dict(method='*', path='/api/login', handler=LoginView, name='login'),
    dict(method='*', path='/api/profile/{user_id}', handler=ProfileView, name='profile')
]
