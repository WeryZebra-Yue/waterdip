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
from abc import ABC
from datetime import timedelta
from typing import Any, Dict, List
from uuid import UUID

from pymongo.collection import Collection

from waterdip.core.commons.models import TimeRange
from waterdip.core.metrics.base import MongoMetric


class DataMetrics(MongoMetric, ABC):
    """
    Attributes:
    -----
    collection: Collection
        mongo collection
    dataset_id: UUID
        dataset id on which the metric calculation will be applied

    """

    def __init__(self, collection: Collection, dataset_id: UUID):
        super().__init__(collection)
        self._dataset_id = dataset_id


class CategoricalCountHistogram(DataMetrics):
    """
    The categorical histogram feature measures count of each categorical column.

    ...

    Methods:
    --------
    aggregation_result()
        returns count aggregation by categorical column names

    Examples:
        >>> from waterdip.core.metrics.data_metrics import CategoricalCountHistogram
        >>> DATASET_BATCH_ID_V2_3 = UUID("1d195bf6-7a1f-4a33-b7b1-37a603aadd33")
        >>> mongo_collection: Collection
        >>>
        >>> hist = CategoricalCountHistogram(
        >>>     collection=mongo_collection,
        >>>     dataset_id=DATASET_BATCH_ID_V2_3,
        >>> )
        >>> hist_result = hist.aggregation_result() # returns histogram result
        >>> # res structure -> { "column_name": { "bins": ["<bin1>"], "count": ["<bin1_count>"] } }
    """

    @property
    def metric_name(self) -> str:
        return "categorical_count_hist"

    def aggregation_result(
        self, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Dict]:
        hist = {}
        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range), kwargs=kwargs
        )

        for doc in self._collection.aggregate(agg_query):
            column_name = doc["_id"]["column_name"]
            column_value = doc["_id"]["column_value"]
            count = doc["count"]
            if column_name not in hist:
                hist[column_name] = {"bins": [], "count": []}
            hist[column_name]["bins"].append(column_value)
            hist[column_name]["count"].append(count)
        return hist

    def _aggregation_query(
        self, time_filter: Dict = None, **kwargs
    ) -> List[Dict[str, Any]]:
        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {"$unwind": "$columns"},
            {
                "$match": {
                    "columns.data_type": "CATEGORICAL",
                    "columns.value_categorical": {"$ne": None},
                }
            },
            {
                "$group": {
                    "_id": {
                        "column_name": "$columns.name",
                        "column_value": "$columns.value_categorical",
                    },
                    "count": {"$sum": 1},
                }
            },
        ]


class CategoricalNestedDateCountHistogram(DataMetrics):
    """
    The categorical nested date count histogram feature
    measures count of each categorical column for every date

    ...

    Methods:
    --------
    aggregation_result()
        returns count aggregation by categorical column names

    Examples:
        >>> from waterdip.core.metrics.data_metrics import CategoricalNestedDateCountHistogram
        >>> DATASET_BATCH_ID_V2_3 = UUID("1d195bf6-7a1f-4a33-b7b1-37a603aadd33")
        >>> mongo_collection: Collection
        >>>
        >>> hist = CategoricalNestedDateCountHistogram(
        >>>     collection=mongo_collection,
        >>>     dataset_id=DATASET_BATCH_ID_V2_3,
        >>> )
        >>> hist_result = hist.aggregation_result() # returns histogram result
        >>> # result structure ->
        >>> # {
        >>> #   "01-01-2023": {"column_name": { "bins": ["<bin1>"], "count": ["<bin1_count>"] } }
        >>> #   "02-01-2023": {"column_name": { "bins": ["<bin1>"], "count": ["<bin1_count>"] } }
        >>> # }
    """

    @property
    def metric_name(self) -> str:
        return "categorical_count_date_hist"

    def aggregation_result(
        self, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Dict]:
        hist = {}
        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range), kwargs=kwargs
        )

        for doc in self._collection.aggregate(agg_query):
            date_str = doc["_id"]["date_str"]
            column_name = doc["_id"]["column_name"]
            column_value = doc["_id"]["column_value"]
            count = doc["count"]
            if date_str not in hist:
                hist[date_str] = {}
            if column_name not in hist[date_str]:
                hist[date_str][column_name] = {"bins": [], "count": []}
            hist[date_str][column_name]["bins"].append(column_value)
            hist[date_str][column_name]["count"].append(count)
        return hist

    def _aggregation_query(
        self, time_filter: Dict = None, **kwargs
    ) -> List[Dict[str, Any]]:
        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {
                "$addFields": {
                    "date_str": {
                        "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                    }
                }
            },
            {"$unwind": "$columns"},
            {
                "$match": {
                    "columns.data_type": "CATEGORICAL",
                    "columns.value_categorical": {"$ne": None},
                }
            },
            {
                "$group": {
                    "_id": {
                        "date_str": "$date_str",
                        "column_name": "$columns.name",
                        "column_value": "$columns.value_categorical",
                    },
                    "count": {"$sum": 1},
                }
            },
        ]


