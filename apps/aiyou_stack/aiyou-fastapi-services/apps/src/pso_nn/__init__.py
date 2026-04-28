# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PSO-NN: Particle Swarm Optimization for Neural Networks.

This module provides PSO-based optimization for neural network weights,
hyperparameters, and topology evolution. Integrates with n-autoresearch/Kosmos/BioAgents
swarm for distributed optimization.

Usage:
    from pso_nn import PsoModel, WeightOptimizer, ParticleSwarm

    # Optimize a neural network
    model = PsoModel(target_network=my_nn)
    optimized = await model.optimize(fitness_fn=loss_fn)

    # Direct swarm optimization
    swarm = ParticleSwarm(num_particles=50, dimensions=1000)
    best = swarm.optimize(fitness_fn, max_iterations=100)
"""

from .core.fitness import (
    ComposedFitness,
    CrossEntropyFitness,
    FitnessFunction,
    MSEFitness,
)
from .core.particle import Particle, ParticleState
from .core.swarm import ParticleSwarm
from .models.pso_model import PsoModel
from .optimizers.weight_optimizer import WeightOptimizer

__version__ = "0.1.0"
__all__ = [
    "ComposedFitness",
    "CrossEntropyFitness",
    "FitnessFunction",
    "MSEFitness",
    "Particle",
    "ParticleState",
    "ParticleSwarm",
    "PsoModel",
    "WeightOptimizer",
]
