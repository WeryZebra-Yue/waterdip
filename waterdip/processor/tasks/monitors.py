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

from loguru import logger

from waterdip.processor.app import celery_app
from waterdip.processor.monitors.monitor_processor import MonitorProcessor
from waterdip.server.db.models.monitors import MonitorDB
from waterdip.server.db.mongodb import MongodbBackend
from waterdip.server.db.repositories.alert_repository import AlertRepository
from waterdip.server.db.repositories.dataset_repository import DatasetRepository
from waterdip.server.db.repositories.monitor_repository import MonitorRepository
from waterdip.server.db.repositories.integration_repository import IntegrationRepository
from waterdip.server.services.integration_service import IntegrationService


@celery_app.task(name="process_monitor", bind=True)
def process_monitor(self, monitor):
    """
    Process a single incoming monitor data using MonitorProcessor
    """
    logger.info(f"Starting processing monitor job: [{monitor}]")
    mongo_backend = MongodbBackend.get_instance()

    processor = MonitorProcessor(
        monitor=monitor,
        mongodb_backend=mongo_backend,
        alert_repo=AlertRepository.get_instance(mongodb=mongo_backend),
        dataset_repo=DatasetRepository.get_instance(mongodb=mongo_backend),
        integration_service=IntegrationService.get_instance(
            repository=IntegrationRepository.get_instance(mongodb=mongo_backend)
        )
    )
    processor.process()


@celery_app.task(name="create_process_monitor_jobs", bind=True)
def generate_monitor_jobs(self):
    """
    Gets all the monitors from the datastore.
    and sends all the monitors to queue to process. process_monitor will pick one monitor at a time to process
    """
    monitor_repo = MonitorRepository.get_instance(mongodb=MongodbBackend.get_instance())
    monitors: List[MonitorDB] = monitor_repo.find_monitors(filters={}, limit=0)
    for monitor in monitors:
        logger.info(f"Generating monitor job: [{monitor.monitor_name}]")
        process_monitor.apply_async(kwargs={"monitor": monitor.dict()})
