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
from typing import Optional, TypeVar

from waterdip.core.commons.models import MonitorSeverity, MonitorType
from waterdip.core.monitors.models import BaseMonitorCondition

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from uuid import UUID

from pydantic import BaseModel, Field


class MonitorIdentification(BaseModel):
    model_version_id: UUID = Field(description="")
    model_id: UUID = Field(description="...")


class BaseMonitorDB(BaseModel):
    monitor_id: UUID = Field(...)
    monitor_name: str = Field(...)
    monitor_identification: MonitorIdentification = Field(...)
    monitor_type: MonitorType = Field(
        description="Monitor types can be data_drift | prediction_drift"
    )
    monitor_condition: BaseMonitorCondition = Field(...)
    count_of_alerts: Optional[int]
    model_name: Optional[str]
    last_run: Optional[datetime]
    created_at: datetime
    severity: MonitorSeverity = Field(default=MonitorSeverity.LOW)
    integration_id: Optional[UUID]

    def dict(self, *args, **kwargs) -> "DictStrAny":
        monitor = super().dict(*args, **kwargs)
        monitor["monitor_id"] = str(monitor["monitor_id"])
        monitor["monitor_identification"]["model_version_id"] = str(
            monitor["monitor_identification"]["model_version_id"]
        )
        monitor["monitor_identification"]["model_id"] = str(
            monitor["monitor_identification"]["model_id"]
        )
        if monitor.get("integration_id"):
            monitor["integration_id"] = str(monitor["integration_id"])

        return monitor


MonitorDB = TypeVar("MonitorDB", bound=BaseMonitorDB)