class NumericNestedCountDateHistogram(DataMetrics):
    """
    The numeric nested date count histogram feature
    measures count of each numeric column for every date

    ...
    Methods:
    --------
    aggregation_result()
        returns count aggregation by numeric column names

    Examples:
        >>> from waterdip.core.metrics.data_metrics import NumericNestedCountDateHistogram
        >>> DATASET_EVENT_ID_V2_3 = UUID("1d195bf6-7a1f-4a33-b7b1-37a603aadd33")
        >>> mongo_collection: Collection
        >>>
        >>> hist = NumericNestedCountDateHistogram(
        >>>     collection=mongo_collection,
        >>>     dataset_id=DATASET_EVENT_ID_V2_3,
        >>> )
        >>> hist_result = hist.aggregation_result() # returns histogram result
        >>> # result structure ->
        >>> # {
        >>> #   "01-01-2023": {"column_name": { "bins": ["<bin1>"], "count": ["<bin1_count>"] } }
        >>> #   "02-01-2023": {"column_name": { "bins": ["<bin1>"], "count": ["<bin1_count>"] } }
        >>> # }

    """

    @property
    def metric_name(self) -> str:
        return "numeric_count_date_hist"

    @staticmethod
    def _facet_to_date_agg(facets: Dict) -> Dict:
        """
        Converts facet result to date aggregation
        Args:
            facets: facets result from mongodb aggregation

        Returns:
            date aggregation

        Examples:
            >>> facets = {
            >>>     "01-01-2023:lead_time": [
            >>>       {"_id": {}, "count": 1},
            >>>       {"_id": {}, "count": 2},
            >>>       {"_id": {}, "count": 3},
            >>>     ],
            >>>     "01-01-2023:lead_time_2": [
            >>>       {"_id": {}, "count": 1},
            >>>       {"_id": {}, "count": 2},
            >>>       {"_id": {}, "count": 3},
            >>>     ],
            >>> }
            >>> NumericNestedCountDateHistogram._facet_to_date_agg(facets)
            >>> # returns
            >>> # {
            >>> #   "01-01-2023": {
            >>> #       "lead_time":  [{"_id": {}, "count": 1}, {"_id": {}, "count": 2}, {"_id": {}, "count": 3}],]
            >>> #       "lead_time_2": [{"_id": {}, "count": 1}, {"_id": {}, "count": 2}, {"_id": {}, "count": 3}],]
            >>> #   }
        """
        agg = {}
        for facet_key in facets.keys():
            splits = facet_key.split(":")
            date_str, numeric_column = splits[0], splits[1]
            if date_str not in agg:
                agg[date_str] = {}
            agg[date_str][numeric_column] = facets[facet_key]
        return agg

    def _get_mongo_response(self, query: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._collection.aggregate(query).next()

    def aggregation_result(
        self, numeric_columns: List, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Any]:
        hist: Dict[str, Dict] = {}

        agg_query = self._aggregation_query(
            numeric_columns=numeric_columns,
            time_filter=self._time_filter_builder(time_range=time_range),
            date_list=time_range.get_date_list,
            kwargs=kwargs,
        )
        facets_response = self._get_mongo_response(query=agg_query)

        facets_date_agg: Dict[str, Dict] = self._facet_to_date_agg(
            facets=facets_response
        )

        for agg_date, facets_agg_value in facets_date_agg.items():
            hist[agg_date] = {}
            for numeric_column in facets_agg_value.keys():
                hist[agg_date][numeric_column] = {}
                nbins, count = [], []
                for k, doc in enumerate(facets_agg_value[numeric_column]):
                    count.append(doc["count"])
                    lower_limit = 0 if not doc["_id"]["min"] else doc["_id"]["min"]
                    nbins.append(lower_limit)
                    if k == len(facets_agg_value[numeric_column]) - 1:
                        nbins[k] = doc["_id"]["max"]

                hist[agg_date][numeric_column]["bins"] = nbins
                hist[agg_date][numeric_column]["count"] = count

        return hist

    def _aggregation_query(
        self,
        numeric_columns: List[str],
        date_list: List[str],
        time_filter: Dict = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        facet_query = {}
        bins: Dict[str, List[str]] = kwargs.get("bins", None)

        for date_str in date_list:
            for column in numeric_columns:
                query = [{"$match": {"columns.name": column, "date_str": date_str}}]
                if bins is None:
                    query.append(
                        {
                            "$bucketAuto": {
                                "groupBy": "$columns.value_numeric",
                                "buckets": 9,
                            }
                        }
                    )
                else:
                    query.append(
                        {
                            "$bucket": {
                                "groupBy": "$columns.value_numeric",
                                "boundaries": bins[column],
                                "default": bins[column][-1],
                            }
                        }
                    )
                facet_query[f"{date_str}:{column}"] = query

        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {
                "$addFields": {
                    "date_str": {
                        "$dateToString": {"format": "%d-%m-%Y", "date": "$created_at"}
                    }
                }
            },
            {"$unwind": "$columns"},
            {"$match": {"columns.data_type": "NUMERIC"}},
            {"$facet": facet_query},
        ]


class NumericCountHistogram(DataMetrics):
    @property
    def metric_name(self) -> str:
        return "numeric_count_hist"

    def aggregation_result(
        self, numeric_columns: List, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Any]:
        hist: Dict[str, Any] = {}

        agg_query = self._aggregation_query(
            numeric_columns=numeric_columns,
            time_filter=self._time_filter_builder(time_range=time_range),
            kwargs=kwargs,
        )
        facets = self._collection.aggregate(agg_query).next()
        for numeric_column in facets:
            hist[numeric_column] = {}
            nbins = []
            count = []
            for k, doc in enumerate(facets[numeric_column]):
                count.append(doc["count"])
                lower_limit = 0 if not doc["_id"]["min"] else doc["_id"]["min"]
                nbins.append(lower_limit)
                if k == len(facets[numeric_column]) - 1:
                    nbins[k] = doc["_id"]["max"]

            hist[numeric_column]["bins"] = nbins
            hist[numeric_column]["count"] = count
        return hist

    def _aggregation_query(
        self, numeric_columns: List, time_filter: Dict = None, **kwargs
    ) -> List[Dict[str, Any]]:
        facet_query = {}
        bins: Dict[str, List[str]] = kwargs.get("bins", None)

        if bins is None:
            for column in numeric_columns:
                facet_query[column] = [
                    {"$match": {"columns.name": column}},
                    {
                        "$bucketAuto": {
                            "groupBy": "$columns.value_numeric",
                            "buckets": 9,
                        }
                    },
                ]
        else:
            for column in numeric_columns:
                facet_query[column] = [
                    {"$match": {"columns.name": column}},
                    {
                        "$bucket": {
                            "groupBy": "$columns.value_numeric",
                            "boundaries": bins[column],
                            "default": bins[column][-1],
                        }
                    },
                ]

        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {"$unwind": "$columns"},
            {"$match": {"columns.data_type": "NUMERIC"}},
            {"$facet": facet_query},
        ]


