// Copyright 2026 ShadowTag-v2. All rights reserved.
// Gideon OS — Midas Monte Carlo Risk Engine Implementation

#include "midas_engine.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <numeric>
#include <thread>

namespace gideon::midas {

MidasEngine::MidasEngine(SimulationConfig config)
    : config_(std::move(config)), rng_(config_.seed) {
  if (config_.thread_count == 0) {
    config_.thread_count = std::thread::hardware_concurrency();
    if (config_.thread_count == 0) config_.thread_count = 1;
  }
}

RiskResult MidasEngine::run(const std::vector<double>& scenarios,
                            const std::vector<double>& probabilities) {
  auto start = std::chrono::high_resolution_clock::now();

  if (scenarios.empty() || scenarios.size() != probabilities.size()) {
    return RiskResult{0.0, 0.0, 0.0, 0.0, 0, 0.0};
  }

  // Normalize probabilities to create a discrete distribution.
  std::discrete_distribution<size_t> dist(probabilities.begin(),
                                          probabilities.end());

  // Run Monte Carlo iterations.
  std::vector<double> losses(config_.num_iterations);
  for (uint64_t i = 0; i < config_.num_iterations; ++i) {
    size_t idx = dist(rng_);
    losses[i] = scenarios[idx];
  }

  // Sort for percentile calculations.
  std::sort(losses.begin(), losses.end());

  // Expected value.
  double sum = std::accumulate(losses.begin(), losses.end(), 0.0);
  double expected = sum / static_cast<double>(config_.num_iterations);

  // Standard deviation.
  double sq_sum = 0.0;
  for (double l : losses) {
    sq_sum += (l - expected) * (l - expected);
  }
  double std_dev =
      std::sqrt(sq_sum / static_cast<double>(config_.num_iterations));

  // VaR at confidence level (e.g., 95th percentile of losses).
  size_t var_idx = static_cast<size_t>(
      config_.confidence_level * static_cast<double>(config_.num_iterations));
  if (var_idx >= config_.num_iterations) var_idx = config_.num_iterations - 1;
  double var_95 = losses[var_idx];

  // CVaR (Expected Shortfall) — average of losses beyond VaR.
  double tail_sum = 0.0;
  size_t tail_count = 0;
  for (size_t i = var_idx; i < config_.num_iterations; ++i) {
    tail_sum += losses[i];
    ++tail_count;
  }
  double cvar_95 = (tail_count > 0) ? tail_sum / static_cast<double>(tail_count)
                                    : var_95;

  auto end = std::chrono::high_resolution_clock::now();
  double elapsed =
      std::chrono::duration<double, std::milli>(end - start).count();

  return RiskResult{expected, var_95, cvar_95, std_dev,
                    config_.num_iterations, elapsed};
}

}  // namespace gideon::midas
