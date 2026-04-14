from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

# Constants
DEFAULT_MAX_LR = 0.1
DEFAULT_MIN_LR = 0.01
DEFAULT_TOTAL_EPOCHS = 100


class CosineSchedule:
    """Cosine annealing learning rate schedule."""

    def __init__(
        self,
        max_lr: float = DEFAULT_MAX_LR,
        min_lr: float = DEFAULT_MIN_LR,
        total_epochs: int = DEFAULT_TOTAL_EPOCHS,
    ):
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.total_epochs = total_epochs

    def get_lr(self, epoch: int) -> float:
        """Get learning rate for current epoch."""
        if epoch >= self.total_epochs:
            return self.min_lr
        cosine_factor = (1 + np.cos(np.pi * epoch / self.total_epochs)) / 2
        return float(self.min_lr + (self.max_lr - self.min_lr) * cosine_factor)


def clip_grad_norm(parameters: list, max_norm: float = 1.0) -> float:
    """Clip gradients by global norm."""
    if not parameters:
        return 0.0

    total_norm = 0.0
    for param in parameters:
        if param.grad is not None:
            grad_data = param.grad if isinstance(param.grad, np.ndarray) else param.grad.data
            total_norm += np.sum(grad_data**2)

    total_norm = np.sqrt(total_norm)

    if total_norm > max_norm:
        clip_coef = max_norm / total_norm
        for param in parameters:
            if param.grad is not None:
                if isinstance(param.grad, np.ndarray):
                    param.grad = param.grad * clip_coef
                else:
                    param.grad.data = param.grad.data * clip_coef

    return float(total_norm)


class Trainer:
    """Complete training orchestrator."""

    def __init__(self, model, optimizer, loss_fn, scheduler=None, grad_clip_norm=None):
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.scheduler = scheduler
        self.grad_clip_norm = grad_clip_norm

        self.epoch = 0
        self.step = 0
        self.training_mode = True
        self.history = {"train_loss": [], "eval_loss": [], "learning_rates": []}

    def _train_step(self, inputs, targets, accumulation_steps, batch_idx) -> tuple[float, float]:
        """Execute a single training step (forward + backward)."""
        # Forward
        outputs = self.model(inputs)
        loss = self.loss_fn(outputs, targets)

        # Scale for accumulation
        scaled_loss = loss.data / accumulation_steps

        # Backward
        loss.backward()

        return float(scaled_loss), float(loss.data)

    def _perform_update(self):
        """Perform optimizer update and zero gradients."""
        if self.grad_clip_norm is not None:
            clip_grad_norm(self.model.parameters(), self.grad_clip_norm)

        self.optimizer.step()
        self.optimizer.zero_grad()

    def train_epoch(self, dataloader, accumulation_steps=1):
        """Train for one epoch."""
        self.model.training = True
        self.training_mode = True

        total_loss = 0.0
        num_batches = 0
        accumulated_loss = 0.0

        for batch_idx, (inputs, targets) in enumerate(dataloader):
            scaled_loss, batch_loss = self._train_step(
                inputs, targets, accumulation_steps, batch_idx,
            )
            accumulated_loss += scaled_loss

            # Update if accumulation interval reached
            if (batch_idx + 1) % accumulation_steps == 0:
                self._perform_update()
                total_loss += accumulated_loss * accumulation_steps  # approx reconstruction
                accumulated_loss = 0.0
                num_batches += 1
                self.step += 1

        # Remaining accumulated gradients
        if accumulated_loss > 0:
            self._perform_update()
            total_loss += accumulated_loss * accumulation_steps
            num_batches += 1

        avg_loss = float(total_loss / max(num_batches, 1))
        self.history["train_loss"].append(avg_loss)

        if self.scheduler:
            current_lr = self.scheduler.get_lr(self.epoch)
            self.optimizer.lr = current_lr
            self.history["learning_rates"].append(current_lr)

        self.epoch += 1
        return avg_loss

    def _calculate_accuracy(self, outputs, targets) -> int:
        """Calculate number of correct predictions."""
        if len(outputs.data.shape) > 1:  # Multi-class
            preds = np.argmax(outputs.data, axis=1)
            if len(targets.data.shape) == 1:
                return int(np.sum(preds == targets.data))
            # One-hot
            return int(np.sum(preds == np.argmax(targets.data, axis=1)))
        return 0

    def evaluate(self, dataloader):
        """Evaluate model."""
        self.model.training = False
        self.training_mode = False

        total_loss = 0.0
        correct = 0
        total = 0

        for inputs, targets in dataloader:
            outputs = self.model(inputs)
            loss = self.loss_fn(outputs, targets)
            total_loss += loss.data

            correct += self._calculate_accuracy(outputs, targets)

            # Count total samples (handling batch dimension correctly)
            if len(outputs.data.shape) > 0:
                total += outputs.data.shape[0]
            else:
                total += 1

        avg_loss = total_loss / len(dataloader) if len(dataloader) > 0 else 0.0
        accuracy = correct / total if total > 0 else 0.0
        self.history["eval_loss"].append(avg_loss)

        return avg_loss, accuracy

    def save_checkpoint(self, path: str):
        """Save training state."""
        checkpoint = {
            "epoch": self.epoch,
            "step": self.step,
            "model_state": self._get_model_state(),
            "optimizer_state": self._get_optimizer_state(),
            "scheduler_state": self._get_scheduler_state(),
            "history": self.history,
            "training_mode": self.training_mode,
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(checkpoint, f)

    def load_checkpoint(self, path: str):
        """Load training state."""
        with open(path, "rb") as f:
            checkpoint = pickle.load(f)

        self.epoch = checkpoint["epoch"]
        self.step = checkpoint["step"]
        self.history = checkpoint["history"]
        self.training_mode = checkpoint["training_mode"]

        if "model_state" in checkpoint:
            self._set_model_state(checkpoint["model_state"])
        if "optimizer_state" in checkpoint:
            self._set_optimizer_state(checkpoint["optimizer_state"])
        if "scheduler_state" in checkpoint:
            self._set_scheduler_state(checkpoint["scheduler_state"])

    def _get_model_state(self):
        return {i: param.data.copy() for i, param in enumerate(self.model.parameters())}

    def _set_model_state(self, state):
        for i, param in enumerate(self.model.parameters()):
            if i in state:
                param.data = state[i].copy()

    def _get_optimizer_state(self):
        state = {"lr": self.optimizer.lr}
        if hasattr(self.optimizer, "has_momentum") and self.optimizer.has_momentum():
            momentum_state = self.optimizer.get_momentum_state()
            if momentum_state:
                state["momentum_buffers"] = momentum_state
        return state

    def _set_optimizer_state(self, state):
        if "lr" in state:
            self.optimizer.lr = state["lr"]
        if (
            "momentum_buffers" in state
            and hasattr(self.optimizer, "has_momentum")
            and self.optimizer.has_momentum()
        ):
            self.optimizer.set_momentum_state(state["momentum_buffers"])

    def _get_scheduler_state(self):
        if not self.scheduler:
            return None
        return {
            "max_lr": getattr(self.scheduler, "max_lr", None),
            "min_lr": getattr(self.scheduler, "min_lr", None),
            "total_epochs": getattr(self.scheduler, "total_epochs", None),
        }

    def _set_scheduler_state(self, state):
        if not state or not self.scheduler:
            return
        for k, v in state.items():
            if hasattr(self.scheduler, k):
                setattr(self.scheduler, k, v)