class CountEmptyHistogram(DataMetrics):
    """
    The count empty feature measures count of each empty column.

    ...

    Methods:
    --------
    aggregation_result()
        returns count aggregation by column names where values are empty

    """

    @property
    def metric_name(self) -> str:
        return "count_empty_hist"

    def aggregation_result(self, time_range: TimeRange = None) -> Dict[str, Any]:
        hist: Dict[str, Any] = {}

        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range)
        )
        facets = self._collection.aggregate(agg_query).next()

        empty_columns, total_sum = facets["empty_columns"], facets["total_sum"]

        if len(total_sum) > 0:
            for column_sum in total_sum:
                column_name = column_sum["_id"]["column_name"]
                hist[column_name] = {
                    "empty_count": 0,
                    "empty_percentage": 0.0,
                    "total_count": column_sum["count"],
                }

            for empty_column in empty_columns:
                empty_column_name = empty_column["_id"]["column_name"]
                total_count = hist[empty_column_name].get("total_count")
                empty_count = empty_column["count"]
                empty_percentage = float(empty_count) * (100.0 / float(total_count))
                hist[empty_column_name]["empty_count"] = empty_count
                hist[empty_column_name]["empty_percentage"] = empty_percentage

        return hist

    def _aggregation_query(self, time_filter: Dict = None) -> List[Dict[str, Any]]:
        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {"$unwind": "$columns"},
            {
                "$facet": {
                    "empty_columns": [
                        {
                            "$match": {
                                "$or": [
                                    {
                                        "columns.data_type": "CATEGORICAL",
                                        "columns.value_categorical": None,
                                    },
                                    {
                                        "columns.data_type": "NUMERIC",
                                        "columns.value_numeric": None,
                                    },
                                ]
                            }
                        },
                        {
                            "$group": {
                                "_id": {"column_name": "$columns.name"},
                                "count": {"$sum": 1},
                            }
                        },
                    ],
                    "total_sum": [
                        {
                            "$group": {
                                "_id": {"column_name": "$columns.name"},
                                "count": {"$sum": 1},
                            }
                        }
                    ],
                }
            },
        ]


