// Copyright 2026 ShadowTag-v2. All rights reserved.
// Gideon OS — Midas Monte Carlo Risk Engine
// C++20 | Thread-safe | SIMD-ready

#ifndef GIDEON_MIDAS_ENGINE_H
#define GIDEON_MIDAS_ENGINE_H

#include <cstdint>
#include <random>
#include <string>
#include <vector>

namespace gideon::midas {

/// Configuration for a Monte Carlo simulation run.
struct SimulationConfig {
  uint64_t num_iterations = 100'000;
  double confidence_level = 0.95;
  uint32_t seed = 42;
  uint32_t thread_count = 0;  // 0 = auto-detect
};

/// Result of a single Monte Carlo risk assessment.
struct RiskResult {
  double expected_value;
  double var_95;    // Value at Risk (95th percentile)
  double cvar_95;   // Conditional VaR (Expected Shortfall)
  double std_dev;
  uint64_t iterations_run;
  double elapsed_ms;
};

/// Monte Carlo Risk Engine — core simulation driver.
class MidasEngine {
 public:
  explicit MidasEngine(SimulationConfig config);
  ~MidasEngine() = default;

  // Non-copyable, moveable.
  MidasEngine(const MidasEngine&) = delete;
  MidasEngine& operator=(const MidasEngine&) = delete;
  MidasEngine(MidasEngine&&) = default;
  MidasEngine& operator=(MidasEngine&&) = default;

  /// Run the Monte Carlo simulation with the given loss distribution.
  /// @param scenarios Vector of scenario loss magnitudes.
  /// @param probabilities Corresponding probability weights.
  /// @return RiskResult with VaR, CVaR, and statistics.
  RiskResult run(const std::vector<double>& scenarios,
                 const std::vector<double>& probabilities);

  /// Get the current configuration.
  const SimulationConfig& config() const { return config_; }

 private:
  SimulationConfig config_;
  std::mt19937_64 rng_;
};

}  // namespace gideon::midas

#endif  // GIDEON_MIDAS_ENGINE_H
