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

from typing import List
from urllib.parse import urlparse

from pydantic import BaseSettings


class ServerSettings(BaseSettings):
    """
    Configuration for the backend server
    """

    mongo_url: str = "mongodb://dbuser:dbpass@127.0.0.1:27017/"
    redis_url: str = "redis://127.0.0.1:6379"
    mongo_database: str = "waterdip"
    mongo_collection_models: str = "wd_models"
    mongo_collection_model_versions: str = "wd_model_versions"
    mongo_collection_datasets: str = "wd_datasets"
    mongo_collection_batch_rows: str = "wd_dataset_batch_rows"
    mongo_collection_event_rows: str = "wd_dataset_event_rows"
    mongo_collection_monitors: str = "wd_monitors"
    mongo_collection_alerts: str = "wd_alerts"
    mongo_collection_integrations: str = "wd_integrations"

    docs_enabled: bool = True
    is_testing: str = "false"

    cors_origins: List[str] = ["*"]

    def obfuscated_mongodb(self) -> str:
        """Returns configured mongodb url obfuscating the provided password, if any"""
        parsed = urlparse(self.mongo_url)
        if parsed.password:
            return self.mongo_url.replace(parsed.password, "XXXX")
        return self.mongo_url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "WD_"
        fields = {
            "mongo_url": {"env": ["MONGODB_URL", f"{env_prefix}MONGODB_URL"]},
            "redis_url": {"env": ["REDIS_URL", f"{env_prefix}REDIS_URL"]},
            "mongo_database": {
                "env": ["MONGODB_DATABASE", f"{env_prefix}MONGODB_DATABASE"]
            },
            "docs_enabled": {"env": ["DOCS_ENABLED", f"{env_prefix}DOCS_ENABLED"]},
            "cors_origins": {"env": ["CORS_ORIGINS", f"{env_prefix}CORS_ORIGINS"]},
            "is_testing": {"env": ["IS_TESTING", f"{env_prefix}IS_TESTING"]},
        }


settings = ServerSettings()
