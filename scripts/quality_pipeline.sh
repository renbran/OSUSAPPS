#!/bin/bash
# OSUSAPPS Odoo 17 - Automated Code Quality Testing Pipeline
# This script runs comprehensive code quality checks and generates reports

set -e  # Exit on any error

# Configuration
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$WORKSPACE_DIR/scripts"
REPORTS_DIR="$WORKSPACE_DIR/quality_reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create reports directory
mkdir -p "$REPORTS_DIR"

log "🚀 Starting OSUSAPPS Code Quality Pipeline"
log "📁 Workspace: $WORKSPACE_DIR"
log "📄 Reports: $REPORTS_DIR"

# Check if Python scripts exist
if [[ ! -f "$SCRIPTS_DIR/code_quality_analyzer.py" ]]; then
    error "Code quality analyzer script not found!"
    exit 1
fi

if [[ ! -f "$SCRIPTS_DIR/security_scanner.py" ]]; then
    error "Security scanner script not found!"
    exit 1
fi

# Initialize variables for summary
total_modules=0
passed_modules=0
failed_modules=0
critical_issues=0
high_issues=0
security_vulnerabilities=0
overall_score=0

# Create a summary report
summary_file="$REPORTS_DIR/quality_pipeline_summary_$TIMESTAMP.md"

cat > "$summary_file" << EOF
# 🔍 OSUSAPPS Code Quality Pipeline Report

**Generated:** $(date)
**Workspace:** $WORKSPACE_DIR
**Pipeline Version:** 1.0

## 📊 Executive Summary

EOF

# Run Code Quality Analysis
log "🔍 Running comprehensive code quality analysis..."
quality_report="$REPORTS_DIR/code_quality_$TIMESTAMP.json"

if python3 "$SCRIPTS_DIR/code_quality_analyzer.py" "$WORKSPACE_DIR" --output "$quality_report" --verbose; then
    success "Code quality analysis completed"
    
    # Extract metrics from JSON report
    if command -v jq &> /dev/null; then
        total_modules=$(jq '.summary.total_modules' "$quality_report")
        overall_score=$(jq '.summary.average_score' "$quality_report")
        critical_issues=$(jq '.summary.severity_breakdown.CRITICAL' "$quality_report")
        high_issues=$(jq '.summary.severity_breakdown.HIGH' "$quality_report")
        
        log "📊 Modules analyzed: $total_modules"
        log "⭐ Average quality score: $overall_score"
        log "🚨 Critical issues: $critical_issues"
        log "⚠️  High priority issues: $high_issues"
    else
        warning "jq not installed - skipping JSON parsing"
    fi
else
    error "Code quality analysis failed"
    exit 1
fi

# Run Security Scan
log "🔒 Running security vulnerability assessment..."
security_report="$REPORTS_DIR/security_assessment_$TIMESTAMP.json"

if python3 "$SCRIPTS_DIR/security_scanner.py" "$WORKSPACE_DIR" --output "$security_report" --verbose; then
    success "Security assessment completed"
    
    # Extract security metrics
    if command -v jq &> /dev/null; then
        security_vulnerabilities=$(jq '.summary.total_vulnerabilities' "$security_report")
        log "🛡️  Security vulnerabilities found: $security_vulnerabilities"
    fi
else
    warning "Security scan completed with issues - check report"
fi

# Run Module-specific Tests
log "🧪 Running module-specific quality tests..."

