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
from typing import Dict
from uuid import UUID

from pydantic import BaseModel

from waterdip.core.commons.models import Integration


class AddIntegrationRequest(BaseModel):
    """
    Schema of Add Integration Request:
    Attributes:
    ------------------
    integration : Integration
        Integration type
    app_name : str
        Name of the app
    configuration : Dict
        Configuration of the integration
    """

    integration: Integration
    app_name: str
    configuration: Dict


class AddIntegrationResponse(BaseModel):
    """
    Schema of Add Integration Response:
    Attributes:
    ------------------
    integration_id : UUID
        Integration ID
    integration : Integration
        Integration type
    app_name : str
        Name of the app
    configuration : Dict
        Configuration of the integration
    """

    integration_id: UUID
    integration: Integration
    app_name: str
    configuration: Dict
