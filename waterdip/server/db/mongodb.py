#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from loguru import logger
from pymongo import MongoClient
from pymongo.database import Database

from waterdip.server.commons.config import settings

MONGO_COLLECTION_MODELS = settings.mongo_collection_models
MONGO_COLLECTION_MODEL_VERSIONS = settings.mongo_collection_model_versions
MONGO_COLLECTION_DATASETS = settings.mongo_collection_datasets
MONGO_COLLECTION_BATCH_ROWS = settings.mongo_collection_batch_rows
MONGO_COLLECTION_EVENT_ROWS = settings.mongo_collection_event_rows
MONGO_COLLECTION_MONITORS = settings.mongo_collection_monitors
MONGO_COLLECTION_ALERTS = settings.mongo_collection_alerts
MONGO_COLLECTION_INTEGRATIONS = settings.mongo_collection_integrations


class MongodbBackend:

    _INSTANCE = None

    @classmethod
    def get_instance(cls):
        if cls._INSTANCE is None:
            mongo_client = MongoClient(settings.mongo_url)
            cls._INSTANCE = cls(
                mongo_client=mongo_client, mongo_database=settings.mongo_database
            )
        return cls._INSTANCE

    def init(self):
        logger.info(f"connected to mongodb {self._client.server_info()}")

    def __init__(self, mongo_client: MongoClient, mongo_database: str):
        self._client = mongo_client
        self._database_name = mongo_database

    @property
    def client(self) -> MongoClient:
        """The pymongo client"""
        return self._client

    @property
    def database(self) -> Database:
        """The mongodb database"""
        return self._client[self._database_name]
