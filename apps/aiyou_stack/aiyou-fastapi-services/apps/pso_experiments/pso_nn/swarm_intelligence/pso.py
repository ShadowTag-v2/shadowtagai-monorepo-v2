# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from collections.abc import Iterable

import numpy as np
from tqdm import tqdm

from .particle import Particle


class ParticleSwarmOptimizer:
    def __init__(
        self,
        particle_cls,
        c1,
        c2,
        n_particles,
        fitness_fn,
        compare_fn,
        n_iter=1,
        dims=None,
        random=True,
        particles_list=None,
        position_range=None,
        velocity_range=None,
    ):
        self._validate(
            particle_cls,
            c1,
            c2,
            n_particles,
            fitness_fn,
            compare_fn,
            n_iter,
            dims,
            random,
            particles_list,
        )

        self.particle_cls = particle_cls
        self.c1 = c1
        self.c2 = c2
        self.n_particles = n_particles
        self.n_iter = n_iter
        self.fitness_fn = fitness_fn
        self.compare_fn = compare_fn
        self.position_range = position_range
        self.velocity_range = velocity_range
        self.dims = dims
        self.random = random
        self.particles_list = particles_list

        self._init_particles_list()

    def _validate(
        self,
        particle_cls,
        c1,
        c2,
        n_particles,
        fitness_fn,
        compare_fn,
        n_iter,
        dims,
        random,
        particles_list,
    ):
        if not issubclass(particle_cls, Particle):
            raise TypeError("particle_cls should inherit from particle.Particle class")
        if not isinstance(c1, float):
            raise TypeError(f"c1 should be of type float but got {type(c1)}")
        if not isinstance(c2, float):
            raise TypeError(f"c2 should be of type float but got {type(c2)}")

        if not callable(fitness_fn):
            raise TypeError("fitness_fn should be a callable")
        temp = fitness_fn(np.random.randn(dims))
        if not isinstance(temp, float):
            raise TypeError(
                f"fitness_fn should return a single valued float but returned {type(temp)}",
            )

        if not callable(compare_fn):
            raise TypeError("compare_fn should be a callable")
        temp = compare_fn(10, 20)
        if not isinstance(temp, bool):
            raise TypeError(f"compare_fn should return a bool but returned {type(temp)}")

        if not isinstance(n_particles, int):
            raise TypeError(f"n_particles should be of type int but got {type(n_particles)}")
        if n_particles <= 0:
            raise ValueError("n_particles should be a positive integer")

        if not isinstance(dims, int):
            raise TypeError(f"dims should be of type int but got {type(dims)}")
        if not isinstance(random, bool):
            raise TypeError(f"random should be of type bool but got {type(c1)}")

        if not random:
            if not isinstance(particles_list, Iterable):
                raise TypeError(
                    f"particles_list should be an Iterable but got {type(particles_list)}",
                )
            if len(particles_list) == n_particles:
                raise ValueError(f"particles_list should {n_particles} number of particles.")

            for i, particle in enumerate(particles_list):
                if not isinstance(particle, particle_cls):
                    raise TypeError(
                        "Every particle in particles_list must be an object of class particle_cls"
                        f" but got object of type {type(particle)} at position {i}",
                    )

    def _get_fitness(self, position):
        return self.fitness_fn(position)

    def _update_gbest(self):
        for particle_i in self.particles_list:
            l1, l2 = self._get_fitness(particle_i.pbest), self._get_fitness(self.gbest)
            print(l1)
            if self.compare_fn(l1, l2):
                self.gbest = particle_i.position

    def _init_particles_list(self):
        if self.random:
            self.particles_list = []

            for _i in range(self.n_particles):
                particle = self.particle_cls(
                    self.random,
                    position_range=self.position_range,
                    velocity_range=self.velocity_range,
                    dims=self.dims,
                )
                self.particles_list.append(particle)

        self.gbest = self.particles_list[0].position
        self._update_gbest()

        self.dims = self.particles_list[0].dims

    def optimize(self):
        for _i in tqdm(range(self.n_iter)):
            for particle in self.particles_list:
                particle.update(self.c1, self.c2, self.gbest, self.fitness_fn, self.compare_fn)
            self._update_gbest()
        return self
