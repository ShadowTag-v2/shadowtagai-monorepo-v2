// src/finance/midas_montecarlo.cpp
// ============================================================================
// Midas Monte Carlo — Compute-to-Data Shift (95% VaR)
// ============================================================================
// Block 6 of the Ex Toto Omni-Compile (Gideon OS Architecture)
// Serverless parallel execution calculating 95% VaR via Quarter Kelly.
// Dependencies: httplib.h, nlohmann/json.hpp
// ============================================================================
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include "httplib.h"
#include "json.hpp"

using json = nlohmann::json;

int main() {
    httplib::Server svr;

    svr.Post("/simulate", [](const httplib::Request& req, httplib::Response& res) {
        auto data = json::parse(req.body);
        std::vector<double> paths = data["kronos_paths"];
        std::sort(paths.begin(), paths.end());

        double total = 0.0;
        for (double p : paths) total += p;
        double expected = total / paths.size();
        double var95 = -(paths[int(0.05 * paths.size())] - paths[0]) / paths[0];
        double quarter_kelly = (expected / std::max(0.01, var95)) * 0.25;

        json response = {
            {"expected_return", expected},
            {"var_95", var95},
            {"quarter_kelly", quarter_kelly}
        };
        res.set_content(response.dump(), "application/json");
    });

    const char* port_env = std::getenv("PORT");
    int port = port_env ? std::atoi(port_env) : 8080;
    svr.listen("0.0.0.0", port);
    return 0;
}
