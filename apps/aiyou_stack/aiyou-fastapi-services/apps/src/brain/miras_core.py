import torch
import torch.nn as nn
import torch.nn.functional as F


class ShadowTagMemory(nn.Module):
    def __init__(self, d_model, variant="yaad", p=3, delta=1.0, momentum=0.9):
        super().__init__()
        self.variant = variant
        self.p = p  # Moneta norm parameter
        self.delta = delta  # Yaad Huber threshold
        self.momentum = momentum  #

        # Choice 1: Deep Memory Architecture (Two-layer MLP is crucial)
        # Deep Memory Architecture (Two-layer MLP is crucial)
        self.memory_mlp = nn.Sequential(
            nn.Linear(d_model, d_model * 4), nn.SiLU(), nn.Linear(d_model * 4, d_model)
        )

        # Choice 2: Memory Learning Algorithm (Parametric step size & Momentum)
        self.eta = nn.Parameter(torch.ones(d_model) * 0.1)
        self.register_buffer("S", torch.zeros(1, d_model))  # Momentum state for memory update
        self.retention_gate = nn.Linear(d_model, d_model)

    def forward(self, x):
        # 1. Attentional Bias (The Surprise Detector)
        if self.variant == "moneta":
            # Lp-norm for strict reasoning stability
            surprise = torch.pow(torch.abs(x), self.p - 1) * torch.sign(x)
        elif self.variant == "yaad":
            # Huber loss for outlier robustness
            surprise = F.huber_loss(x, torch.zeros_like(x), delta=self.delta, reduction="none")
        else:  # memora
            # KL-Divergence for probabilistic stability
            # Assuming x is a log-probability distribution for KL-divergence
            # Comparing to a uniform distribution in log-space
            log_uniform = torch.log(torch.ones_like(x) / x.size(-1))
            surprise = F.kl_div(F.log_softmax(x, dim=-1), log_uniform, reduction="none")

        # 2. Momentum-based Memory Update
        # S_t = momentum * S_{t-1} - eta * Gradient
        with torch.no_grad():
            # Ensure surprise has the correct shape for element-wise multiplication with eta
            # If surprise is (batch_size, d_model), take mean over batch
            if surprise.dim() == 2:
                gradient_estimate = surprise.mean(dim=0)
            else:  # Assuming it's already (d_model,) or (1, d_model)
                gradient_estimate = surprise.squeeze(0) if surprise.dim() == 2 else surprise

            self.S = self.momentum * self.S - self.eta * gradient_estimate

        # 3. Retention Gate (Adaptive Weight Decay)
        retention = torch.sigmoid(self.retention_gate(x))

        # Output is synthetic: Long-term memory synthesized with short-term input
        return self.memory_mlp(x) * retention, surprise
