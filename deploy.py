import asyncio
import logging
import argparse
import peewee_async

from aiohttp import web

from app.profiles.models import (UserModel, Friends, )
from app.pins.models import (PinModel, PhotoModel, PhotoLikes, CommentModel, CommentLikes)
from app.base.models import database
from app.main import DATABASE


log = logging.getLogger('application')
log.setLevel(0)
logging.root.setLevel(0)
log.addHandler(logging.StreamHandler())


async def create_app(_loop):
    _app = web.Application(loop=_loop)

    # db conn
    database.init(**DATABASE)
    _app.database = database
    _app.database.set_allow_sync(False)
    _app.objects = peewee_async.Manager(database)

    return _app


async def db_import():
    logging.debug('Creating database')
    with app.objects.allow_sync():
        UserModel.create_table(True)
        Friends.create_table(True)
        PinModel.create_table(True)
        PhotoModel.create_table(True)
        CommentModel.create_table(True)
        CommentLikes.create_table(True)
        PhotoLikes.create_table(True)
    log.info('Done creating database')


async def drop_tables():
    logging.debug('Deleting all tables...')
    with app.objects.allow_sync():
        Friends.drop_table(True)
        PhotoLikes.drop_table(True)
        CommentLikes.drop_table(True)
        CommentModel.drop_table(True)
        PhotoModel.drop_table(True)
        PinModel.drop_table(True)
        UserModel.drop_table(True)
    logging.debug('Done deleting tables')


loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app(loop))

# Args parse
parser = argparse.ArgumentParser()
parser.add_argument("--action",
                    help="action to perform with DB",
                    default='db_import')
args = parser.parse_args()

namespace = {
    'db_import': db_import,
    'drop_tables': drop_tables
}

loop.run_until_complete(namespace.get(args.action, 'db_import')())


