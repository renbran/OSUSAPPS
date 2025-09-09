#!/bin/bash
# Migration Validation and Testing Script
# Companion script for production_ready_migration_script.sh
# Date: 2025-09-07

set -euo pipefail
IFS=$'\n\t'

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Configuration
readonly TARGET_DB="${TARGET_DB:-osusproperties}"
readonly POSTGRES_USER="${POSTGRES_USER:-postgres}"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly VALIDATION_LOG="/var/odoo/validation_${TIMESTAMP}.log"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run validation test
run_validation_test() {
    local test_name="$1"
    local sql_query="$2"
    local expected_result="$3"
    local description="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${BLUE}[TEST $TOTAL_TESTS]${NC} $test_name"
    echo "  Description: $description"
    
    local result=$(sudo -u "$POSTGRES_USER" psql -d "$TARGET_DB" -t -c "$sql_query" 2>/dev/null | tr -d ' ')
    
    if [[ "$result" == "$expected_result" ]]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "  Result: ${GREEN}PASS${NC} (Expected: $expected_result, Got: $result)"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "  Result: ${RED}FAIL${NC} (Expected: $expected_result, Got: $result)"
    fi
    
    echo "  Query: $sql_query"
    echo
}

# Function to validate account mappings
validate_account_mappings() {
    echo -e "${YELLOW}=== ACCOUNT MAPPING VALIDATION ===${NC}"
    
    # Test 1: Verify all expected accounts were mapped
    run_validation_test \
        "Account Mapping Completeness" \
        "SELECT COUNT(*) FROM account_migration_log WHERE status = 'COMPLETED';" \
        "73" \
        "Verify all 73 expected accounts were successfully mapped"
    
    # Test 2: No duplicate account codes
    run_validation_test \
        "Account Code Uniqueness" \
        "SELECT COUNT(*) - COUNT(DISTINCT code) FROM account_account WHERE active = true;" \
        "0" \
        "Ensure no duplicate account codes exist after migration"
    
    # Test 3: Revenue accounts properly mapped
    run_validation_test \
        "Revenue Account Mapping" \
        "SELECT COUNT(*) FROM account_account WHERE code LIKE '401%' AND active = true;" \
        "7" \
        "Verify all 7 revenue accounts mapped to 401xx range"
    
    # Test 4: Cost accounts properly mapped
    run_validation_test \
        "Cost Account Mapping" \
        "SELECT COUNT(*) FROM account_account WHERE code LIKE '50%' AND active = true;" \
        "7" \
        "Verify cost of sales accounts mapped to 50xxx range"
    
    # Test 5: Asset accounts properly mapped
    run_validation_test \
        "Asset Account Mapping" \
        "SELECT COUNT(*) FROM account_account WHERE code LIKE '1%' AND active = true;" \
        "20" \
        "Verify asset accounts mapped to 1xxxx range"
}

# Function to validate trial balance
validate_trial_balance() {
    echo -e "${YELLOW}=== TRIAL BALANCE VALIDATION ===${NC}"
    
    # Test 6: Trial balance is balanced
    run_validation_test \
        "Trial Balance Equality" \
        "SELECT CASE WHEN ABS(COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0)) < 0.01 THEN 'BALANCED' ELSE 'UNBALANCED' END FROM account_move_line aml JOIN account_move am ON aml.move_id = am.id WHERE am.state = 'posted';" \
        "BALANCED" \
        "Verify total debits equal total credits in posted entries"
    
    # Test 7: No negative balances in asset accounts
    run_validation_test \
        "Asset Account Balances" \
        "SELECT COUNT(*) FROM (SELECT SUM(debit - credit) as balance FROM account_move_line aml JOIN account_account aa ON aml.account_id = aa.id JOIN account_account_type aat ON aa.account_type = aat.id WHERE aat.name LIKE '%Asset%' GROUP BY aa.id HAVING SUM(debit - credit) < 0) negative_assets;" \
        "0" \
        "Ensure no asset accounts have negative balances"
    
    # Test 8: Journal entries count preserved
    local original_count=$(sudo -u "$POSTGRES_USER" psql -d "erposus" -t -c "SELECT COUNT(*) FROM account_move_line;" 2>/dev/null || echo "0")
    run_validation_test \
        "Journal Entry Preservation" \
        "SELECT COUNT(*) FROM account_move_line;" \
        "$original_count" \
        "Verify all journal entries were preserved during migration"
}

