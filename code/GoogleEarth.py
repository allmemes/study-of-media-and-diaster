import datetime as dt
from functools import partial
import math
from itertools import product
from typing import Dict, List

import ee
import numpy as np
import pandas as pd


class GoogleEarth(object):
    def __init__(self):
        try:
            ee.Initialize()
        except Exception:
            ee.Authenticate()
            ee.Initialize()

    def _get_point_features(
        self,
        point: ee.feature.Feature,
        fields: List[str],
        collection: ee.ImageCollection,
        region: ee.Geometry,
        start_time: dt.datetime,
        time_delta: dt.timedelta = dt.timedelta(days=1)
    ) -> ee.Feature:
        """Get the features of a point

        Args:
            point (ee.feature.Feature): The point of interest
            fields (List[str]): The fields of interest
            collection (ee.ImageCollection): The collection from Google Earth
            region (ee.Geometry): The region of interest
            start_time (dt.datetime): The start time of interest
            time_delta (dt.timedelta): The time range of the data

        Returns:
            (ee.Feature): The features of the point
        """
        point = point.geometry()
        data = collection.filterDate(start_time, start_time + time_delta)
        data = data.filterBounds(region).mean().reduceRegion(ee.Reducer.first(), point, 500)
        return ee.Feature(point, {field: data.get(field) for field in fields})

    def get_points_features(
        self,
        u: List[float],
        v: List[float],
        fields: List[str],
        start_time: dt.datetime,
        time_delta: dt.timedelta = dt.timedelta(days=1)
    ) -> pd.DataFrame:
        """Get the features of points in a given region

        Args:
            u (List[float]): The x coordinates of points of interest
            v (List[float]): The y coordinates of points of interest
            fields (List[str]): The fields of interest
            start_time (dt.datetime): The start time of interest
            time_delta (dt.timedelta): The time range of the data

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        region = ee.Geometry.Polygon(list(product([min(u), max(u)], [min(v), max(v)])))
        points = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(*p)) for p in zip(u, v)])
        get_fields = partial(self._get_point_features,
                             fields=fields,
                             collection=ee.ImageCollection("NASA/NLDAS/FORA0125_H002"),
                             region=region,
                             start_time=start_time,
                             time_delta=time_delta)
        return self._resolve_features(points.map(get_fields).getInfo(), fields)

    def get_region_features(
        self,
        u: List[float],
        v: List[float],
        fields: List[str],
        start_time: dt.datetime,
        time_delta: dt.timedelta = dt.timedelta(days=1)
    ) -> pd.DataFrame:
        """Get the features of grid points in a given region

        Args:
            u (List[float]): The x coordinates of grid
            v (List[float]): The y coordinates of grid
            fields (List[str]): The fields of interest
            start_time (dt.datetime): The start time of interest
            time_delta (dt.timedelta): The time range of the data

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        region = ee.Geometry.Polygon(list(product([min(u), max(u)], [min(v), max(v)])))
        points = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(*p)) for p in product(u, v)])
        get_fields = partial(self._get_point_features,
                             fields=fields,
                             collection=ee.ImageCollection("NASA/NLDAS/FORA0125_H002"),
                             region=region,
                             start_time=start_time,
                             time_delta=time_delta)
        return self._resolve_features(points.map(get_fields).getInfo())

    def get_region_random_features(
        self,
        u: List[float],
        v: List[float],
        n_points: int,
        fields: List[str],
        start_time: dt.datetime,
        time_delta: dt.timedelta = dt.timedelta(days=1)
    ) -> pd.DataFrame:
        """Get the features of random points in a given region

        Args:
            u (List[float]): The x coordinates
            v (List[float]): The y coordinates
            n_points (int): The number of points
            fields (List[str]): The fields of interest
            start_time (dt.datetime): The start time of interest
            time_delta (dt.timedelta): The time range of the data

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        region = ee.Geometry.Polygon(list(product([min(u), max(u)], [min(v), max(v)])))
        cell_size = region.area().toFloat().sqrt().divide(math.sqrt(n_points))
        points = ee.FeatureCollection.randomPoints(region=region,
                                                   points=n_points,
                                                   seed=0,
                                                   maxError=cell_size.multiply(0.5))
        get_fields = partial(self._get_point_features,
                             fields=fields,
                             collection=ee.ImageCollection("NASA/NLDAS/FORA0125_H002"),
                             region=region,
                             start_time=start_time,
                             time_delta=time_delta)
        return self._resolve_features(points.map(get_fields).getInfo())

    def _resolve_features(self, points_fields: Dict[str, Dict], fields: List[str]) -> pd.DataFrame:
        """Resolve the _resolve_features of points

        Args:
            points_fields (Dict[str, Dict]): The mapped points with fields
            fields (List[str]): The fields of interest

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        df = list()
        for item in points_fields["features"]:
            row = item["geometry"]["coordinates"][:2]
            for field in fields:
                row.append(item["properties"].get(field, np.NaN))
            df.append(row)
        return pd.DataFrame(df, columns=["u", "v"] + fields)
