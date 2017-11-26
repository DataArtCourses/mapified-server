import jwt

from aiohttp.web_response import json_response


from app.profiles.models import UserModel as User
from app.base.settings import Settings

settings = Settings()


async def auth_middleware(_, handler):
    async def middleware(request):
        request.user = None
        jwt_token = request.headers.get('Authorization', None)
        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, settings.SALT, algorithms=['HS256'])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return json_response({'message': 'Token is invalid'}, status=400)
            user = await request.app.objects.get(User, user_id=payload['user_id'])
            request.user = dict(user_id=user.user_id, email=user.email)
        return await handler(request)
    return middleware