# Function to validate data integrity
validate_data_integrity() {
    echo -e "${YELLOW}=== DATA INTEGRITY VALIDATION ===${NC}"
    
    # Test 9: All accounts have valid account types
    run_validation_test \
        "Account Type Validity" \
        "SELECT COUNT(*) FROM account_account WHERE account_type IS NULL AND active = true;" \
        "0" \
        "Ensure all active accounts have valid account types"
    
    # Test 10: No orphaned account move lines
    run_validation_test \
        "Account Move Line Integrity" \
        "SELECT COUNT(*) FROM account_move_line aml LEFT JOIN account_account aa ON aml.account_id = aa.id WHERE aa.id IS NULL;" \
        "0" \
        "Verify no orphaned account move lines exist"
    
    # Test 11: Currency consistency
    run_validation_test \
        "Currency Consistency" \
        "SELECT COUNT(DISTINCT currency_id) FROM account_move_line WHERE currency_id IS NOT NULL;" \
        "1" \
        "Verify currency consistency across all transactions"
    
    # Test 12: Account reconciliation integrity
    run_validation_test \
        "Reconciliation Integrity" \
        "SELECT COUNT(*) FROM account_partial_reconcile apr LEFT JOIN account_move_line aml1 ON apr.debit_move_id = aml1.id LEFT JOIN account_move_line aml2 ON apr.credit_move_id = aml2.id WHERE aml1.id IS NULL OR aml2.id IS NULL;" \
        "0" \
        "Ensure all reconciliations reference valid move lines"
}

# Function to validate business logic
validate_business_logic() {
    echo -e "${YELLOW}=== BUSINESS LOGIC VALIDATION ===${NC}"
    
    # Test 13: Revenue recognition consistency
    run_validation_test \
        "Revenue Account Usage" \
        "SELECT CASE WHEN COUNT(*) > 0 THEN 'USED' ELSE 'UNUSED' END FROM account_move_line aml JOIN account_account aa ON aml.account_id = aa.id WHERE aa.code LIKE '401%';" \
        "USED" \
        "Verify revenue accounts are actually being used in transactions"
    
    # Test 14: Cost allocation consistency
    run_validation_test \
        "Cost Account Usage" \
        "SELECT CASE WHEN COUNT(*) > 0 THEN 'USED' ELSE 'UNUSED' END FROM account_move_line aml JOIN account_account aa ON aml.account_id = aa.id WHERE aa.code LIKE '50%';" \
        "USED" \
        "Verify cost accounts are being used appropriately"
    
    # Test 15: Bank account validation
    run_validation_test \
        "Bank Account Setup" \
        "SELECT COUNT(*) FROM account_account WHERE code LIKE '101%' AND active = true;" \
        "3" \
        "Verify all bank accounts (ADCB, ENBD, Alaan) are properly set up"
}

# Function to validate system performance
validate_performance() {
    echo -e "${YELLOW}=== PERFORMANCE VALIDATION ===${NC}"
    
    # Test 16: Database size check
    local db_size=$(sudo -u "$POSTGRES_USER" psql -d "$TARGET_DB" -t -c "SELECT pg_size_pretty(pg_database_size('$TARGET_DB'));" | tr -d ' ')
    echo -e "${BLUE}[INFO]${NC} Database Size: $db_size"
    
    # Test 17: Index integrity
    run_validation_test \
        "Index Integrity" \
        "SELECT COUNT(*) FROM pg_stat_user_indexes WHERE schemaname = 'public' AND idx_scan = 0 AND indexrelname LIKE '%account%';" \
        "0" \
        "Check that account-related indexes are being used"
    
    # Test 18: Query performance test
    local query_time=$(sudo -u "$POSTGRES_USER" psql -d "$TARGET_DB" -c "\timing on" -c "SELECT COUNT(*) FROM account_move_line;" 2>&1 | grep "Time:" | awk '{print $2}' | tr -d 'ms')
    echo -e "${BLUE}[INFO]${NC} Account Move Line Query Time: ${query_time}ms"
}

