from collections import defaultdict
import datetime as dt
from typing import List

from GoogleEarth import GoogleEarth


class Simulator(object):
    def __init__(self,
                 start_time: dt.datetime,
                 source_x: float,
                 source_y: float,
                 iteration_interval: dt.timedelta,
                 particles: List[float],
                 dispersion_coeff: float,
                 google_earth: GoogleEarth):
        """A simulator for the disperson

        Args:
            start_time (dt.datetime): The start time of the disperson
            source_x (float): The x coordinate of the source
            source_y (float): The y coordinate of the source
            iteration_interval (dt.timedelta): The timedelta for each iteration
            particles (List[float]): The number of particles generated at the source
            dispersion_coeff (float): The dispersion coefficient of the gas
            google_earth (GoogleEarth): Google Earth API
        """
        self.time = start_time
        self.iteration_interval = iteration_interval
        self.particles = particles
        self.google_earth = google_earth
        self.source = source_x, source_y
        self.dispersion_coeff = dispersion_coeff
        self.status = dict()
        self.particle_index = 0

    def step(self):
        new_status = defaultdict(int)
        xx = list()
        yy = list()
        if self.particle_index < len(self.particles):
            new_status[self.source] = self.particles[self.particle_index]
        for x, y in self.status.keys():
            xx.append(x)
            yy.append(y)
        geo = self.google_earth.get_point_features(xx,
                                                   yy,
                                                   self.time,
                                                   ["wind_u", "wind_v", "temperature"],
                                                   start_time=self.time,
                                                   time_delta=self.iteration_interval)
        for (x, y), p in self.status.items():
            geo_info = geo[(geo["x"] == x) & (geo["y"] == y)]
            new_x = x + geo_info["wind_x"] * self.iteration_interval + geo_info["temperature"]
            new_y = y + geo_info["wind_y"] * self.iteration_interval + geo_info["temperature"]
            new_status[(new_x, new_y)] += p

        self.time += self.iteration_interval
        self.status = new_status
