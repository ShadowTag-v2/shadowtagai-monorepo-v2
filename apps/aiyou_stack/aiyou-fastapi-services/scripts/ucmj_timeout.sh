#!/bin/bash
# UCMJ Timeout Wrapper
# Usage: ./ucmj_timeout.sh <timeout_seconds> <command> [args...]

TIMEOUT_SEC=$1
shift
CMD="$@"

echo ">>> [UCMJ] Starting command: '$CMD' with timeout ${TIMEOUT_SEC}s"

# Run with timeout
timeout "${TIMEOUT_SEC}s" $CMD
EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "!!! [UCMJ VIOLATION] COMMAND TIMED OUT !!!"
    echo "!!! DRAG RACE LIGHT BAR: RED !!!"
    echo "!!! The agent failed to complete the mission in time. !!!"
    exit 124
elif [ $EXIT_CODE -ne 0 ]; then
    echo "!!! [UCMJ FAILURE] Command failed with exit code $EXIT_CODE !!!"
    exit $EXIT_CODE
else
    echo ">>> [UCMJ] Mission Accomplished."
    exit 0
fi
