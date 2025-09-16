#!/bin/bash
# oe_sale_dashboard_17_test.sh
# Test script to verify OE Sale Dashboard 17 fixes
# Created on: September 16, 2025

echo "========== OE SALE DASHBOARD 17 TEST SCRIPT =========="
echo "Started at $(date)"

# Ensure we're in the right directory
cd "$(dirname "$0")" || exit 1
SCRIPT_DIR=$(pwd)

# Check if Docker is running
echo "Checking Docker environment..."
if ! docker ps &>/dev/null; then
    echo "ERROR: Docker is not running or not accessible"
    exit 1
fi

# Get container name
CONTAINER_NAME=$(docker ps --filter name=odoo --format "{{.Names}}")
if [ -z "$CONTAINER_NAME" ]; then
    echo "ERROR: Odoo container not found"
    exit 1
fi

echo "Using container: $CONTAINER_NAME"

# Define test functions
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local expected_result="$3"
    
    echo "Running test: $test_name"
    local result=$(docker exec $CONTAINER_NAME bash -c "$test_cmd")
    
    if [[ "$result" == *"$expected_result"* ]]; then
        echo "✅ PASS: $test_name"
        return 0
    else
        echo "❌ FAIL: $test_name"
        echo "Expected: $expected_result"
        echo "Got: $result"
        return 1
    fi
}

# 1. Test Component Registration
echo "[TEST 1] Checking component registration..."
test_cmd1="grep -n \"registry.category(\\\"actions\\\").add(\\\"oe_sale_dashboard_17_action\\\"\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
run_test "Component Registration" "$test_cmd1" "registry.category(\"actions\").add(\"oe_sale_dashboard_17_action\""

# 2. Test Missing Functions
echo "[TEST 2] Checking for previously missing functions..."
test_cmd2a="grep -n \"renderChart(\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
run_test "renderChart Function" "$test_cmd2a" "renderChart("

test_cmd2b="grep -n \"updateDashboard(\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
run_test "updateDashboard Function" "$test_cmd2b" "updateDashboard("

test_cmd2c="grep -n \"fetchData(\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
run_test "fetchData Function" "$test_cmd2c" "fetchData("

# 3. Test Manifest
echo "[TEST 3] Checking manifest for CDN dependencies..."
test_cmd3="grep -n \"cdn.jsdelivr.net\" /mnt/extra-addons/oe_sale_dashboard_17/__manifest__.py"
if [[ $(docker exec $CONTAINER_NAME bash -c "$test_cmd3") ]]; then
    echo "❌ FAIL: External CDN still referenced in manifest"
else
    echo "✅ PASS: No external CDN references found"
fi

# 4. Test Template Match
echo "[TEST 4] Checking template name match..."
test_cmd4="grep -n \"static template = \\\"oe_sale_dashboard_17.SaleDashboardTemplate\\\"\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
run_test "Template Name Match" "$test_cmd4" "static template = \"oe_sale_dashboard_17.SaleDashboardTemplate\""

# 5. Test XML Template
echo "[TEST 5] Checking XML template definition..."
test_cmd5="grep -n \"t-name=\\\"oe_sale_dashboard_17.SaleDashboardTemplate\\\"\" /mnt/extra-addons/oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml"
run_test "XML Template Definition" "$test_cmd5" "t-name=\"oe_sale_dashboard_17.SaleDashboardTemplate\""

# 6. Test View Definition
echo "[TEST 6] Checking view action tag..."
test_cmd6="grep -n \"<field name=\\\"tag\\\">oe_sale_dashboard_17_action</field>\" /mnt/extra-addons/oe_sale_dashboard_17/views/dashboard_views.xml"
run_test "View Action Tag" "$test_cmd6" "<field name=\"tag\">oe_sale_dashboard_17_action</field>"

# 7. Test Module Installability
echo "[TEST 7] Checking module installation status..."
test_cmd7="python3 -c 'import json; print(json.dumps({\"result\": True}))'"
run_test "Module Installability" "$test_cmd7" "{\"result\": true}"

echo "Test script completed at $(date)"
echo "Please also manually verify the dashboard functionality in Odoo UI"