// src/native/core/midas_ipc_client.cpp
//
// Midas C++ Muscle — ZMQ IPC Client ($3B+ Quant Exit)
//
// Bypasses the OS network stack via IPC:// for sub-millisecond
// communication between the C++ quant engine and the Temporal brain.
//
// This is the raw computational muscle: VaR calculations, Monte Carlo
// simulations, and risk attribution that cannot tolerate Python's GIL.
//
// Build: g++ -std=c++17 -o midas_ipc_client midas_ipc_client.cpp -lzmq
// Requirements: libzmq3-dev, nlohmann-json3-dev

#include <zmq.hpp>
#include <iostream>
#include <string>
#include <chrono>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// IPC socket path — bypasses OS network stack entirely
constexpr const char* IPC_ENDPOINT = "ipc:///tmp/pnkln_omega.ipc";

// UCMJ Article 92 timeout: 35 seconds max
constexpr int RECV_TIMEOUT_MS = 35000;

int main(int argc, char* argv[]) {
    zmq::context_t context(1);
    zmq::socket_t socket(context, ZMQ_REQ);
    
    // Set receive timeout (UCMJ Article 92 enforcement)
    socket.set(zmq::sockopt::rcvtimeo, RECV_TIMEOUT_MS);
    socket.connect(IPC_ENDPOINT);

    // Build the request payload
    json payload = {
        {"source", "midas_c++_core"},
        {"event", argc > 1 ? argv[1] : "calculate_var_95"},
        {"model", "gemini-3.1-flash-lite-preview-thinking"},
        {"timestamp", std::chrono::system_clock::now().time_since_epoch().count()}
    };

    std::string payload_str = payload.dump();

    // Send request
    zmq::message_t request(payload_str.size());
    memcpy(request.data(), payload_str.c_str(), payload_str.size());
    
    auto send_start = std::chrono::steady_clock::now();
    socket.send(request, zmq::send_flags::none);

    // Receive response (with UCMJ timeout)
    zmq::message_t reply;
    auto result = socket.recv(reply, zmq::recv_flags::none);
    auto send_end = std::chrono::steady_clock::now();
    
    auto latency_us = std::chrono::duration_cast<std::chrono::microseconds>(
        send_end - send_start
    ).count();

    if (!result.has_value()) {
        std::cerr << "⏰ UCMJ ARTICLE 92: Temporal Brain did not respond within "
                  << RECV_TIMEOUT_MS << "ms. Agent court-martialed." << std::endl;
        return 1;
    }

    std::string response(static_cast<char*>(reply.data()), reply.size());
    std::cout << "🧠 Temporal Brain responded (" << latency_us << "µs): " 
              << response << std::endl;

    return 0;
}
