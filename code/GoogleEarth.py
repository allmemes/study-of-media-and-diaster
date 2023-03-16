import datetime as dt
from functools import partial
import math
from itertools import product
from typing import Dict, List

import ee
import pandas as pd


class GoogleEarth(object):
    def __init__(self):
        ee.Authenticate()
        ee.Initialize()

    def _get_point_features(
        self,
        point: ee.feature.Feature,
        start_date: dt.datetime,
        end_date: dt.datetime,
        fields: List[str],
        collection: ee.ImageCollection,
        region: ee.Geometry
    ) -> ee.Feature:
        """Get the features of a point

        Args:
            point (ee.feature.Feature): The point of interest
            start_date (dt.datetime): start_date
            end_date (dt.datetime): end_date
            fields (List[str]): The fields of interest
            collection (ee.ImageCollection): The collection from Google Earth
            region (ee.Geometry): The region of interest

        Returns:
            (ee.Feature): The features of the point
        """
        point = point.geometry()
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        data_mean = collection.filterDate(start_date, end_date).filterBounds(region).mean()
        data = data_mean.reduceRegion(ee.Reducer.first(), point, 500)
        return ee.Feature(point, {field: data.get(field) for field in fields})

    def get_region_features(
        self,
        u: List[float],
        v: List[float],
        start_date: dt.datetime,
        end_date: dt.datetime,
        fields: List[str]
    ) -> pd.DataFrame:
        """Get the features of random points in a given region

        Args:
            u (List[float]): The x coordinates
            v (List[float]): The y coordinates
            start_date (dt.datetime): start_date
            end_date (dt.datetime): end_date
            fields (List[str]): The fields of interest

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        region = ee.Geometry.Polygon(list(product([min(u), max(u)], [min(v), max(v)])))
        points = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(*p)) for p in product(u, v)])
        get_fields = partial(self._get_point_features,
                             start_date=start_date,
                             end_date=end_date,
                             fields=fields,
                             collection=ee.ImageCollection("NASA/NLDAS/FORA0125_H002"),
                             region=region)
        return self._resolve_features(points.map(get_fields).getInfo())

    def get_region_random_features(
        self,
        u: List[float],
        v: List[float],
        n_points: int,
        start_date: dt.datetime,
        end_date: dt.datetime,
        fields: List[str]
    ) -> pd.DataFrame:
        """Get the features of random points in a given region

        Args:
            u (List[float]): The x coordinates
            v (List[float]): The y coordinates
            n_points (int): The number of points
            start_date (dt.datetime): start_date
            end_date (dt.datetime): end_date
            fields (List[str]): The fields of interest

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
                             start_date=start_date,
                             end_date=end_date,
                             fields=fields,
                             collection=ee.ImageCollection("NASA/NLDAS/FORA0125_H002"),
                             region=region)
        return self._resolve_features(points.map(get_fields).getInfo())

    def _resolve_features(self, points_fields: Dict[str, Dict]) -> pd.DataFrame:
        """Resolve the _resolve_features of points

        Args:
            points_fields (Dict[str, Dict]): The mapped points with fields

        Returns:
            (pd.DataFrame): The dataframe with points coordinates and features
        """
        df = {"u": list(), "v": list()}
        for item in points_fields["features"]:
            df["u"].append(item["geometry"]["coordinates"][0])
            df["v"].append(item["geometry"]["coordinates"][1])
            for key in item["properties"].keys():
                if key not in df.keys():
                    df[key] = list()
                df[key].append(item["properties"][key])
        return pd.DataFrame(df)
