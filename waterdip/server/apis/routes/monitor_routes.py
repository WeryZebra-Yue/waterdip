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

from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from waterdip.core.commons.models import MonitorType
from waterdip.server.apis.models.monitors import (
    CreateMonitorRequest,
    CreateMonitorResponse,
    MonitorListResponse,
)
from waterdip.server.apis.models.params import RequestPagination, RequestSort
from waterdip.server.services.monitor_service import MonitorService

router = APIRouter()


@router.post(
    "/monitor.create", response_model=CreateMonitorResponse, name="monitor:create"
)
def create_monitor(
    request: CreateMonitorRequest = Body(
        ..., description="the request model register info"
    ),
    service: MonitorService = Depends(MonitorService.get_instance),
):
    monitor_type: MonitorType = request.monitor_type

    if monitor_type == MonitorType.DATA_QUALITY:
        return service.create_data_quality_monitor(
            monitor_name=request.monitor_name,
            identification=request.monitor_identification,
            condition=request.monitor_condition,
            severity=request.severity,
            integration_id=request.integration_id,
        )
    elif monitor_type == MonitorType.PERFORMANCE:
        return service.create_model_performance_monitor(
            monitor_name=request.monitor_name,
            identification=request.monitor_identification,
            condition=request.monitor_condition,
            severity=request.severity,
            integration_id=request.integration_id,
        )
    elif monitor_type == MonitorType.DRIFT:
        return service.create_drift_monitor(
            monitor_name=request.monitor_name,
            identification=request.monitor_identification,
            condition=request.monitor_condition,
            severity=request.severity,
            integration_id=request.integration_id,
        )


@router.post("/monitor.delete", name="monitor:delete")
def delete_monitor(
    monitor_id: UUID = Body(..., description="the monitor id"),
    service: MonitorService = Depends(MonitorService.get_instance),
):
    return service.delete_monitor(monitor_id)


@router.get("/list.monitors", response_model=MonitorListResponse, name="list:monitor")
def list_monitor(
    pagination: RequestPagination = Depends(),
    sort: RequestSort = Depends(),
    service: MonitorService = Depends(MonitorService.get_instance),
    model_id: Optional[UUID] = None,
    model_version_id: Optional[UUID] = None,
):
    list_monitors = service.list_monitors(
        sort_request=sort,
        pagination=pagination,
        model_id=model_id,
        model_version_id=model_version_id,
    )
    response = MonitorListResponse(
        monitor_list=list_monitors,
        meta={
            "page": pagination.page,
            "limit": pagination.limit,
            "total": service.count_monitors(),
        },
    )
    return response
