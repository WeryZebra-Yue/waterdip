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

from typing import Dict, List
from uuid import UUID, uuid4

from fastapi import Depends
from waterdip.server.db.repositories.integration_repository import IntegrationRepository
from waterdip.server.db.models.integrations import BaseIntegrationDB
from waterdip.core.commons.models import Integration,Integration_Type
from waterdip.server.errors.base_errors import IntegrationError
from waterdip.server.db.models.alerts import BaseAlertDB
from waterdip.server.db.models.monitors import BaseMonitorCondition
from slack_sdk import WebClient

class IntegrationService:
    _INSTANCE: "IntegrationService" = None

    @classmethod
    def get_instance(
        cls, repository: IntegrationRepository = Depends(IntegrationRepository.get_instance)
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(repository=repository)
        return cls._INSTANCE

    def __init__(
        self,
        repository: IntegrationRepository,
    ):
        self._repository = repository
    def add_integration(self,
        integration: Integration,
        app_name: str,
        configuration: Dict,
    ) :
        """
        Insert a add integration into the database
        """
        integration = BaseIntegrationDB(
            integration_id=uuid4(),
            integration=integration,
            app_name=app_name,
            configuration=configuration,
        )
        if integration.integration == Integration.MONITORING:
            if integration.configuration["type"] == Integration_Type.SLACK:
                self.send_message_to_slack(
                    message="Hello from your app! :tada:",
                    channel=integration.configuration["channel"],
                    token=integration.configuration["token"],
                )
            else:
                raise NotImplementedError()
        return self._repository.add_integration(
            integration=integration
        )
    def delete_integration(self, integration_id: UUID):
        """
        Delete a integration from the database
        """
        return self._repository.delete_integration(integration_id=str(integration_id))
    
    def list_integration(self):
        """
        List a integration from the database
        """
        return self._repository.list_integration()

    def send_message_to_slack(self, message: str, channel: str, token: str):
        """
        Send message to slack
        """
        slack_client = WebClient(token=token)
        try:
            response = slack_client.chat_postMessage(
                channel=channel,
                text=message,
            ) 
        except Exception as e:
            raise IntegrationError(name=Integration_Type.SLACK,  message=str(e))
    def get_integration(self, integration_id: UUID):
        """
        Get a integration from the database
        """
        return self._repository.get_integration(integration_id=str(integration_id))
    def send_alert(self, alert : BaseAlertDB, monitor_condition : BaseMonitorCondition, integration_id: UUID):
        integration = self.get_integration(integration_id=integration_id)
        if integration.configuration["type"] == Integration_Type.SLACK:
            self.send_message_to_slack(
                message=self.alert_description(alert=alert, monitor_condition=monitor_condition),
                channel=integration.configuration["channel"],
                token=integration.configuration["token"],
            )

    def alert_description(self, alert : BaseAlertDB, monitor_condition : BaseMonitorCondition):
        if monitor_condition.evaluation_metric.EMPTY_VALUE == monitor_condition.evaluation_metric.EMPTY_VALUE:
            field = alert.violation["field"]
            focal_value = alert.violation["focal_value"]
            focal_time_period = alert.violation["focal_time_window"]
            model = alert.model_id
            model_version = alert.violation["model_version_id"]
            max_threshold = alert.violation["max_threshold"]
            
            return f"""An anomaly in the ratio of missing values of feature *{field}*.\nThe anomaly was observed in the *{model}* model, in version *{model_version}* for the *last {focal_time_period} *.\nBased on defined limits, the missing ratio was expected to be below *{max_threshold}*, but *{focal_value}* was received.\nMissing data can have a significant effect on model behavior and may lead to unexpected results.\nMissing data might occur because: \n- Serving environment fault\n- Data store / provider schema changes\n- Changes in internal API\n- Changes in model subject input"""
        else:
            raise NotImplementedError()