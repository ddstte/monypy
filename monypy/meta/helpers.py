import asyncio
from contextlib import suppress
from functools import lru_cache
from itertools import chain

from bson.codec_options import DEFAULT_CODEC_OPTIONS
from motor.motor_asyncio import AsyncIOMotorClient

from ..manager import Manager, ManagerDescriptor


def get_database(**database_attrs):
    attrs = dict(database_attrs)
    db_name = attrs.pop('name')
    client = create_motor_client(**attrs)
    return client[db_name]


@lru_cache(maxsize=100, typed=True)
def create_motor_client(**kwargs):
    loop = asyncio.get_running_loop()
    return AsyncIOMotorClient(**kwargs, io_loop=loop)


def get_collection(doc_class, db, **options):
    collection_name = options.get('name') or doc_class.__name__.lower()
    collection_codec_options = (DEFAULT_CODEC_OPTIONS
                                .with_options(document_class=doc_class))

    return (db[collection_name]
            .with_options(collection_codec_options))


def manager_factory(doc_class, collection):
    manager_doc_class = doc_class.manager_class
    manager_class = (manager_doc_class.for_doc(doc_class)
                     if manager_doc_class is Manager
                     else manager_doc_class)

    manager = manager_class(collection)
    return ManagerDescriptor(manager)


def find_token(classes, token):
    def find(cls):
        targets = (c.__dict__.get(token) for c in cls.__mro__)
        return filter(None, targets)

    with suppress(StopIteration):
        return next(chain.from_iterable(map(find, classes)))
