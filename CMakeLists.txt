cmake_minimum_required(VERSION 3.20)
project(gideon_os_cpp
  VERSION 1.0.0
  LANGUAGES CXX
  DESCRIPTION "Gideon OS C++ Components — Monte Carlo Risk Engine"
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ──────────────────────────────────────────────────────
# Midas Monte Carlo Risk Engine
# Path: labs/uphillsnowball/gideon_os/midas_montecarlo_cpp/
# ──────────────────────────────────────────────────────
set(MIDAS_SRC_DIR "${CMAKE_SOURCE_DIR}/labs/uphillsnowball/gideon_os/midas_montecarlo_cpp")

if(EXISTS "${MIDAS_SRC_DIR}")
  file(GLOB_RECURSE MIDAS_SOURCES "${MIDAS_SRC_DIR}/src/*.cpp")
  if(MIDAS_SOURCES)
    add_executable(midas_montecarlo ${MIDAS_SOURCES})
    target_include_directories(midas_montecarlo PRIVATE "${MIDAS_SRC_DIR}/include")
    target_compile_options(midas_montecarlo PRIVATE -Wall -Wextra -Wpedantic -O2)
    find_package(Threads REQUIRED)
    target_link_libraries(midas_montecarlo PRIVATE Threads::Threads)
    message(STATUS "Gideon OS: midas_montecarlo_cpp target configured")
  else()
    message(STATUS "Gideon OS: midas_montecarlo_cpp — no sources found yet (scaffold only)")
  endif()
else()
  message(STATUS "Gideon OS: midas_montecarlo_cpp directory not found — skipping")
endif()
