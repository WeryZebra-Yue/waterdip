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

from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from waterdip.core.commons.models import MonitorSeverity, MonitorType
from waterdip.core.monitors.models import MonitorCondition
from waterdip.server.db.models.monitors import (
    BaseMonitorCondition,
    MonitorIdentification,
)
from waterdip.server.services.monitor_service import ServiceBaseMonitor


class CreateMonitorRequest(BaseModel):
    """
    Create monitor API request
    Attributes:
    ------------------
    monitor_name:
        name of the monitor
    monitor_identification:
        identification
    monitor_type:
        monitor types
    monitor_condition:
        conditions
    """

    monitor_name: str
    monitor_identification: MonitorIdentification
    monitor_type: MonitorType
    monitor_condition: BaseMonitorCondition
    severity: MonitorSeverity
    integration_id: Optional[UUID]


class CreateMonitorResponse(ServiceBaseMonitor):
    pass


class MonitorListRow(BaseModel):
    """
    Monitor list row
    Attributes:
    ------------------
    monitor_id:
        id of the monitor
    monitor_name:
        name of the monitor
    monitor_type:
        monitor types
    monitor_identification:
        identification
    monitor_condition:
        conditions

    """

    monitor_id: UUID
    monitor_name: str
    monitor_type: MonitorType
    monitor_identification: MonitorIdentification
    monitor_condition: MonitorCondition
    count_of_alerts: int
    model_name: str
    last_run: Optional[datetime]
    created_at: datetime
    severity: MonitorSeverity
    integration_id: Optional[UUID]


class MonitorListResponse(BaseModel):
    monitor_list: List[MonitorListRow]
    meta: Optional[Dict[str, Union[str, int]]]
