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

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, root_validator


class Environment(str, Enum):
    """
    Model Dataset Environment
    Attributes:
    ------------------
    TRAINING:
        Training environment
    TESTING:
        Testing environment
    VALIDATION:
        Validation environment
    """

    TRAINING = "TRAINING"
    TESTING = "TESTING"
    VALIDATION = "VALIDATION"
    PRODUCTION = "PRODUCTION"


class MonitorType(str, Enum):
    """
    Monitor types of the model

    Attributes:
    ------------------
    DATA_QUALITY:
        Data quality monitor
    DRIFT:
        Drift monitor
    MODEL_PERFORMANCE:
        Model performance monitor
    """

    DATA_QUALITY = "DATA_QUALITY"
    DRIFT = "DRIFT"
    PERFORMANCE = "PERFORMANCE"


class DriftMetric(str, Enum):
    """
    Drift metrics
    Attributes:
    ------------------
    PSI:
        PSI type drift
    """

    PSI = "PSI"


class DataQualityMetric(str, Enum):
    MISSING_VALUE = "MISSING_VALUE"
    EMPTY_VALUE = "EMPTY_VALUE"
    NEW_VALUE = "NEW_VALUE"


class PerformanceMetric(str, Enum):
    PRECISION = "PRECISION"
    RECALL = "RECALL"
    F1 = "F1"


class TimeRange(BaseModel):
    """
    Attributes:
    ------------------
    start_time:
        start time of the time range
    model_version:
        end time of the time range
    """

    start_time: datetime
    end_time: datetime

    @property
    def get_date_list(self) -> List[str]:
        return [
            (self.start_time + timedelta(days=x)).strftime("%d-%m-%Y")
                for x in range(0, (self.end_time - self.start_time).days + 1)
        ]

class ModelBaselineTimeWindowType(str, Enum):
    """
    Model baseline time window type.
    Attributes:
    ------------------
    MOVING_TIME_WINDOW:
        moving time window
    FIXED_TIME_WINDOW:
        fixed time window
    """

    MOVING_TIME_WINDOW = "MOVING_TIME_WINDOW"
    FIXED_TIME_WINDOW = "FIXED_TIME_WINDOW"


class MovingTimeWindow(BaseModel):
    """
    Fixed time window.

    Attributes:
    ------------------
    skip_period:
       how many days from current day the window starts
    time_period:
       time in days for the moving time window
    """

    skip_period: str = Field(
        default="1d", description="Moving time window skip period. Default is 1d"
    )
    time_period: str = Field(
        default="7d", description="Moving time window time period. Default is 7d"
    )


class FixedTimeWindow(BaseModel):
    """
    Fixed time window.
    Attributes:
    ------------------
    start_time:
        start time of the time window
    end_time:
        end time of the time window
    """

    start_time: datetime = Field(description="start time of the time window")
    end_time: datetime = Field(description="end time of the time window")


class ModelBaselineTimeWindow(BaseModel):
    """
    Model baseline time window.
    Model baseline time window can either be a fixed time window or a moving time window.
    Any one of it is mandatory
    Attributes:
    ------------------
    time_window_type:
        type of the time window
    fixed_time_window:
        fixed time window
    """

    time_window_type: ModelBaselineTimeWindowType = Field(
        description="type of the time window",
        default=ModelBaselineTimeWindowType.MOVING_TIME_WINDOW,
    )
    fixed_time_window: Optional[FixedTimeWindow] = Field(
        default=None, description="fixed time window"
    )
    moving_time_window: Optional[MovingTimeWindow] = Field(
        default=MovingTimeWindow(), description="moving time window"
    )


class ModelBaseline(BaseModel):
    """
    Model baseline.
    Model baseline can either be a batch dataset or a time window.
    Any one of it is mandatory

    Attributes:
    ------------------
    dataset_env:
        the dataset env. If ENV is Testing, then baseline will point to the dataset for this env
    time_window:
        time window for the baseline. Time window can be either FixedTimeWindow or MovingTimeWindow

    """

    dataset_env: Optional[Environment] = Field(
        description="dataset environment", default=None
    )
    time_window: ModelBaselineTimeWindow = Field(
        default=ModelBaselineTimeWindow(), description="time window for the baseline"
    )

    @root_validator
    def any_of(cls, v):
        if not any(v.values()):
            raise ValueError("one of dataset_id or time_window must have a value")
        return v


class Histogram(BaseModel):
    """
    Histogram for a metrics

    Attributes:
    ------------------
    bins:
        bins of the histogram
    val:
        value of the histogram
    """

    bins: List[str]
    val: List[Union[float, int]]


class DateHistogram(BaseModel):
    date_bins: List[datetime]
    val: List[Union[float, int]]


class PredictionTaskType(str, Enum):
    """
    prediction task type for any model version.

    Attributes:
    ------------------
    BINARY:
        Binary Classification
    MULTI_CLASS:
        Multi Class Classification

    """

    BINARY = "BINARY"
    MULTI_CLASS = "MULTICLASS"


class DatasetType(str, Enum):
    """
    dataset type of the datasets associated to model versions

    Attributes:
    ------------------
    BATCH:
        One time uploaded dataset. It is a non-time series dataset
    """

    BATCH = "BATCH"
    EVENT = "EVENT"


class ColumnDataType(str, Enum):
    """
    data type of the dataset

    Attributes:
    ------------------
    NUMERIC:
        numeric data type. It can be integer or float
    CATEGORICAL:
        categorical data type can take on one of a limited,
        and usually fixed, number of possible values
    BOOLEAN:
        boolean data type, i.e. True or False

    """

    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    BOOLEAN = "BOOLEAN"


class ColumnMappingType(str, Enum):
    """
    mapping of column type to model version schema.

    Attributes:
    ------------------
    FEATURE:
        column type is a feature input type
    PREDICTION:
        column type is a prediction output type
    PREDICTION_SCORE:
        column type is a prediction score type
    ACTUAL:
        column type is an actual type. Actual is realized and final output
    ACTUAL_SCORE:
        column type is an actual score.


    """

    FEATURE = "FEATURE"
    PREDICTION = "PREDICTION"
    PREDICTION_SCORE = "PREDICTION_SCORE"
    ACTUAL = "ACTUAL"
    ACTUAL_SCORE = "ACTUAL_SCORE"


class MonitorSeverity(str, Enum):
    """
    severity of the monitor

    Attributes:
    ------------------
    LOW:
        Low severity
    MEDIUM:
        Medium severity
    HIGH:
        High severity
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
class Integration(str, Enum):
    """
        integrations for monitoring and data source

        Attributes:
        ------------------
        DATA_SOURCE:
            Data source
        MONITORING:
            Moinitoring
    """
    DATA_SOURCE = "DATA_SOURCE",
    MONITORING = "MONITORING"

class Integration_Type(str, Enum):
    """
        type of integrations for monitoring

        Attributes:
        ------------------
        SLACK:
            Slack
        TEAMS:
            Microsoft Teams
    """
    SLACK = "SLACK",
    TEAMS = "TEAMS"