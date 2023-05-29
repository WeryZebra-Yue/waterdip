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

import datetime
import uuid

import pytest

from waterdip.core.commons.models import (
    DataQualityMetric,
    DatasetType,
    Environment,
    MonitorSeverity,
    MonitorType,
)
from waterdip.core.monitors.models import MonitorDimensions, MonitorThreshold
from waterdip.processor.monitors.monitor_processor import MonitorProcessor
from waterdip.server.db.models.datasets import BaseDatasetDB
from waterdip.server.db.models.monitors import (
    BaseMonitorCondition,
    BaseMonitorDB,
    MonitorIdentification,
)
from waterdip.server.db.mongodb import MongodbBackend
from waterdip.server.db.repositories.alert_repository import AlertRepository
from waterdip.server.db.repositories.dataset_repository import DatasetRepository
from waterdip.server.db.repositories.integration_repository import IntegrationRepository
from waterdip.server.services.integration_service import IntegrationService


@pytest.mark.usefixtures("mock_mongo_backend")
class TestMonitorProcessor:
    def test_should_process_data_quality_monitor(
        self, mocker, mock_mongo_backend: MongodbBackend
    ):
        mocker.patch(
            "waterdip.processor.monitors.monitor_processor.MonitorProcessor._get_event_dataset",
            return_value=[
                BaseDatasetDB(
                    dataset_id=uuid.uuid4(),
                    dataset_name="name",
                    environment=Environment.PRODUCTION,
                    created_at=datetime.datetime.now(),
                    dataset_type=DatasetType.EVENT,
                    model_id=uuid.uuid4(),
                    model_version_id=uuid.uuid4(),
                )
            ],
        )
        mocker.patch(
            "waterdip.core.metrics.data_metrics.CountEmptyHistogram.aggregation_result",
            return_value={
                "f1": {"empty_count": 11, "empty_percentage": 1.1, "total_count": 1000}
            },
        )
        condition = BaseMonitorCondition(
            threshold=MonitorThreshold(threshold="gt", value=10),
            evaluation_metric=DataQualityMetric.EMPTY_VALUE,
            dimensions=MonitorDimensions(features=["f1", "f2"]),
        )
        monitor_db = BaseMonitorDB(
            monitor_id=uuid.uuid4(),
            monitor_name="M1",
            monitor_identification=MonitorIdentification(
                model_id=uuid.uuid4(), model_version_id=uuid.uuid4()
            ),
            monitor_type=MonitorType.DATA_QUALITY,
            monitor_condition=condition,
            created_at="2021-08-01T00:00:00Z",
            last_run="2021-08-01T00:00:00Z",
            severity="LOW",
        )

        monitor_processor = MonitorProcessor(
            monitor=monitor_db.dict(),
            mongodb_backend=mock_mongo_backend,
            alert_repo=AlertRepository.get_instance(mongodb=mock_mongo_backend),
            dataset_repo=DatasetRepository.get_instance(mongodb=mock_mongo_backend),
            integration_service=IntegrationService.get_instance(
                repository=IntegrationRepository.get_instance(
                    mongodb=mock_mongo_backend
                )
            ),
        )
        violation = monitor_processor.process()
        assert len(violation) == 1
