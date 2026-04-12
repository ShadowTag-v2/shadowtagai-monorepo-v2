"""
PSO-NN Core: Particle and swarm primitives for optimization.
"""

from .fitness import CrossEntropyFitness, FitnessFunction, MSEFitness
from .particle import Particle, ParticleState
from .swarm import ParticleSwarm

__all__ = [
    "Particle",
    "ParticleState",
    "ParticleSwarm",
    "FitnessFunction",
    "MSEFitness",
    "CrossEntropyFitness",
]
