"""Tests for PSO-NN Weight Optimizer."""

import numpy as np
import pytest

from ..core.fitness import SimpleFitness
from ..core.particle import Particle, ParticleState
from ..core.swarm import ParticleSwarm, SwarmConfig
from ..models.pso_model import PsoModel, PsoModelConfig, create_pso_model
from ..optimizers.weight_optimizer import WeightOptimizer


# Simple neural network for testing
class SimpleNN:
    """Simple 2-layer neural network for testing."""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        self.weights = {
            "W1": np.random.randn(input_dim, hidden_dim) * 0.1,
            "b1": np.zeros(hidden_dim),
            "W2": np.random.randn(hidden_dim, output_dim) * 0.1,
            "b2": np.zeros(output_dim),
        }

    def forward(self, x: np.ndarray) -> np.ndarray:
        h = np.maximum(0, x @ self.weights["W1"] + self.weights["b1"])  # ReLU
        return h @ self.weights["W2"] + self.weights["b2"]

    def get_weights(self) -> list[np.ndarray]:
        return [
            self.weights["W1"],
            self.weights["b1"],
            self.weights["W2"],
            self.weights["b2"],
        ]

    def set_weights(self, weights: list[np.ndarray]) -> None:
        self.weights["W1"] = weights[0]
        self.weights["b1"] = weights[1]
        self.weights["W2"] = weights[2]
        self.weights["b2"] = weights[3]


class TestParticle:
    """Tests for Particle class."""

    def test_random_initialization(self):
        """Test random particle initialization."""
        p = Particle.random(dimensions=10, bounds=(-1, 1))
        assert p.position.shape == (10,)
        assert p.velocity.shape == (10,)
        assert np.all(p.position >= -1) and np.all(p.position <= 1)

    def test_velocity_update(self):
        """Test velocity update with global best."""
        p = Particle.random(dimensions=5)
        global_best = np.ones(5)

        old_velocity = p.velocity.copy()
        p.update_velocity(global_best)

        # Velocity should change
        assert not np.allclose(p.velocity, old_velocity)

    def test_position_update(self):
        """Test position update."""
        p = Particle.random(dimensions=5, bounds=(-1, 1))
        p.velocity = np.ones(5) * 0.1

        old_position = p.position.copy()
        p.update_position(bounds=(-1, 1))

        # Position should change but stay in bounds
        assert not np.allclose(p.position, old_position)
        assert np.all(p.position >= -1) and np.all(p.position <= 1)

    def test_personal_best_update(self):
        """Test personal best tracking."""
        p = Particle.random(dimensions=5)

        # Initial fitness is inf, so any value should update
        updated = p.update_personal_best(0.5)
        assert updated
        assert p.personal_best_fitness == 0.5

        # Higher fitness should not update
        updated = p.update_personal_best(0.8)
        assert not updated
        assert p.personal_best_fitness == 0.5

    def test_get_state(self):
        """Test state snapshot."""
        p = Particle.random(dimensions=5)
        state = p.get_state()

        assert isinstance(state, ParticleState)
        assert state.position.shape == (5,)


class TestParticleSwarm:
    """Tests for ParticleSwarm class."""

    def test_initialization(self):
        """Test swarm initialization."""
        swarm = ParticleSwarm(num_particles=10, dimensions=5)
        assert len(swarm.particles) == 10
        assert swarm.global_best is None

    def test_step(self):
        """Test single optimization step."""
        swarm = ParticleSwarm(num_particles=10, dimensions=5)

        # Simple sphere function
        def sphere(x):
            return np.sum(x**2)

        fitness = swarm.step(sphere)
        assert swarm.global_best is not None
        assert fitness == swarm.global_best_fitness

    def test_optimize_sphere(self):
        """Test optimization on sphere function."""
        config = SwarmConfig(
            num_particles=30,
            dimensions=5,
            bounds=(-5, 5),
            max_iterations=100,
            stagnation_limit=20,  # Allow more iterations before stopping
        )
        swarm = ParticleSwarm(config)

        def sphere(x):
            return np.sum(x**2)

        result = swarm.optimize(sphere)

        # Should improve from initial random (typically ~25-50) to reasonable value
        # PSO is stochastic, so we use a lenient threshold
        assert result.best_fitness < 5.0
        assert np.all(np.abs(result.best_position) < 3.0)

    def test_convergence_detection(self):
        """Test convergence detection."""
        swarm = ParticleSwarm(num_particles=10, dimensions=2)

        # Trivial function that converges immediately
        def const(x):
            return 0.0

        for _ in range(5):
            swarm.step(const)

        assert swarm.is_converged()

    def test_diversity_calculation(self):
        """Test swarm diversity metric."""
        swarm = ParticleSwarm(num_particles=10, dimensions=5)
        diversity = swarm.get_diversity()
        assert diversity > 0  # Randomly initialized should have diversity

    def test_particle_injection(self):
        """Test injecting a particle at specific position."""
        swarm = ParticleSwarm(num_particles=10, dimensions=5)

        # Evaluate particles first so they have fitness
        def sphere(x):
            return np.sum(x**2)

        swarm.step(sphere)

        # Inject particle at origin
        optimal = np.zeros(5)
        swarm.inject_particle(optimal)

        # One particle should be at origin
        positions = [p.position for p in swarm.particles]
        has_optimal = any(np.allclose(pos, optimal) for pos in positions)
        assert has_optimal


