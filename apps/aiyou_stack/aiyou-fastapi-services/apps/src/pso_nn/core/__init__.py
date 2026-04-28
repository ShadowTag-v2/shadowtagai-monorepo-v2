# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PSO-NN Core: Particle and swarm primitives for optimization."""

from .fitness import CrossEntropyFitness, FitnessFunction, MSEFitness
from .particle import Particle, ParticleState
from .swarm import ParticleSwarm

__all__ = [
    "CrossEntropyFitness",
    "FitnessFunction",
    "MSEFitness",
    "Particle",
    "ParticleState",
    "ParticleSwarm",
]
