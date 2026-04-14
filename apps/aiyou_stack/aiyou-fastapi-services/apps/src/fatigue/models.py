"""Fatigue Prediction Models
Edge-optimized ML models for real-time fatigue prediction (100-500ms latency)

Model Tiers:
- v1: Logistic Regression / GBDT (10-50 KB, fastest)
- v2: Distilled Neural Network (1-5 MB, balanced)
- v3: Full Neural Network (10-50 MB, cloud-only)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class FatiguePrediction:
    """Fatigue prediction output"""

    score: float  # 0-1 fatigue score
    confidence: float  # 0-1 confidence in prediction
    level: str  # fresh, mild, moderate, severe, critical
    timestamp: datetime
    features: dict[str, float]  # input features used
    model_version: str
    latency_ms: float  # inference time


class FatiguePredictor(ABC):
    """Base class for all fatigue prediction models"""

    def __init__(self, model_version: str):
        self.model_version = model_version
        self.feature_names = [
            # Blink features
            "blink_rate",
            "blink_duration",
            "incomplete_blinks",
            "time_since_last_blink",
            # Pupil features
            "pupil_diameter",
            "pupil_variance",
            "pupil_asymmetry",
            # HRV features
            "hrv_rmssd",
            "hrv_hr",
            "hrv_stress_index",
            # IMU features
            "head_tilt",
            "micro_saccade_rate",
            "head_drift",
            # Temporal features
            "session_duration_min",
            "time_since_last_break_min",
            "time_of_day_hour",
        ]

    @abstractmethod
    def predict(self, features: dict[str, float]) -> FatiguePrediction:
        """Predict fatigue from features"""

    def extract_features(self, sensor_fusion) -> dict[str, float]:
        """Extract features from SensorFusion object"""
        blink_metrics = sensor_fusion.blink_detector.get_metrics()
        pupil_metrics = sensor_fusion.pupil_tracker.get_metrics()
        hrv_metrics = sensor_fusion.hrv_monitor.get_metrics()
        imu_metrics = sensor_fusion.imu_analyzer.get_metrics()

        now = datetime.utcnow()

        features = {
            # Blink
            "blink_rate": blink_metrics.blink_rate,
            "blink_duration": blink_metrics.blink_duration,
            "incomplete_blinks": float(blink_metrics.incomplete_blinks),
            "time_since_last_blink": (now - blink_metrics.last_blink).total_seconds(),
            # Pupil
            "pupil_diameter": pupil_metrics.avg_diameter,
            "pupil_variance": pupil_metrics.diameter_variance,
            "pupil_asymmetry": abs(pupil_metrics.left_diameter - pupil_metrics.right_diameter),
            # HRV
            "hrv_rmssd": hrv_metrics.rmssd,
            "hrv_hr": hrv_metrics.hr_avg,
            "hrv_stress_index": hrv_metrics.stress_index,
            # IMU
            "head_tilt": imu_metrics.head_tilt_deg,
            "micro_saccade_rate": imu_metrics.micro_saccade_rate,
            "head_drift": imu_metrics.head_drift,
            # Temporal (placeholder - would track in session manager)
            "session_duration_min": 30.0,  # TODO: track actual session
            "time_since_last_break_min": 20.0,
            "time_of_day_hour": float(now.hour),
        }

        return features

    def normalize_features(self, features: dict[str, float]) -> np.ndarray:
        """Normalize features for model input"""
        # Feature normalization ranges (mean, std) from training data
        normalization = {
            "blink_rate": (15.0, 5.0),
            "blink_duration": (150.0, 50.0),
            "incomplete_blinks": (1.0, 1.5),
            "time_since_last_blink": (4.0, 3.0),
            "pupil_diameter": (3.5, 0.8),
            "pupil_variance": (0.3, 0.2),
            "pupil_asymmetry": (0.2, 0.15),
            "hrv_rmssd": (30.0, 15.0),
            "hrv_hr": (70.0, 12.0),
            "hrv_stress_index": (50.0, 20.0),
            "head_tilt": (5.0, 8.0),
            "micro_saccade_rate": (15.0, 8.0),
            "head_drift": (8.0, 5.0),
            "session_duration_min": (30.0, 20.0),
            "time_since_last_break_min": (15.0, 10.0),
            "time_of_day_hour": (12.0, 6.0),
        }

        normalized = []
        for name in self.feature_names:
            value = features.get(name, 0.0)
            mean, std = normalization.get(name, (0.0, 1.0))
            normalized.append((value - mean) / std)

        return np.array(normalized)

    def score_to_level(self, score: float) -> str:
        """Convert fatigue score to level"""
        if score < 0.2:
            return "fresh"
        if score < 0.4:
            return "mild"
        if score < 0.6:
            return "moderate"
        if score < 0.8:
            return "severe"
        return "critical"


class LogisticFatigueModel(FatiguePredictor):
    """Logistic Regression model (v1)

    Size: ~10 KB
    Latency: 50-100 ms
    Use Case: Ultra-low-power edge devices (glasses chip)

    Simple weighted sum → sigmoid activation
    """

    def __init__(self):
        super().__init__("logistic-v1.0")

        # Pre-trained weights (would be loaded from file in production)
        # These are example weights - would be learned from training data
        self.weights = np.array(
            [
                # Blink features (strong predictors)
                -0.15,  # blink_rate (lower = more fatigue)
                0.20,  # blink_duration (higher = more fatigue)
                0.25,  # incomplete_blinks
                0.18,  # time_since_last_blink
                # Pupil features
                -0.12,  # pupil_diameter (smaller = more fatigue)
                0.15,  # pupil_variance
                0.08,  # pupil_asymmetry
                # HRV features (strong predictors)
                -0.22,  # hrv_rmssd (lower = more stress/fatigue)
                0.18,  # hrv_hr (higher = more fatigue)
                0.25,  # hrv_stress_index
                # IMU features
                0.12,  # head_tilt (forward lean = fatigue)
                -0.10,  # micro_saccade_rate (lower = less alert)
                0.14,  # head_drift
                # Temporal features
                0.20,  # session_duration (longer = more fatigue)
                0.15,  # time_since_last_break
                0.05,  # time_of_day (slight circadian effect)
            ],
        )

        self.bias = -1.0  # Bias term

    def predict(self, features: dict[str, float]) -> FatiguePrediction:
        """Predict fatigue using logistic regression"""
        start_time = datetime.utcnow()

        # Normalize features
        X = self.normalize_features(features)

        # Linear combination
        logit = np.dot(self.weights, X) + self.bias

        # Sigmoid activation
        score = 1.0 / (1.0 + np.exp(-logit))

        # Clip to [0, 1]
        score = np.clip(score, 0.0, 1.0)

        # Calculate confidence (based on distance from decision boundary)
        confidence = abs(score - 0.5) * 2  # 0.0 at boundary, 1.0 at extremes

        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return FatiguePrediction(
            score=float(score),
            confidence=float(confidence),
            level=self.score_to_level(score),
            timestamp=datetime.utcnow(),
            features=features,
            model_version=self.model_version,
            latency_ms=latency_ms,
        )


class GBDTFatigueModel(FatiguePredictor):
    """Gradient Boosted Decision Tree model (v1.5)

    Size: 50-200 KB
    Latency: 100-200 ms
    Use Case: Mid-tier edge devices (phone companion app)

    Better accuracy than logistic, captures non-linear patterns
    """

    def __init__(self):
        super().__init__("gbdt-v1.5")

        # Simplified GBDT (would use LightGBM/XGBoost in production)
        # This is a mock implementation showing the concept
        self.n_trees = 10
        self.learning_rate = 0.1

        # Mock decision trees (in production, load from trained model)
        self.trees = self._create_mock_trees()

    def _create_mock_trees(self) -> list[dict]:
        """Create mock decision trees (simplified)"""
        # Each tree is a simple decision structure
        # In production, this would be loaded from a trained GBDT model
        trees = []
        for i in range(self.n_trees):
            tree = {
                "tree_id": i,
                "feature_thresholds": {
                    "blink_rate": 12.0 - i * 0.5,
                    "hrv_rmssd": 25.0 - i * 2.0,
                    "session_duration_min": 20.0 + i * 3.0,
                },
                "leaf_values": np.random.randn(8) * 0.1,  # 8 leaf nodes
            }
            trees.append(tree)
        return trees

    def _predict_tree(self, tree: dict, features: dict[str, float]) -> float:
        """Predict using single decision tree"""
        # Simplified tree traversal (binary decisions)
        leaf_idx = 0

        if features["blink_rate"] < tree["feature_thresholds"]["blink_rate"]:
            leaf_idx += 1
        if features["hrv_rmssd"] < tree["feature_thresholds"]["hrv_rmssd"]:
            leaf_idx += 2
        if features["session_duration_min"] > tree["feature_thresholds"]["session_duration_min"]:
            leaf_idx += 4

        return tree["leaf_values"][min(leaf_idx, len(tree["leaf_values"]) - 1)]

    def predict(self, features: dict[str, float]) -> FatiguePrediction:
        """Predict using GBDT ensemble"""
        start_time = datetime.utcnow()

        # Initialize with base prediction
        prediction = 0.5  # Start at neutral fatigue

        # Boosting: add predictions from each tree
        for tree in self.trees:
            tree_pred = self._predict_tree(tree, features)
            prediction += self.learning_rate * tree_pred

        # Apply sigmoid to get probability
        score = 1.0 / (1.0 + np.exp(-prediction))
        score = np.clip(score, 0.0, 1.0)

        # Higher confidence than logistic (ensemble reduces variance)
        confidence = min(0.95, abs(score - 0.5) * 2.2)

        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return FatiguePrediction(
            score=float(score),
            confidence=float(confidence),
            level=self.score_to_level(score),
            timestamp=datetime.utcnow(),
            features=features,
            model_version=self.model_version,
            latency_ms=latency_ms,
        )


class NeuralFatigueModel(FatiguePredictor):
    """Distilled Neural Network model (v2)

    Size: 1-5 MB
    Latency: 200-500 ms
    Use Case: Phone app or cloud-assisted prediction

    3-layer MLP with knowledge distillation from larger model
    Best accuracy for real-time prediction
    """

    def __init__(self):
        super().__init__("neural-v2.0")

        # Network architecture
        self.input_size = len(self.feature_names)
        self.hidden_sizes = [32, 16]
        self.output_size = 1

        # Initialize weights (would load from trained model)
        self.W1 = np.random.randn(self.input_size, self.hidden_sizes[0]) * 0.1
        self.b1 = np.zeros(self.hidden_sizes[0])

        self.W2 = np.random.randn(self.hidden_sizes[0], self.hidden_sizes[1]) * 0.1
        self.b2 = np.zeros(self.hidden_sizes[1])

        self.W3 = np.random.randn(self.hidden_sizes[1], self.output_size) * 0.1
        self.b3 = np.zeros(self.output_size)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation"""
        return np.maximum(0, x)

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation"""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def predict(self, features: dict[str, float]) -> FatiguePrediction:
        """Forward pass through neural network"""
        start_time = datetime.utcnow()

        # Normalize input
        X = self.normalize_features(features).reshape(1, -1)

        # Layer 1
        h1 = self._relu(np.dot(X, self.W1) + self.b1)

        # Layer 2
        h2 = self._relu(np.dot(h1, self.W2) + self.b2)

        # Output layer
        logit = np.dot(h2, self.W3) + self.b3
        score = self._sigmoid(logit)[0, 0]

        # Confidence from output layer activation strength
        # Higher values (further from 0) = more confident
        confidence = min(0.98, abs(logit[0, 0]) / 5.0)

        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return FatiguePrediction(
            score=float(score),
            confidence=float(confidence),
            level=self.score_to_level(score),
            timestamp=datetime.utcnow(),
            features=features,
            model_version=self.model_version,
            latency_ms=latency_ms,
        )


class AdaptiveFatiguePredictor:
    """Adaptive model selector based on device capabilities

    Automatically chooses best model for available compute:
    - Glasses chip (milliwatts): Logistic
    - Phone app (watts): GBDT or Neural
    - Cloud (unlimited): Full neural network
    """

    def __init__(self, device_tier: str = "mid"):
        """Args:
        device_tier: "low" (glasses), "mid" (phone), "high" (cloud)

        """
        self.device_tier = device_tier

        # Initialize appropriate model
        if device_tier == "low":
            self.model = LogisticFatigueModel()
        elif device_tier == "mid":
            self.model = GBDTFatigueModel()
        else:  # high
            self.model = NeuralFatigueModel()

    def predict(self, sensor_fusion) -> FatiguePrediction:
        """Predict fatigue from sensor fusion"""
        features = self.model.extract_features(sensor_fusion)
        return self.model.predict(features)

    def upgrade_model(self, new_tier: str):
        """Dynamically upgrade to more powerful model"""
        if new_tier != self.device_tier:
            self.device_tier = new_tier
            self.__init__(new_tier)


class FatigueSessionTracker:
    """Tracks fatigue progression over entire session

    Features:
    - Session duration tracking
    - Break detection and timing
    - Fatigue trend analysis
    - Intervention triggering
    """

    def __init__(self):
        self.session_start = datetime.utcnow()
        self.last_break = datetime.utcnow()
        self.predictions: list[FatiguePrediction] = []
        self.breaks_taken = 0
        self.interventions_triggered = 0

    def add_prediction(self, prediction: FatiguePrediction):
        """Add new prediction to session history"""
        self.predictions.append(prediction)

        # Trigger intervention if severe fatigue
        if prediction.level in ["severe", "critical"]:
            self.interventions_triggered += 1

    def take_break(self, duration_seconds: int):
        """Record break taken"""
        self.last_break = datetime.utcnow()
        self.breaks_taken += 1

    def get_session_stats(self) -> dict:
        """Get session statistics"""
        if not self.predictions:
            return {}

        scores = [p.score for p in self.predictions]
        levels = [p.level for p in self.predictions]

        return {
            "session_duration_min": (datetime.utcnow() - self.session_start).total_seconds() / 60,
            "time_since_last_break_min": (datetime.utcnow() - self.last_break).total_seconds() / 60,
            "avg_fatigue_score": np.mean(scores),
            "max_fatigue_score": np.max(scores),
            "current_fatigue_score": scores[-1],
            "fatigue_trend": "increasing"
            if len(scores) > 5 and scores[-1] > scores[-5]
            else "stable",
            "predictions_count": len(self.predictions),
            "breaks_taken": self.breaks_taken,
            "interventions_triggered": self.interventions_triggered,
            "time_in_severe_fatigue_min": sum(1 for l in levels if l in ["severe", "critical"])
            * 0.5,
        }

    def should_force_break(self) -> bool:
        """Determine if break should be forced"""
        if not self.predictions:
            return False

        stats = self.get_session_stats()

        # Force break if:
        # 1. Critical fatigue
        # 2. Severe fatigue for >5 minutes
        # 3. No break for >30 minutes and moderate+ fatigue

        current_level = self.predictions[-1].level

        if current_level == "critical":
            return True

        if current_level == "severe" and stats["time_in_severe_fatigue_min"] > 5:
            return True

        return bool(
            stats["time_since_last_break_min"] > 30 and stats["current_fatigue_score"] >= 0.4,
        )
