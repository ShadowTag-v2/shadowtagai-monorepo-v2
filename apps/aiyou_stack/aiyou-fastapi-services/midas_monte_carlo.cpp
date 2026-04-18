#include <vector>
#include <cmath>
#include <algorithm>
#include "mlx/mlx.h"

using namespace mlx::core;

extern "C" {
    // Midas Fast Monte Carlo layer 7 - Retrofitted for Apple Silicon MLX Vector Arrays
    // Computes the 95% Value at Risk (VaR) and dynamic Quarter Kelly criterion
    void run_monte_carlo(double start_price, double volatility, double drift, int steps, int simulations, double* out_var95, double* out_kelly) {

        double dt = 1.0 / 252.0;
        double drift_step = (drift - 0.5 * volatility * volatility) * dt;
        double vol_step = volatility * std::sqrt(dt);

        // 1. MLX Massively Parallel Tensor Math replacing scalar CPU loops
        // Generates the entire [simulations x steps] Brownian motion distribution on the Neural Engine / GPU instantly
        array z = random::normal({simulations, steps}, float32);

        // 2. Compute log return limits natively via broadcast tensors
        array drift_arr = array(drift_step, float32);
        array vol_arr = array(vol_step, float32);
        array log_increments = add(drift_arr, multiply(vol_arr, z));

        // 3. Accumulate sum across time steps (axis 1)
        array total_log_returns = sum(log_increments, 1);

        // 4. Output final prices
        array start_price_arr = array(start_price, float32);
        array final_prices = multiply(start_price_arr, exp(total_log_returns));

        // Compute win/loss limits entirely on NPU
        array win_mask = greater(final_prices, start_price_arr);
        array loss_mask = less_equal(final_prices, start_price_arr);

        array wins_count_arr = sum(win_mask);
        array losses_count_arr = sum(loss_mask);

        array final_over_start = divide(final_prices, start_price_arr);
        array win_multipliers = multiply(win_mask, subtract(final_over_start, array(1.0f, float32)));
        array loss_multipliers = multiply(loss_mask, subtract(array(1.0f, float32), final_over_start));

        array win_sum_arr = sum(win_multipliers);
        array loss_sum_arr = sum(loss_multipliers);

        // MLX NPU Optimization: Sort final prices natively on hardware for VaR checks
        array sorted_final_prices = sort(final_prices, 0);

        // Barrier block to execute lazily evaluated MLX graph on hardware in a single shot
        eval({sorted_final_prices, wins_count_arr, losses_count_arr, win_sum_arr, loss_sum_arr});

        // 5. Port tensor memory back to standard C++ scope for scalar reductions
        const float* sorted_prices_data = sorted_final_prices.data<float>();

        int wins = static_cast<int>(wins_count_arr.item<float>());
        int losses = static_cast<int>(losses_count_arr.item<float>());
        double win_multiplier_avg = static_cast<double>(win_sum_arr.item<float>());
        double loss_multiplier_avg = static_cast<double>(loss_sum_arr.item<float>());

        // Calculate 95% VaR natively off the pre-sorted NPU vector
        int index_95 = static_cast<int>(0.05 * simulations);
        *out_var95 = start_price - static_cast<double>(sorted_prices_data[index_95]);

        // Calculate Quarter Kelly
        if (wins == 0 || losses == 0) {
            *out_kelly = 0.0;
        } else {
            double win_prob = static_cast<double>(wins) / simulations;
            double avg_win = win_multiplier_avg / wins;
            double avg_loss = loss_multiplier_avg / losses;

            double kelly = win_prob - ((1.0 - win_prob) / (avg_win / avg_loss));
            *out_kelly = std::max(0.0, kelly / 4.0); // strictly Quarter Kelly, 0-bounded
        }
    }
}