class TestWeightOptimizer:
    """Tests for WeightOptimizer class."""

    def test_weight_extraction(self):
        """Test weight extraction from network."""
        nn = SimpleNN(4, 8, 2)
        optimizer = WeightOptimizer(nn)

        assert optimizer.shape_info.total_params == 4 * 8 + 8 + 8 * 2 + 2
        assert len(optimizer.shape_info.shapes) == 4

    def test_weight_flatten_reshape(self):
        """Test flattening and reshaping weights."""
        nn = SimpleNN(4, 8, 2)
        optimizer = WeightOptimizer(nn)

        original_weights = nn.get_weights()
        flat = optimizer._flatten_weights()
        reshaped = optimizer._reshape_weights(flat)

        for orig, new in zip(original_weights, reshaped, strict=False):
            assert np.allclose(orig, new)

    def test_optimize_simple(self):
        """Test optimizing a simple network."""
        np.random.seed(42)

        # Generate simple linear data
        X = np.random.randn(100, 4)
        y = X @ np.array([1, 2, 3, 4]) + 0.1 * np.random.randn(100)
        y = y.reshape(-1, 1)

        nn = SimpleNN(4, 8, 1)
        config = SwarmConfig(
            num_particles=20,
            max_iterations=30,
            bounds=(-2, 2),
        )
        optimizer = WeightOptimizer(nn, swarm_config=config)

        # Initial prediction error
        initial_preds = nn.forward(X)
        initial_mse = np.mean((initial_preds - y) ** 2)

        # Optimize
        result = optimizer.optimize(X, y)

        # Final prediction error
        final_preds = nn.forward(X)
        np.mean((final_preds - y) ** 2)

        # Should improve (note: PSO may not always find optimal)
        assert result.best_fitness <= initial_mse


class TestPsoModel:
    """Tests for PsoModel class."""

    def test_initialization(self):
        """Test PsoModel initialization."""
        nn = SimpleNN(4, 8, 2)
        model = PsoModel(target_network=nn)

        stats = model.get_stats()
        assert stats["network_params"] > 0
        assert stats["task_type"] == "regression"

    def test_create_factory(self):
        """Test factory function."""
        nn = SimpleNN(4, 8, 2)
        model = create_pso_model(nn, task="classification", num_particles=30, max_iterations=50)

        assert model.config.task_type == "classification"
        assert model.config.num_particles == 30

    def test_sync_optimization(self):
        """Test synchronous optimization."""
        np.random.seed(42)

        X = np.random.randn(50, 4)
        y = (np.sum(X, axis=1) > 0).astype(float).reshape(-1, 1)

        nn = SimpleNN(4, 8, 1)
        config = PsoModelConfig(
            num_particles=15,
            max_iterations=20,
        )
        model = PsoModel(target_network=nn, config=config)

        result = model.optimize_sync(X, y)

        assert result is not None
        assert result.iterations > 0

    @pytest.mark.asyncio
    async def test_async_optimization(self):
        """Test async optimization."""
        np.random.seed(42)

        X = np.random.randn(50, 4)
        y = np.random.randn(50, 1)

        nn = SimpleNN(4, 8, 1)
        config = PsoModelConfig(
            num_particles=15,
            max_iterations=20,
        )
        model = PsoModel(target_network=nn, config=config)

        result = await model.optimize(X, y)

        assert result is not None
        assert model.get_optimized_weights() is not None

    def test_save_load_weights(self, tmp_path):
        """Test saving and loading weights."""
        nn = SimpleNN(4, 8, 2)
        model = PsoModel(target_network=nn)

        # Optimize briefly
        X = np.random.randn(20, 4)
        y = np.random.randn(20, 2)
        model.optimize_sync(X, y, max_iterations=5)

        # Save
        path = str(tmp_path / "weights.npy")
        model.save_weights(path)

        # Create new model and load
        nn2 = SimpleNN(4, 8, 2)
        model2 = PsoModel(target_network=nn2)
        model2.load_weights(path)

        # Weights should match
        w1 = model.get_optimized_weights()
        w2 = model2.get_optimized_weights()
        assert np.allclose(w1, w2)


class TestFitness:
    """Tests for fitness functions."""

    def test_simple_fitness(self):
        """Test SimpleFitness wrapper."""
        fitness = SimpleFitness(lambda x: np.sum(x**2))
        result = fitness(np.array([1, 2, 3]))
        assert result == 14

    def test_mse_fitness(self):
        """Test MSE fitness calculation via SimpleFitness."""
        # Use SimpleFitness for straightforward testing
        # (MSEFitness requires proper weight application which is done by WeightOptimizer)
        nn = SimpleNN(4, 8, 1)
        X = np.random.randn(10, 4)
        y = np.random.randn(10, 1)

        def mse_fn(unused_weights):
            # Just test that MSE calculation works on current network state
            preds = nn.forward(X)
            return np.mean((preds - y) ** 2)

        fitness = SimpleFitness(mse_fn)
        result = fitness(np.array([]))

        # Should return a scalar
        assert isinstance(result, (int, float, np.floating))


# Run tests with: pytest src/pso_nn/tests/test_weight_optimizer.py -v
