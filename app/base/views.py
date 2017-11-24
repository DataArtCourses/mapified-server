from aiohttp_jinja2 import template
from aiohttp.web import View


class BaseView(View):

    @template('index.html')
    async def get(self):
        return {}
