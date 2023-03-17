from collections import defaultdict
import datetime as dt
import math
from typing import Dict, List, Optional, Tuple

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from shapely.geometry import Point
import pandas as pd

from GoogleEarth import GoogleEarth


class Simulator(object):
    def __init__(self,
                 start_time: dt.datetime,
                 end_time: dt.datetime,
                 source: Tuple[float],
                 iteration_interval: dt.timedelta,
                 simulate_interval: dt.timedelta,
                 google_earth: GoogleEarth,
                 precision: int = 2):
        """A simulator for the disperson

        Args:
            start_time (dt.datetime): The start time of the disperson
            end_time (dt.datetime): The start time of the disperson
            source (Tuple[float]): The x, y coordinate of the source
            iteration_interval (dt.timedelta): The timedelta for each iteration
            simulate_interval (dt.timedelta): The timedelta for each wind simulation
            google_earth (GoogleEarth): Google Earth API
            precision (int): The precision of simulation
        """
        self.time = start_time
        self.end_time = end_time
        self.iteration_interval = iteration_interval
        self.simulation_interval = simulate_interval.seconds
        self.google_earth = google_earth
        self.status = dict()
        y_unit = 111690  # 1 degree in latitude is equal to 111690m
        self.move = np.array([1 / math.cos(source[-1] * math.pi / 180), 1])
        self.move = (iteration_interval.seconds / y_unit / self.move)
        self.source = tuple(round(i, precision) for i in source)
        self.precision = precision

    def apply_wind(self,
                   df_coordinates: List[List[float]],
                   new_status: Dict[Tuple[float], float]) -> np.array:
        """Get wind data from google earth and apply it on the coordinates

        Args:
            df_coordinates (pd.DataFrame): A dataframe with coordinates

        Returns:
            (pd.DataFrame): A new dataframe with updated coordinates
        """
        df_coordinates = pd.DataFrame(df_coordinates, columns=["x", "y", "p"])
        geo = self.google_earth.get_points_features(df_coordinates["x"],
                                                    df_coordinates["y"],
                                                    ["wind_u", "wind_v"],
                                                    start_time=self.time,
                                                    time_delta=self.iteration_interval).values
        simulation_count = self.iteration_interval.seconds // self.simulation_interval
        geo = np.repeat(geo, simulation_count, axis=0)
        move = np.tile(np.ones(simulation_count).cumsum(), len(df_coordinates))
        geo[:, :2] += (move.reshape(len(move), 1) * self.move.reshape(1, 2)) * geo[:, -2:]

        particles = np.repeat(df_coordinates["p"], simulation_count) / simulation_count
        for (x, y), particle in zip(geo[:, :2].round(self.precision), particles):
            new_status[(x, y)] += particle

    def step(self):
        new_status = defaultdict(int)
        if self.time <= self.end_time:
            self.status[self.source] = 1

        df_coordinates = list()
        for (x, y), p in self.status.items():
            if p < 1e-4:
                continue
            df_coordinates.append([x, y, p])
            if len(df_coordinates) >= 2500:
                self.apply_wind(df_coordinates, new_status)
                df_coordinates.clear()
        if df_coordinates:
            self.apply_wind(df_coordinates, new_status)
        self.time += self.iteration_interval
        self.status = new_status

    def get_status(self) -> pd.DataFrame:
        """Get current simulation status"""
        df = pd.DataFrame(columns=["X", "Y", "P"])
        for (x, y), p in self.status.items():
            df.loc[len(df)] = [x, y, p]
        return df

    @staticmethod
    def plot_status(df_status: pd.DataFrame,
                    df_shp: gpd.GeoDataFrame,
                    status_time: Optional[dt.datetime] = None):
        """Plot the simulation status"""
        geometry = [Point(xy) for xy in zip(df_status["X"], df_status["Y"])]
        df_geo = gpd.GeoDataFrame(df_status, geometry=geometry, crs="EPSG:4326")
        df_geo = gpd.sjoin(df_geo, df_shp, op="within", how="left")
        df_status = df_shp.set_index(["NAME"])
        df_status["Value"] = df_geo.groupby(["NAME"]).count()["P"]
        df_status["Value"] = df_status["Value"].fillna(0)
        df_status["Value"] = df_status["Value"] / df_status["Value"].sum()
        ax = plt.subplots(figsize=(12.5, 12.5))[1]
        df_status.plot(column="Value", cmap="Reds", linewidth=0.1, edgecolor="white", ax=ax)
        ax.set_xlim(-100, -60)
        ax.set_ylim(25, 55)
        if status_time is not None:
            status_time = status_time.strftime("%Y%m%d %H%M%S")
            ax.set_title(f"Status plot at {status_time}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