class CardinalityCategorical(DataMetrics):
    @property
    def metric_name(self) -> str:
        return "categorical_cardinality"

    def aggregation_result(self, time_range: TimeRange = None) -> Dict[str, Any]:
        cardinality = {}

        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range)
        )
        for doc in self._collection.aggregate(agg_query):
            column, values = doc["_id"], doc["value_counts"]
            values.sort(key=lambda x: x["count"], reverse=True)
            cardinality[column] = {
                "values": values,
                "unique_values": len(values),
                "top_value": values[0]["value"],
                "top_value_count": values[0]["count"],
            }
        return cardinality

    def _aggregation_query(self, time_filter: Dict = None) -> List[Dict[str, Any]]:
        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {"$unwind": {"path": "$columns"}},
            {
                "$match": {
                    "columns.data_type": "CATEGORICAL",
                    "columns.value_categorical": {"$ne": None},
                }
            },
            {
                "$group": {
                    "_id": {
                        "name": "$columns.name",
                        "value": "$columns.value_categorical",
                    },
                    "count": {"$sum": 1},
                }
            },
            {
                "$group": {
                    "_id": "$_id.name",
                    "value_counts": {
                        "$push": {"value": "$_id.value", "count": "$count"}
                    },
                }
            },
        ]


class NumericBasicMetrics(DataMetrics):
    @property
    def metric_name(self) -> str:
        return "numeric_basic"

    def aggregation_result(
        self, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Any]:
        basic_metrics: Dict[str, Dict] = {}
        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range), **kwargs
        )
        facets = self._collection.aggregate(agg_query).next()
        total_values = facets["total"]
        average_values = facets["average_values"]
        min_values = facets["min_values"]
        max_values = facets["max_values"]
        zero_values = facets["zero_values"]
        std_dev_values = facets["std_dev_values"] if "std_dev_values" in facets else []

        for average_value in average_values:
            basic_metrics[average_value["_id"]["column_name"]] = {
                "avg": round(average_value["avg"], 2)
            }

        for total_value in total_values:
            basic_metrics[total_value["_id"]["column_name"]]["total"] = total_value[
                "count"
            ]
        for min_value in min_values:
            basic_metrics[min_value["_id"]["column_name"]]["min"] = min_value["min"]
        for max_value in max_values:
            basic_metrics[max_value["_id"]["column_name"]]["max"] = max_value["max"]
        for zero_value in zero_values:
            basic_metrics[zero_value["_id"]["column_name"]]["zeros"] = zero_value[
                "zero_count"
            ]

        for std_dev_value in std_dev_values:
            basic_metrics[std_dev_value["_id"]["column_name"]]["std_dev"] = round(
                std_dev_value["std_dev"], 2
            )
            basic_metrics[std_dev_value["_id"]["column_name"]]["variance"] = round(
                std_dev_value["std_dev"] ** 2
            )

        return basic_metrics

    def _aggregation_query(
        self, time_filter: Dict = None, **kwargs
    ) -> List[Dict[str, Any]]:
        facets = {
            "total": [
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "count": {"$sum": 1},
                    }
                }
            ],
            "average_values": [
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "avg": {"$avg": "$columns.value_numeric"},
                    }
                }
            ],
            "min_values": [
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "min": {"$min": "$columns.value_numeric"},
                    }
                }
            ],
            "max_values": [
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "max": {"$max": "$columns.value_numeric"},
                    }
                }
            ],
            "zero_values": [
                {"$match": {"columns.value_numeric": 0}},
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "zero_count": {"$sum": 1},
                    }
                },
            ],
        }
        if kwargs.get("std_dev_disable", "false") == "false":
            facets["std_dev_values"] = [
                {
                    "$group": {
                        "_id": {"column_name": "$columns.name"},
                        "std_dev": {"$stdDevPop": "$columns.value_numeric"},
                    }
                }
            ]

        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {"$unwind": "$columns"},
            {
                "$match": {
                    "columns.data_type": "NUMERIC",
                    "columns.value_numeric": {"$ne": None},
                }
            },
            {"$facet": facets},
        ]


class UniqueValueCountHistogram(DataMetrics):
    @property
    def metric_name(self) -> str:
        return "unique_value_count_hist"

    def aggregation_result(
        self, time_range: TimeRange = None, **kwargs
    ) -> Dict[str, Any]:
        hist: Dict[str, Any] = {}
        agg_query = self._aggregation_query(
            time_filter=self._time_filter_builder(time_range=time_range), **kwargs
        )
        for doc in self._collection.aggregate(agg_query):
            column_name = doc["_id"]
            column_value = doc["count"]
            hist[column_name] = column_value
        return hist

    def _aggregation_query(self, time_filter: Dict = None) -> List[Dict[str, Any]]:
        return [
            {
                "$match": {
                    "dataset_id": str(self._dataset_id),
                    **(time_filter if time_filter is not None else {}),
                }
            },
            {
                '$unwind': {
                    'path': '$columns'
             }
            }, 
            {
                '$match': {
                    '$or': [
                        {
                            'columns.value_numeric': {
                                '$ne': None
                            }
                        }, {
                            'columns.value_categorical': {
                                '$ne': None
                            }
                        }
                    ]
                }
            }, {
                '$group': {
                    '_id': '$columns.name',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]