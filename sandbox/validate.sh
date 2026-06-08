#!/usr/bin/env bash

# RanSafe Lane 1 - Baseline Validation Script
# Automated test runner for target microservice and malware simulation.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "===================================================="
echo "🧪 Running Baseline Validation Check..."
echo "===================================================="

# Cleanup any stale processes
echo "Cleaning up any stale nodes or simulation processes..."
pkill -f "node microservice.js" || true
pkill -f "python3 -c.*cpu_burner" || true
rm -rf data/db/*

# Start Target Microservice
echo "1. Starting Target Microservice..."
node microservice.js > microservice.log 2>&1 &
MICROSERVICE_PID=$!
echo "   Microservice started with PID: ${MICROSERVICE_PID}"

# Wait for files to be generated
echo "2. Waiting 8 seconds for organic transaction files to be created..."
sleep 8

echo "   Checking generated files in data/db/:"
ls -lh data/db/

# Show content of one transaction file before attack
first_file=$(find data/db/ -type f -name "*.log" | head -n 1)
if [ -n "${first_file}" ]; then
    echo "   [BEFORE] Content of $(basename "${first_file}"):"
    cat "${first_file}"
else
    echo "❌ ERROR: No transaction logs were generated!"
    kill -9 "${MICROSERVICE_PID}"
    exit 1
fi

# Measure CPU before attack
echo "3. Measuring baseline CPU load..."
if command -v mpstat &> /dev/null; then
    mpstat 1 1 | tail -n 1
else
    # Simple python fallback for cpu load
    python3 -c "
import os, time
t0 = os.times()
time.sleep(0.5)
t1 = os.times()
print(f'   CPU User Time (s): {t1.user - t0.user:.2f}')
"
fi

# Start Malware Simulation
echo "4. Launching Malware Simulation (malware_sim.sh)..."
./malware_sim.sh > malware_sim.log 2>&1 &
MALWARE_PID=$!
echo "   malware_sim.sh running under PID: ${MALWARE_PID}"

# Wait for simulation to execute CPU spiker and encryption
echo "5. Waiting 6 seconds for simulation to take effect..."
sleep 6

# Check CPU utilization during attack
echo "6. Measuring system CPU usage during simulation (should be high)..."
if command -v top &> /dev/null; then
    top -b -n 1 | head -n 15
else
    # Python fallback to show CPU cores load
    python3 -c "
import os, time
print('   Checking CPU activity spikes...')
t0 = os.times()
time.sleep(1)
t1 = os.times()
print(f'   Active user time: {t1.user - t0.user:.2f}s, sys time: {t1.system - t0.system:.2f}s')
"
fi

# Verify Files are Encrypted
echo "7. Inspecting data/db/ directory..."
ls -lh data/db/

# Show content of one file after attack
locked_file=$(find data/db/ -type f -name "*.locked" | head -n 1)
if [ -n "${locked_file}" ]; then
    echo "   [AFTER] Content of $(basename "${locked_file}"):"
    cat "${locked_file}"
    echo "✅ Success: Files successfully encrypted and renamed to .locked!"
else
    echo "❌ ERROR: No .locked files found. Encryption failed!"
    kill -9 "${MICROSERVICE_PID}"
    kill -9 "${MALWARE_PID}"
    exit 1
fi

# Stop simulation and microservice
echo "8. Terminating Simulation..."
kill -15 "${MALWARE_PID}" || true
kill -15 "${MICROSERVICE_PID}" || true
sleep 2

# Verify cleanup
echo "9. Verifying cleanup of spiker processes..."
if pgrep -f "cpu_burner" > /dev/null; then
    echo "⚠️ Warning: Some spiker processes are still active. Force killing them..."
    pkill -9 -f "cpu_burner" || true
else
    echo "✅ Success: All spiker processes terminated successfully."
fi

echo "===================================================="
echo "🎉 Validation Check Completed Successfully!"
echo "===================================================="
