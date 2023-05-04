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
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends
from pydantic import Field

from waterdip.core.commons.models import MonitorSeverity, MonitorType
from waterdip.core.monitors.models import (
    DataQualityBaseMonitorCondition,
    DriftBaseMonitorCondition,
    PerformanceBaseMonitorCondition,
)
from waterdip.server.apis.models.params import RequestPagination, RequestSort
from waterdip.server.db.models.monitors import (
    BaseMonitorCondition,
    BaseMonitorDB,
    MonitorDB,
    MonitorIdentification,
)
from waterdip.server.db.repositories.monitor_repository import MonitorRepository
from waterdip.server.services.alert_service import AlertService
from waterdip.server.services.model_service import ModelService, ModelVersionService


class ServiceBaseMonitor(BaseMonitorDB):
    pass


class ServiceDataQualityMonitor(ServiceBaseMonitor):
    monitor_type: MonitorType = Field(default=MonitorType.DATA_QUALITY, const=True)
    monitor_condition: DataQualityBaseMonitorCondition = Field(...)


class ServicePerformanceMonitor(ServiceBaseMonitor):
    monitor_type: MonitorType = Field(default=MonitorType.PERFORMANCE, const=True)
    monitor_condition: PerformanceBaseMonitorCondition = Field(...)


class ServiceDriftMonitor(ServiceBaseMonitor):
    monitor_type: MonitorType = Field(default=MonitorType.DRIFT, const=True)
    monitor_condition: DriftBaseMonitorCondition = Field(...)


class MonitorService:
    _INSTANCE: "MonitorService" = None

    @classmethod
    def get_instance(
        cls,
        repository: MonitorRepository = Depends(MonitorRepository.get_instance),
        model_service: ModelService = Depends(ModelService.get_instance),
        model_version_service: ModelVersionService = Depends(
            ModelVersionService.get_instance
        ),
        alert_service: AlertService = Depends(AlertService.get_instance),
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(
                repository=repository,
                model_service=model_service,
                model_version_service=model_version_service,
                alert_service=alert_service,
            )
        return cls._INSTANCE

    def __init__(
        self,
        repository: MonitorRepository,
        model_service: ModelService,
        model_version_service: ModelVersionService,
        alert_service: AlertService,
    ):
        self._repository = repository
        self.model_service = model_service
        self.model_version_service = model_version_service
        self.alert_service = alert_service

    def _check_monitor_identification(
        self, monitor_identification: MonitorIdentification
    ):
        """
        Constrain check for model creation. This will check the
        existence of model_id and model_version_id associated with the monitor
        """
        self.model_version_service.find_by_id(
            model_version_id=monitor_identification.model_version_id
        )
        self.model_service.find_by_id(model_id=monitor_identification.model_id)

    def create_data_quality_monitor(
        self,
        monitor_name: str,
        identification: MonitorIdentification,
        condition: BaseMonitorCondition,
        severity: MonitorSeverity,
        integration_id: Optional[List[UUID]] = None,
    ) -> ServiceBaseMonitor:
        self._check_monitor_identification(identification)

        monitor_id = uuid.uuid4()

        service_quality_monitor = ServiceDataQualityMonitor(
            monitor_id=monitor_id,
            monitor_name=monitor_name,
            monitor_identification=identification,
            monitor_condition=DataQualityBaseMonitorCondition(
                evaluation_metric=condition.evaluation_metric,
                dimensions=condition.dimensions,
                threshold=condition.threshold,
                evaluation_window=condition.evaluation_window,
                skip_period=condition.skip_period,
            ),
            severity=severity,
            created_at=datetime.utcnow(),
            integration_id=integration_id,
        )

        return self._repository.insert_monitor(monitor=service_quality_monitor)

    def create_model_performance_monitor(
        self,
        monitor_name: str,
        identification: MonitorIdentification,
        condition: BaseMonitorCondition,
        severity: MonitorSeverity,
        integration_id: Optional[List[UUID]] = None,
    ) -> ServiceBaseMonitor:
        self._check_monitor_identification(identification)

        monitor_id = uuid.uuid4()

        service_perf_monitor = ServicePerformanceMonitor(
            monitor_id=monitor_id,
            monitor_name=monitor_name,
            monitor_identification=identification,
            monitor_condition=PerformanceBaseMonitorCondition(
                evaluation_metric=condition.evaluation_metric,
                threshold=condition.threshold,
                evaluation_window=condition.evaluation_window,
                skip_period=condition.skip_period,
            ),
            created_at=datetime.utcnow(),
            severity=severity,
            integration_id=integration_id,
        )

        return self._repository.insert_monitor(monitor=service_perf_monitor)

    def create_drift_monitor(
        self,
        monitor_name: str,
        identification: MonitorIdentification,
        condition: BaseMonitorCondition,
        severity: MonitorSeverity,
        integration_id: Optional[List[UUID]] = None,
    ) -> ServiceBaseMonitor:
        self._check_monitor_identification(identification)

        monitor_id = uuid.uuid4()

        service_drift_monitor = ServiceDriftMonitor(
            monitor_id=monitor_id,
            monitor_name=monitor_name,
            monitor_identification=identification,
            monitor_condition=DriftBaseMonitorCondition(
                evaluation_metric=condition.evaluation_metric,
                dimensions=condition.dimensions,
                threshold=condition.threshold,
                baseline=condition.baseline,
                evaluation_window=condition.evaluation_window,
                skip_period=condition.skip_period,
            ),
            created_at=datetime.utcnow(),
            severity=severity,
            integration_id=integration_id,
        )

        return self._repository.insert_monitor(monitor=service_drift_monitor)

    def delete_monitor(self, monitor_id: UUID):
        return self._repository.delete_monitor(monitor_id=monitor_id)

    def list_monitors(
        self,
        sort_request: Optional[RequestSort] = None,
        pagination: Optional[RequestPagination] = None,
        model_id: Optional[UUID] = None,
        model_version_id: Optional[UUID] = None,
    ) -> List[MonitorDB]:
        filters = {}
        if model_id:
            filters["monitor_identification.model_id"] = str(model_id)
        if model_version_id:
            filters["monitor_identification.model_version_id"] = str(model_version_id)

        monitors = self._repository.find_monitors(
            filters=filters,
            sort=[(sort_request.get_sort_field, sort_request.get_sort_order)]
            if sort_request and sort_request.sort
            else [("created_at", -1)],
            skip=(pagination.page - 1) * pagination.limit if pagination else 0,
            limit=pagination.limit if pagination else 10,
        )
        for monitor in monitors:
            monitor.count_of_alerts = self.alert_service.count_alerts(
                {"model_id": str(monitor.monitor_identification.model_id)}
            )
            monitor.model_name = self.model_service.find_by_id(
                model_id=monitor.monitor_identification.model_id
            ).model_name
        return monitors

    def count_monitors(self) -> int:
        return self._repository.count_monitors(filters={})

    def delete_monitors_by_model_id(self, model_id: UUID):
        self._repository.delete_monitors_by_model_id(model_id=model_id)