# Find all modules
module_count=0
for module_dir in "$WORKSPACE_DIR"/*; do
    if [[ -d "$module_dir" && -f "$module_dir/__manifest__.py" ]]; then
        module_name=$(basename "$module_dir")
        
        # Skip hidden directories and non-modules
        if [[ "$module_name" == .* ]]; then
            continue
        fi
        
        log "🔍 Testing module: $module_name"
        ((module_count++))
        
        # Run module-specific tests
        module_passed=true
        
        # Check manifest file
        if python3 -c "
import ast
import sys
try:
    with open('$module_dir/__manifest__.py', 'r') as f:
        manifest = ast.literal_eval(f.read())
    required_fields = ['name', 'version', 'author', 'category', 'depends']
    missing = [f for f in required_fields if f not in manifest]
    if missing:
        print(f'Missing required fields: {missing}')
        sys.exit(1)
    print('Manifest validation passed')
except Exception as e:
    print(f'Manifest validation failed: {e}')
    sys.exit(1)
"; then
            log "✅ $module_name: Manifest validation passed"
        else
            warning "❌ $module_name: Manifest validation failed"
            module_passed=false
        fi
        
        # Check security directory
        if [[ -d "$module_dir/security" ]]; then
            log "✅ $module_name: Security directory exists"
        else
            warning "⚠️  $module_name: Missing security directory"
            module_passed=false
        fi
        
        # Check for Python syntax errors
        python_files_with_errors=0
        while IFS= read -r -d '' py_file; do
            if ! python3 -m py_compile "$py_file" 2>/dev/null; then
                error "❌ $module_name: Syntax error in $(basename "$py_file")"
                ((python_files_with_errors++))
                module_passed=false
            fi
        done < <(find "$module_dir" -name "*.py" -print0)
        
        if [[ $python_files_with_errors -eq 0 ]]; then
            log "✅ $module_name: Python syntax validation passed"
        fi
        
        # Check XML files
        xml_files_with_errors=0
        while IFS= read -r -d '' xml_file; do
            if ! xmllint --noout "$xml_file" 2>/dev/null; then
                error "❌ $module_name: XML error in $(basename "$xml_file")"
                ((xml_files_with_errors++))
                module_passed=false
            fi
        done < <(find "$module_dir" -name "*.xml" -print0)
        
        if [[ $xml_files_with_errors -eq 0 ]]; then
            log "✅ $module_name: XML validation passed"
        fi
        
        # Update counters
        if $module_passed; then
            ((passed_modules++))
        else
            ((failed_modules++))
        fi
    fi
done

total_modules=$module_count

# Generate Quality Dashboard
log "📊 Generating quality dashboard..."
if python3 "$SCRIPTS_DIR/quality_dashboard.py" "$WORKSPACE_DIR" --output "$REPORTS_DIR/quality_dashboard_$TIMESTAMP.html" --update; then
    success "Quality dashboard generated"
else
    warning "Dashboard generation failed"
fi

# Calculate pass rate
if [[ $total_modules -gt 0 ]]; then
    pass_rate=$((100 * passed_modules / total_modules))
else
    pass_rate=0
fi

# Determine overall status
overall_status="UNKNOWN"
status_color="$BLUE"

if [[ $critical_issues -gt 0 ]]; then
    overall_status="CRITICAL"
    status_color="$RED"
elif [[ $high_issues -gt 5 || $security_vulnerabilities -gt 10 ]]; then
    overall_status="POOR"
    status_color="$RED"
elif [[ $pass_rate -lt 70 ]]; then
    overall_status="NEEDS_IMPROVEMENT"
    status_color="$YELLOW"
elif [[ $pass_rate -lt 90 ]]; then
    overall_status="GOOD"
    status_color="$GREEN"
else
    overall_status="EXCELLENT"
    status_color="$GREEN"
fi

# Complete summary report
cat >> "$summary_file" << EOF
| Metric | Value |
|--------|-------|
| Total Modules | $total_modules |
| Modules Passed | $passed_modules |
| Modules Failed | $failed_modules |
| Pass Rate | $pass_rate% |
| Overall Quality Score | $overall_score/100 |
| Critical Issues | $critical_issues |
| High Priority Issues | $high_issues |
| Security Vulnerabilities | $security_vulnerabilities |
| **Overall Status** | **$overall_status** |

## 📋 Module Test Results

| Module | Status | Issues |
|--------|--------|--------|
EOF

# Add module results to summary (this would be populated during the module loop)
echo "| Summary | $passed_modules passed, $failed_modules failed | Total issues found |" >> "$summary_file"

cat >> "$summary_file" << EOF

## 📄 Generated Reports

- **Code Quality Analysis**: \`$(basename "$quality_report")\`
- **Security Assessment**: \`$(basename "$security_report")\`
- **Quality Dashboard**: \`quality_dashboard_$TIMESTAMP.html\`

## 🔄 Recommendations

EOF

# Generate recommendations based on results
if [[ $critical_issues -gt 0 ]]; then
    echo "- 🚨 **URGENT**: Address $critical_issues critical issues immediately" >> "$summary_file"
fi

if [[ $security_vulnerabilities -gt 0 ]]; then
    echo "- 🔒 **SECURITY**: Review and fix $security_vulnerabilities security vulnerabilities" >> "$summary_file"
fi

if [[ $pass_rate -lt 80 ]]; then
    echo "- 📈 **QUALITY**: Improve module quality - current pass rate is $pass_rate%" >> "$summary_file"
fi

if [[ $overall_score -lt 75 ]]; then
    echo "- ⭐ **STANDARDS**: Focus on code quality improvement - current score is $overall_score/100" >> "$summary_file"
fi

echo "- 📊 **MONITORING**: Set up continuous quality monitoring" >> "$summary_file"
echo "- 🧪 **TESTING**: Implement automated testing for critical modules" >> "$summary_file"

cat >> "$summary_file" << EOF

## 🎯 Next Steps

1. **Immediate Actions**
   - Review and address critical issues
   - Fix security vulnerabilities
   - Validate failing modules

2. **Short-term Goals**
   - Improve overall quality score to >80
   - Achieve >90% module pass rate
   - Implement missing security controls

3. **Long-term Strategy**
   - Establish quality gates in CI/CD
   - Regular security assessments
   - Performance optimization initiatives

---

**Pipeline executed on:** $(date)
**Total execution time:** \$((SECONDS/60)) minutes
**Next scheduled run:** $(date -d "+1 day" +"%Y-%m-%d %H:%M:%S")

EOF

# Final summary
log "📋 Pipeline Summary:"
log "   Modules: $total_modules total, $passed_modules passed, $failed_modules failed"
log "   Quality Score: $overall_score/100"
log "   Critical Issues: $critical_issues"
log "   Security Vulnerabilities: $security_vulnerabilities"
echo -e "   Overall Status: ${status_color}$overall_status${NC}"

success "✅ Quality pipeline completed successfully!"
log "📄 Summary report: $summary_file"
log "📊 Quality dashboard: $REPORTS_DIR/quality_dashboard_$TIMESTAMP.html"

# Set exit code based on overall status
case $overall_status in
    "CRITICAL"|"POOR")
        exit 1
        ;;
    "NEEDS_IMPROVEMENT")
        exit 2
        ;;
    *)
        exit 0
        ;;
esac