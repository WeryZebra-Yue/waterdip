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
from fastapi import APIRouter, Body, Depends
from uuid import UUID
from waterdip.server.apis.models.integrations import AddIntegrationRequest,AddIntegrationResponse
from waterdip.server.services.integration_service import IntegrationService
from typing import Dict,Optional
    
router = APIRouter()


@router.post("/integration.add", response_model=AddIntegrationResponse)
def add_integration(
    request: AddIntegrationRequest = Body(
        ..., description="the request add integration"
    ),
    service: IntegrationService = Depends(IntegrationService.get_instance),
    
):
    return service.add_integration(
        integration = request.integration,
        app_name = request.app_name,
        configuration = request.configuration,
    )
    
@router.post("/integration.delete")
def delete_integration(
    integration_id : UUID = Body(..., description="the model id to delete"),
    service: IntegrationService = Depends(IntegrationService.get_instance),
):
    service.delete_integration(
        integration_id = integration_id,
    )
@router.get("/integration.list")
def list_integration(
    monitor_id: Optional[UUID] = None,
    service: IntegrationService = Depends(IntegrationService.get_instance),
):
    return service.list_integration()

# {
#   "integration": "MONITORING",
#   "app_name": "string",
#   "configuration": {
#     "type": "SLACK",
#     "token": "xoxb-5138958481397-5192933291799-6SMdg9AQKYjRfxUBZkM1dsA0",
#     "channel": "C053RAQLPMM"
#   }
#  }