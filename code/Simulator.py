from collections import defaultdict
import datetime as dt

from GoogleEarth import GoogleEarth


class Simulator(object):
    def __init__(self,
                 start_time: dt.datetime,
                 stop_time: dt.timedelta,
                 explosion_x: float,
                 explosion_y: float,
                 iteration_interval: dt.timedelta,
                 particles: float,
                 google_earth: GoogleEarth):
        """A simulator for the disperson

        Args:
            start_time (dt.datetime): The start time of the disperson
            stop_time (dt.datetime): The stop time of the explosion
            explosion_x (float): The x coordinate of the explosion
            explosion_y (float): The y coordinate of the explosion
            iteration_interval (dt.timedelta): The timedelta for each iteration
            particles (float): The many particles are relased totaly for simulation
            google_earth (GoogleEarth): Google Earth API
        """
        self.time = start_time
        self.stop_time = stop_time
        self.iteration_interval = iteration_interval
        self.particles = particles
        self.google_earth = google_earth
        self.emission_rate = particles / (self.stop_time - self.time) / iteration_interval
        self.explosion_point = explosion_x, explosion_y
        self.state = {self.explosion_point: particles}

    def step(self):
        new_state = defaultdict(int)
        xx = list()
        yy = list()
        for x, y in self.state.keys():
            xx.append(x)
            yy.append(y)
        geo = self.google_earth.get_point_features(xx, yy, self.time, ["wind_u", "wind_v", "temp"])
        for (x, y), p in self.state.items():
            geo_info = geo[(geo["x"] == x) & (geo["y"] == y)]
            new_x = x + geo_info["wind_x"] * self.iteration_interval + geo_info["temp"]
            new_y = y + geo_info["wind_y"] * self.iteration_interval + geo_info["temp"]
            new_state[(new_x, new_y)] += p

        self.time += self.iteration_interval
        if self.time <= self.stop_time:
            new_state[self.explosion_point] += self.emission_rate
        self.state = new_state