# Function to generate validation report
generate_validation_report() {
    echo -e "${YELLOW}=== VALIDATION SUMMARY ===${NC}"
    echo
    echo "Total Tests Run: $TOTAL_TESTS"
    echo -e "Tests Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Tests Failed: ${RED}$FAILED_TESTS${NC}"
    echo
    
    local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: $success_rate%"
    echo
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}✅ ALL VALIDATION TESTS PASSED${NC}"
        echo "Migration validation completed successfully!"
        return 0
    elif [[ $FAILED_TESTS -lt 3 ]]; then
        echo -e "${YELLOW}⚠️  MINOR ISSUES DETECTED${NC}"
        echo "Migration mostly successful but review failed tests"
        return 1
    else
        echo -e "${RED}❌ SIGNIFICANT ISSUES DETECTED${NC}"
        echo "Migration has serious issues - consider rollback"
        return 2
    fi
}

# Function to run specific account code validation
validate_specific_mappings() {
    echo -e "${YELLOW}=== SPECIFIC ACCOUNT CODE VALIDATION ===${NC}"
    
    # Create array of critical mappings to verify
    local mappings=(
        "1001:40101:Revenue - Exclusive Dubai Sales"
        "2008:51001:Internal Commission - RM/SM/CXO"
        "4003:10101:ADCB Bank - Main Operating Account"
        "5001:21001:Accounts Payable - Trade"
        "6001:30101:Share Capital - Partner 1"
        "3021:60101:Salaries and Wages - Basic"
    )
    
    for mapping in "${mappings[@]}"; do
        IFS=':' read -r old_code new_code expected_name <<< "$mapping"
        
        run_validation_test \
            "Mapping $old_code → $new_code" \
            "SELECT name FROM account_account WHERE code = '$new_code' AND active = true;" \
            "$expected_name" \
            "Verify $old_code mapped correctly to $new_code with proper name"
    done
}

# Main validation function
main() {
    echo "================================================================================"
    echo -e "${GREEN}MIGRATION VALIDATION SUITE${NC}"
    echo "================================================================================"
    echo "Target Database: $TARGET_DB"
    echo "Timestamp: $TIMESTAMP"
    echo "Log File: $VALIDATION_LOG"
    echo
    
    # Check if target database exists
    if ! sudo -u "$POSTGRES_USER" psql -lqt | cut -d \| -f 1 | grep -qw "$TARGET_DB"; then
        echo -e "${RED}ERROR: Target database '$TARGET_DB' does not exist${NC}"
        exit 1
    fi
    
    # Check if migration log table exists (indicates migration was run)
    if ! sudo -u "$POSTGRES_USER" psql -d "$TARGET_DB" -c "SELECT 1 FROM account_migration_log LIMIT 1;" >/dev/null 2>&1; then
        echo -e "${YELLOW}WARNING: Migration log table not found - was migration script run?${NC}"
    fi
    
    # Run validation test suites
    validate_account_mappings
    validate_trial_balance
    validate_data_integrity
    validate_business_logic
    validate_specific_mappings
    validate_performance
    
    # Generate final report
    echo
    echo "================================================================================"
    generate_validation_report
    echo "================================================================================"
    
    # Log results
    {
        echo "Validation completed at $(date)"
        echo "Total Tests: $TOTAL_TESTS"
        echo "Passed: $PASSED_TESTS"
        echo "Failed: $FAILED_TESTS"
        echo "Success Rate: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"
    } >> "$VALIDATION_LOG"
    
    return $FAILED_TESTS
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit $?
fi
