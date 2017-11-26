import asyncio
import logging
import argparse

from app.main import create_app

from app.profiles.models import UserModel

loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app(loop))

log = logging.getLogger('application')
log.setLevel(0)
logging.root.setLevel(0)
log.addHandler(logging.StreamHandler())


async def db_import():
    logging.debug('Creating database')
    with app.objects.allow_sync():
        UserModel.create_table(True)
    log.info('Done creating database')


async def drop_tables():
    logging.debug('Deleting all tables...')
    with app.objects.allow_sync():
        UserModel.drop_table(True)
    logging.debug('Done deleting tables')

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

loop = asyncio.get_event_loop()
loop.run_until_complete(namespace.get(args.action, 'db_import')())


