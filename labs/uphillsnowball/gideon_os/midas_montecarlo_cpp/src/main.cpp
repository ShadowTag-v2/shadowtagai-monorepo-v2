// Copyright 2026 ShadowTag-v2. All rights reserved.
// Gideon OS — Midas Monte Carlo Risk Engine CLI Entry Point

#include <cstdio>
#include <vector>

#include "midas_engine.h"

int main() {
  // Example: 5 risk scenarios with associated probabilities.
  std::vector<double> scenarios = {0.0, 10'000.0, 50'000.0, 250'000.0, 1'000'000.0};
  std::vector<double> probabilities = {0.60, 0.20, 0.12, 0.06, 0.02};

  gideon::midas::SimulationConfig config;
  config.num_iterations = 1'000'000;
  config.confidence_level = 0.95;
  config.seed = 42;

  gideon::midas::MidasEngine engine(config);
  auto result = engine.run(scenarios, probabilities);

  std::printf("═══════════════════════════════════════════\n");
  std::printf("  Gideon OS — Midas Monte Carlo Report\n");
  std::printf("═══════════════════════════════════════════\n");
  std::printf("  Iterations:     %llu\n", result.iterations_run);
  std::printf("  Expected Loss:  $%.2f\n", result.expected_value);
  std::printf("  VaR (95%%):      $%.2f\n", result.var_95);
  std::printf("  CVaR (95%%):     $%.2f\n", result.cvar_95);
  std::printf("  Std Dev:        $%.2f\n", result.std_dev);
  std::printf("  Elapsed:        %.2f ms\n", result.elapsed_ms);
  std::printf("═══════════════════════════════════════════\n");

  return 0;
}
