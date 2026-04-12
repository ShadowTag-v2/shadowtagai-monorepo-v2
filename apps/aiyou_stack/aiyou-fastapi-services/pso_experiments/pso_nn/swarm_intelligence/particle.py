from collections.abc import Iterable

import numpy as np


class Particle:
    def __init__(
        self,
        random,
        position=None,
        velocity=None,
        position_range=None,
        velocity_range=None,
        dims=None,
        alpha=0.1,
    ):
        if velocity is None:
            velocity = [0.0]
        if position is None:
            position = [0.0]
        self._validate(random, position, velocity, position_range, velocity_range, dims, alpha)

        self.random = random
        self.position = position
        self.velocity = velocity
        self.position_range = position_range
        self.velocity_range = velocity_range
        self.dims = dims
        self.alpha = alpha

        self._init_particle()

        self.pbest = self.position

    def _validate(self, random, position, velocity, position_range, velocity_range, dims, alpha):
        if not isinstance(random, bool):
            raise TypeError(f"random should be of type bool but got type {type(random)}")
        if not isinstance(alpha, float):
            raise TypeError(f"alpha should be of type float but got type {type(alpha)}")

        if random is True:
            if not isinstance(position_range, Iterable):
                raise TypeError(
                    "When random is True position_range should be an"
                    f" Iterable of length 2 but got {type(position_range)}."
                )
            if not isinstance(velocity_range, Iterable):
                raise TypeError(
                    "When random is True velocity_range should be an"
                    f" Iterable of length 2 but got {type(position_range)}."
                )
            if not isinstance(dims, int):
                raise TypeError(
                    f"When random is True dims should be an int but got {type(position_range)}."
                )
        elif random is False:
            if not isinstance(position, Iterable):
                raise TypeError(
                    f"When random is False position should be an Iterable but got {type(position_range)}."
                )
            if not isinstance(velocity, Iterable):
                raise TypeError(
                    f"When random is False velocity should be an Iterable but got {type(position_range)}."
                )

    def _init_particle(self):
        if self.random:
            self.position = np.random.uniform(
                low=self.position_range[0], high=self.position_range[1], size=(self.dims,)
            )
            self.velocity = np.random.uniform(
                low=-abs(self.velocity_range[1] - self.velocity_range[0]),
                high=abs(self.velocity_range[1] - self.velocity_range[0]),
                size=(self.dims,),
            )
        else:
            self.position = np.asarray(position)
            self.velocity = np.asarray(velocity)
            self.dims = self.position.shape[0]

    def update(self, c1, c2, gbest, fitness_fn, compare_fn):
        if not isinstance(c1, float):
            raise TypeError(f"c1 should be of type float but got {type(c1)}")
        if not isinstance(c2, float):
            raise TypeError(f"c2 should be of type float but got {type(c2)}")
        if not isinstance(gbest, type(self.position)):
            raise TypeError(
                f"gbest should have same type as Particle's velocity,which is of type {type(self.velocity)}"
            )
        if self.position.shape[0] != gbest.shape[0]:
            raise ValueError(
                f"gbest should have shape {self.position.shape} but got shape {gbest.shape}"
            )

        self._update_velocity(c1, c2, gbest)
        self._update_position(fitness_fn, compare_fn)

    def _update_velocity(self, c1, c2, gbest):
        self.alpha = self.alpha / 2
        wrt_pbest = c1 * np.random.rand() * (self.pbest - self.position)
        wrt_gbest = c2 * np.random.rand() * (gbest - self.position)
        self.velocity = self.alpha * self.velocity + wrt_pbest + wrt_gbest

    def _update_position(self, fitness_fn, compare_fn):
        self.position = self.position + self.velocity + 0.01 * self.position
        if compare_fn(fitness_fn(self.position), fitness_fn(self.pbest)):
            self.pbest = self.position

    def __repr__(self):
        return f"<Particle: dims={self.dims} random={self.random}>"
