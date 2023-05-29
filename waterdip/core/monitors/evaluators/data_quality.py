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

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

from loguru import logger

from waterdip.core.commons.models import TimeRange
from waterdip.core.metrics.data_metrics import (
    CountEmptyHistogram,
    DataMetrics,
    UniqueValueCountHistogram,
)
from waterdip.core.monitors.evaluators.base import MonitorEvaluator
from waterdip.core.monitors.models import DataQualityBaseMonitorCondition


class DataQualityMonitorEvaluator(MonitorEvaluator, ABC):
    """ """

    def __init__(
        self,
        monitor_condition: DataQualityBaseMonitorCondition,
        metrics: Union[List[DataMetrics], DataMetrics],
    ):
        super().__init__(monitor_condition, metrics)

    def _get_columns(self):
        columns = []
        if self.monitor_condition.dimensions.features:
            columns.extend(self.monitor_condition.dimensions.features)
        if self.monitor_condition.dimensions.predictions:
            columns.extend(self.monitor_condition.dimensions.predictions)
        return columns

    def _does_violate_threshold(self, value) -> bool:
        threshold = self.monitor_condition.threshold
        threshold_type, threshold_value = threshold.threshold, threshold.value
        if threshold_type == "gt":
            if value > threshold_value:
                logger.debug(
                    f"Value : [{value}] is greater than threshold : [{threshold_value}]"
                )
                return True
        elif threshold_type == "lt":
            if value < threshold_value:
                logger.debug(
                    f"Value : [{value}] is less than threshold : [{threshold_value}]"
                )
                return True
        return False

    def _get_evaluation_window_timerange(self) -> TimeRange:
        evaluation_window = self.monitor_condition.evaluation_window
        no_of_days, day_unit = evaluation_window[:-1], evaluation_window[-1]

        return TimeRange(
            start_time=datetime.utcnow() - timedelta(days=int(no_of_days)),
            end_time=datetime.utcnow(),
        )

    @abstractmethod
    def _get_metrics(self, **kwargs) -> Dict[str, Any]:
        pass


class EmptyValueEvaluator(DataQualityMonitorEvaluator):
    """ """

    def __init__(
        self,
        monitor_condition: DataQualityBaseMonitorCondition,
        metric: CountEmptyHistogram,
    ):
        super().__init__(monitor_condition, metric)

    def _get_metrics(self, **kwargs) -> Dict[str, Any]:
        evaluation_window = self._get_evaluation_window_timerange()
        return self.metrics.aggregation_result(time_range=evaluation_window)

    def evaluate(self, **kwargs) -> List[Dict]:
        empties = self._get_metrics()
        logger.debug(f"Empties we got : [{empties}]")
        violations: List[Dict] = []
        for col in self._get_columns():
            empty = empties.get(col)
            if empty:
                empty = empty["empty_count"]
                violation = self._does_violate_threshold(empty)
                if violation is True:
                    violations.append(
                        {
                            "metric_value": empty,
                            "threshold": self.monitor_condition.threshold,
                            "dimension": col,
                        }
                    )
        return violations


class NewValueEvaluator(DataQualityMonitorEvaluator):
    def __init__(
        self,
        monitor_condition: DataQualityBaseMonitorCondition,
        metrics: List[UniqueValueCountHistogram],
    ):
        super().__init__(monitor_condition, metrics)

    def _get_metrics(self, **kwargs) -> Dict[str, Any]:
        evaluation_window = self._get_evaluation_window_timerange()
        return (
            self.metrics["baseline_metric"].aggregation_result(
                time_range=evaluation_window
            ),
            self.metrics["production_metric"].aggregation_result(
                time_range=evaluation_window
            ),
        )

    def evaluate(self, **kwargs):
        baseline, production = self._get_metrics()
        violations: List[Dict] = []
        for col in self._get_columns():
            baseline_count = baseline.get(col)
            production_count = production.get(col)
            if baseline_count and production_count:
                violation = self._does_violate_threshold(
                    abs(production_count - baseline_count)
                )
                if violation is True:
                    violations.append(
                        {
                            "metric_value": abs(production_count - baseline_count),
                            "threshold": self.monitor_condition.threshold,
                            "dimension": col,
                        }
                    )
        return violations


class MissingValueEvaluator(DataQualityMonitorEvaluator):
    def __init__(
        self,
        monitor_condition: DataQualityBaseMonitorCondition,
        metrics: List[UniqueValueCountHistogram],
    ):
        super().__init__(monitor_condition, metrics)

    def _get_metrics(self, **kwargs) -> Dict[str, Any]:
        evaluation_window = self._get_evaluation_window_timerange()
        return (
            self.metrics["baseline_metric"].aggregation_result(
                time_range=evaluation_window
            ),
            self.metrics["production_metric"].aggregation_result(
                time_range=evaluation_window
            ),
        )

    def evaluate(self, **kwargs):
        baseline, production = self._get_metrics()
        violations: List[Dict] = []
        for col in self._get_columns():
            baseline_count = baseline.get(col)
            production_count = production.get(col)
            if baseline_count and production_count:
                violation = self._does_violate_threshold(
                    abs(baseline_count - production_count)
                )
                if violation is True:
                    violations.append(
                        {
                            "metric_value": abs(baseline_count - production_count),
                            "threshold": self.monitor_condition.threshold,
                            "dimension": col,
                        }
                    )
        return violations
