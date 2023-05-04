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

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends

from waterdip.server.db.models.alerts import AlertDB, BaseAlertDB
from waterdip.server.db.mongodb import MONGO_COLLECTION_INTEGRATIONS, MongodbBackend
from waterdip.server.db.models.integrations import BaseIntegrationDB
from waterdip.server.errors.base_errors import EntityAlreadyExistsError


class IntegrationRepository:
    _INSTANCE = None

    @classmethod
    def get_instance(
        cls, mongodb: MongodbBackend = Depends(MongodbBackend.get_instance)
    ):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(mongodb=mongodb)
        return cls._INSTANCE

    def __init__(self, mongodb: MongodbBackend):
        self._mongo = mongodb
        
    def list_integration(self) -> List[BaseIntegrationDB]:
        """
        List all integrations from the database
        """
        return [
            BaseIntegrationDB(**integration)
            for integration in self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].find({})
        ]

    def get_integration(self, integration_id: str) -> BaseIntegrationDB:
        return BaseIntegrationDB(
            **self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].find_one(
                {"integration_id": integration_id}
            )
        )

    def add_integration(self, integration: BaseIntegrationDB):
        """
        Insert a add integration into the database
        """
        if(self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].find_one({
            "configuration": integration.configuration,
        })):
          raise EntityAlreadyExistsError(name="Integration", message="Integration already exists")
        else:
            integration = self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].insert_one(
                integration.dict()
            )
            return BaseIntegrationDB(
                **self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].find_one(
                    {"_id": integration.inserted_id}
                )
            )

    def delete_integration(self, integration_id: str):
        """
        Delete a integration from the database
        """
        return self._mongo.database[MONGO_COLLECTION_INTEGRATIONS].delete_one(
            {"integration_id": integration_id}
        )