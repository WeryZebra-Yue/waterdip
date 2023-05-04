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
from typing import Type, Union

from starlette import status


class WDServerError(Exception):
    HTTP_STATUS: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def api_documentation(cls):
        return {
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "code": cls.get_error_code(),
                            "params": {"extra": "error parameters"},
                        }
                    }
                }
            },
        }

    @classmethod
    def get_error_code(cls):
        return f"waterdip.api.errors::{cls.__name__}"

    @property
    def code(self) -> str:
        return self.get_error_code()

    @property
    def arguments(self):
        return (
            {k: v for k, v in vars(self).items() if v is not None}
            if vars(self)
            else None
        )

    def __str__(self):
        args = self.arguments or {}
        printable_args = ",".join([f"{k}={v}" for k, v in args.items()])
        return f"{self.code}({printable_args})"


class EntityNotFoundError(WDServerError):
    """Error raised when entity not found"""

    HTTP_STATUS = status.HTTP_404_NOT_FOUND

    def __init__(self, name: str, type: Union[Type, str], message: str = None):
        self.name = name
        self.type = type if isinstance(type, str) else type.__name__
        self.message = message

class EntityAlreadyExistsError(WDServerError):
    """ Error raised when entity already exists """
    
    HTTP_STATUS = status.HTTP_409_CONFLICT

    def __init__(self, name: str,  message: str = None):
        self.name = name
        self.message = message
        
class IntegrationError(WDServerError):
    """Error raised when integration fails"""

    HTTP_STATUS = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, name: str, message: str = None):
        self.name = name
        self.message = message