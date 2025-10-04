#!/usr/bin/env python3
"""
OSUSAPPS Odoo 17 - Security Assessment & Vulnerability Scanner

This specialized script focuses on security analysis for Odoo modules:
- Access control validation
- SQL injection detection
- XSS vulnerability assessment
- CSRF protection verification
- Authentication bypass detection
- Data exposure analysis
"""

import os
import sys
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Set
import csv
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    vulnerability_type: str
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    cwe_id: str  # Common Weakness Enumeration ID
    remediation: str
    osusapps_reference: str = ""

class OdooSecurityScanner:
    """Security-focused scanner for Odoo 17 modules"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.vulnerabilities: List[SecurityVulnerability] = []
        
        # SQL Injection patterns
        self.sql_injection_patterns = [
            r'cr\.execute\s*\(\s*["\'].*%s.*["\'].*%.*\)',  # String formatting in SQL
            r'cr\.execute\s*\(\s*["\'].*\+.*["\'].*\)',      # String concatenation
            r'cr\.execute\s*\(\s*f["\'].*\{.*\}.*["\'].*\)', # f-string in SQL
            r'query\s*=.*%s.*%',                            # Query with % formatting
            r'sql.*\+.*',                                   # SQL concatenation
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<.*\|\s*safe.*>',                             # Jinja2 safe filter
            r'Markup\s*\(',                                 # Direct markup usage
            r'html.*\+.*',                                  # HTML concatenation
            r'format_html.*%s.*%',                          # Unsafe HTML formatting
        ]
        
        # Authentication bypass patterns
        self.auth_bypass_patterns = [
            r'@http\.route.*auth=["\']none["\']',           # No authentication
            r'@http\.route.*csrf=False',                    # CSRF disabled
            r'request\.env\.user\.sudo\(\)',                # Sudo without context
            r'env\.sudo\(\)',                              # Global sudo
        ]
        
        # Dangerous function patterns
        self.dangerous_functions = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
            r'globals\s*\(\)',
            r'locals\s*\(\)',
        ]
        
        # File operation patterns
        self.file_operation_patterns = [
            r'open\s*\([^)]*["\']w["\']',                   # Write operations
            r'os\.remove\s*\(',                             # File deletion
            r'os\.unlink\s*\(',                             # File deletion
            r'shutil\.rmtree\s*\(',                         # Directory deletion
            r'subprocess\.',                                # Process execution
        ]
        
        # Data exposure patterns
        self.data_exposure_patterns = [
            r'password.*=.*request\.',                      # Password in request
            r'api_key.*=.*request\.',                       # API key in request
            r'secret.*=.*request\.',                        # Secret in request
            r'print\s*\(.*password',                        # Password in logs
            r'_logger.*password',                           # Password in logs
        ]
    
    def scan_module(self, module_path: Path) -> List[SecurityVulnerability]:
        """Scan a single module for security vulnerabilities"""
        module_vulnerabilities = []
        
        print(f"🔒 Security scanning: {module_path.name}")
        
        # Scan Python files
        self._scan_python_files(module_path, module_vulnerabilities)
        
        # Scan XML files
        self._scan_xml_files(module_path, module_vulnerabilities)
        
        # Check security configuration
        self._check_security_config(module_path, module_vulnerabilities)
        
        # Check access rights
        self._check_access_rights(module_path, module_vulnerabilities)
        
        self.vulnerabilities.extend(module_vulnerabilities)
        return module_vulnerabilities
    
    def _scan_python_files(self, module_path: Path, vulnerabilities: List[SecurityVulnerability]):
        """Scan Python files for security issues"""
        python_files = list(module_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # SQL Injection detection
                self._check_sql_injection(py_file, content, lines, vulnerabilities)
                
                # XSS detection
                self._check_xss_vulnerabilities(py_file, content, lines, vulnerabilities)
                
                # Authentication bypass
                self._check_auth_bypass(py_file, content, lines, vulnerabilities)
                
                # Dangerous functions
                self._check_dangerous_functions(py_file, content, lines, vulnerabilities)
                
                # File operations
                self._check_file_operations(py_file, content, lines, vulnerabilities)
                
                # Data exposure
                self._check_data_exposure(py_file, content, lines, vulnerabilities)
                
            except Exception as e:
                print(f"⚠️  Error scanning {py_file}: {e}")
    
    def _check_sql_injection(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for SQL injection vulnerabilities"""
        for pattern in self.sql_injection_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                vulnerabilities.append(SecurityVulnerability(
                    severity="CRITICAL",
                    vulnerability_type="SQL_INJECTION",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description="Potential SQL injection vulnerability detected",
                    cwe_id="CWE-89",
                    remediation="Use parameterized queries or ORM methods instead of string formatting",
                    osusapps_reference="Follow safe database patterns from account_statement module"
                ))
    
    def _check_xss_vulnerabilities(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for XSS vulnerabilities"""
        for pattern in self.xss_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                vulnerabilities.append(SecurityVulnerability(
                    severity="HIGH",
                    vulnerability_type="XSS",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description="Potential XSS vulnerability - unsafe HTML rendering",
                    cwe_id="CWE-79",
                    remediation="Properly escape user input and avoid using 'safe' filter unnecessarily",
                    osusapps_reference="Use proper escaping as in payment_account_enhanced views"
                ))
    
    def _check_auth_bypass(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for authentication bypass vulnerabilities"""
        for pattern in self.auth_bypass_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                severity = "CRITICAL" if "auth='none'" in match.group().lower() else "HIGH"
                
                vulnerabilities.append(SecurityVulnerability(
                    severity=severity,
                    vulnerability_type="AUTH_BYPASS",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description="Potential authentication bypass detected",
                    cwe_id="CWE-287",
                    remediation="Ensure proper authentication and CSRF protection",
                    osusapps_reference="Follow authentication patterns from enhanced_rest_api module"
                ))
    
    def _check_dangerous_functions(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for dangerous function usage"""
        for pattern in self.dangerous_functions:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                vulnerabilities.append(SecurityVulnerability(
                    severity="HIGH",
                    vulnerability_type="DANGEROUS_FUNCTION",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description=f"Dangerous function usage: {match.group()}",
                    cwe_id="CWE-94",
                    remediation="Avoid using dangerous functions or implement proper validation",
                    osusapps_reference="Use safe alternatives as demonstrated in existing modules"
                ))
    
    def _check_file_operations(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for potentially dangerous file operations"""
        for pattern in self.file_operation_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                vulnerabilities.append(SecurityVulnerability(
                    severity="MEDIUM",
                    vulnerability_type="FILE_OPERATION",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description="Potentially dangerous file operation detected",
                    cwe_id="CWE-22",
                    remediation="Validate file paths and implement proper access controls",
                    osusapps_reference="Follow file handling patterns from report modules"
                ))
    
    def _check_data_exposure(self, file_path: Path, content: str, lines: List[str], vulnerabilities: List[SecurityVulnerability]):
        """Check for sensitive data exposure"""
        for pattern in self.data_exposure_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                code_snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                
                vulnerabilities.append(SecurityVulnerability(
                    severity="MEDIUM",
                    vulnerability_type="DATA_EXPOSURE",
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=code_snippet,
                    description="Potential sensitive data exposure",
                    cwe_id="CWE-200",
                    remediation="Avoid logging or exposing sensitive data",
                    osusapps_reference="Follow data protection patterns from user management modules"
                ))
    
    def _scan_xml_files(self, module_path: Path, vulnerabilities: List[SecurityVulnerability]):
        """Scan XML files for security issues"""
        xml_files = list(module_path.rglob("*.xml"))
        
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for unsafe JavaScript in views
                js_patterns = [
                    r'<script[^>]*>.*eval\s*\(',
                    r'<script[^>]*>.*innerHTML\s*=',
                    r'onclick\s*=\s*["\'].*eval\s*\(',
                ]
                
                for pattern in js_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        
                        vulnerabilities.append(SecurityVulnerability(
                            severity="HIGH",
                            vulnerability_type="UNSAFE_JAVASCRIPT",
                            file_path=str(xml_file),
                            line_number=line_num,
                            code_snippet=match.group()[:100] + "..." if len(match.group()) > 100 else match.group(),
                            description="Unsafe JavaScript code in XML view",
                            cwe_id="CWE-79",
                            remediation="Use safe JavaScript practices and avoid eval()",
                            osusapps_reference="Follow frontend security patterns from custom_sales module"
                        ))
                
            except Exception as e:
                print(f"⚠️  Error scanning XML {xml_file}: {e}")
    
    def _check_security_config(self, module_path: Path, vulnerabilities: List[SecurityVulnerability]):
        """Check security configuration files"""
        security_dir = module_path / 'security'
        
        if not security_dir.exists():
            vulnerabilities.append(SecurityVulnerability(
                severity="HIGH",
                vulnerability_type="MISSING_SECURITY",
                file_path=str(module_path),
                line_number=0,
                code_snippet="",
                description="Module missing security directory",
                cwe_id="CWE-862",
                remediation="Create security directory with proper access controls",
                osusapps_reference="Follow security structure from payment_account_enhanced"
            ))
            return
        
        # Check for security.xml
        security_xml = security_dir / 'security.xml'
        if security_xml.exists():
            try:
                tree = ET.parse(security_xml)
                root = tree.getroot()
                
                # Check for overly permissive rules
                for rule in root.findall(".//record[@model='ir.rule']"):
                    domain = rule.find(".//field[@name='domain_force']")
                    if domain is not None and domain.text and domain.text.strip() == "[(1,'=',1)]":
                        vulnerabilities.append(SecurityVulnerability(
                            severity="HIGH",
                            vulnerability_type="PERMISSIVE_RULE",
                            file_path=str(security_xml),
                            line_number=0,
                            code_snippet=domain.text,
                            description="Overly permissive security rule detected",
                            cwe_id="CWE-862",
                            remediation="Implement proper domain restrictions",
                            osusapps_reference="Use restrictive rules as in commission modules"
                        ))
                
            except ET.ParseError as e:
                vulnerabilities.append(SecurityVulnerability(
                    severity="MEDIUM",
                    vulnerability_type="XML_PARSE_ERROR",
                    file_path=str(security_xml),
                    line_number=0,
                    code_snippet="",
                    description=f"Security XML parsing error: {e}",
                    cwe_id="CWE-20",
                    remediation="Fix XML syntax in security file",
                    osusapps_reference=""
                ))
    
    def _check_access_rights(self, module_path: Path, vulnerabilities: List[SecurityVulnerability]):
        """Check access rights configuration"""
        access_file = module_path / 'security' / 'ir.model.access.csv'
        
        if not access_file.exists():
            vulnerabilities.append(SecurityVulnerability(
                severity="HIGH",
                vulnerability_type="MISSING_ACCESS_RIGHTS",
                file_path=str(module_path / 'security'),
                line_number=0,
                code_snippet="",
                description="Missing access rights file",
                cwe_id="CWE-862",
                remediation="Create ir.model.access.csv with appropriate permissions",
                osusapps_reference="Follow access patterns from existing modules"
            ))
            return
        
        try:
            with open(access_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, 2):  # Start from 2 (header is 1)
                    # Check for overly permissive access
                    if all(row.get(perm, '0') == '1' for perm in ['perm_read', 'perm_write', 'perm_create', 'perm_unlink']):
                        if 'admin' not in row.get('name', '').lower() and 'manager' not in row.get('name', '').lower():
                            vulnerabilities.append(SecurityVulnerability(
                                severity="MEDIUM",
                                vulnerability_type="OVERPERMISSIVE_ACCESS",
                                file_path=str(access_file),
                                line_number=row_num,
                                code_snippet=f"Group: {row.get('name', 'unknown')}",
                                description="Potentially overpermissive access rights",
                                cwe_id="CWE-732",
                                remediation="Review and restrict permissions as needed",
                                osusapps_reference="Follow principle of least privilege"
                            ))
        
        except Exception as e:
            vulnerabilities.append(SecurityVulnerability(
                severity="MEDIUM",
                vulnerability_type="ACCESS_FILE_ERROR",
                file_path=str(access_file),
                line_number=0,
                code_snippet="",
                description=f"Error reading access rights file: {e}",
                cwe_id="CWE-20",
                remediation="Fix access rights file format",
                osusapps_reference=""
            ))
    
    def generate_security_report(self, output_file: str = None) -> Dict:
        """Generate comprehensive security report"""
        
        # Calculate statistics
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        vulnerability_types = {}
        
        for vuln in self.vulnerabilities:
            severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
            vulnerability_types[vuln.vulnerability_type] = vulnerability_types.get(vuln.vulnerability_type, 0) + 1
        
        # Calculate risk score
        risk_score = (
            severity_counts["CRITICAL"] * 10 +
            severity_counts["HIGH"] * 7 +
            severity_counts["MEDIUM"] * 4 +
            severity_counts["LOW"] * 1
        )
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "risk_score": risk_score,
                "severity_breakdown": severity_counts,
                "vulnerability_types": vulnerability_types
            },
            "vulnerabilities": [asdict(vuln) for vuln in self.vulnerabilities],
            "recommendations": self._generate_security_recommendations(),
            "compliance_status": self._assess_compliance()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"🔒 Security report saved to: {output_file}")
        
        return report
    
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security-specific recommendations"""
        recommendations = []
        
        # Group by vulnerability type
        vuln_counts = {}
        for vuln in self.vulnerabilities:
            vuln_counts[vuln.vulnerability_type] = vuln_counts.get(vuln.vulnerability_type, 0) + 1
        
        # Critical recommendations
        if vuln_counts.get("SQL_INJECTION", 0) > 0:
            recommendations.append(f"🚨 CRITICAL: {vuln_counts['SQL_INJECTION']} SQL injection vulnerabilities - Immediate remediation required")
        
        if vuln_counts.get("AUTH_BYPASS", 0) > 0:
            recommendations.append(f"🚨 CRITICAL: {vuln_counts['AUTH_BYPASS']} authentication bypass issues - Review access controls")
        
        # High priority recommendations
        if vuln_counts.get("XSS", 0) > 0:
            recommendations.append(f"⚠️ HIGH: {vuln_counts['XSS']} XSS vulnerabilities - Implement proper input validation")
        
        if vuln_counts.get("MISSING_SECURITY", 0) > 0:
            recommendations.append(f"⚠️ HIGH: {vuln_counts['MISSING_SECURITY']} modules without security controls")
        
        # Medium priority recommendations
        if vuln_counts.get("DATA_EXPOSURE", 0) > 0:
            recommendations.append(f"⚠️ MEDIUM: {vuln_counts['DATA_EXPOSURE']} potential data exposure issues")
        
        # General recommendations
        total_critical_high = vuln_counts.get("SQL_INJECTION", 0) + vuln_counts.get("AUTH_BYPASS", 0) + vuln_counts.get("XSS", 0)
        
        if total_critical_high > 0:
            recommendations.append("🔒 Implement mandatory security code review process")
            recommendations.append("🔒 Establish security testing in CI/CD pipeline")
        
        if len(self.vulnerabilities) > 20:
            recommendations.append("🔒 Consider implementing static code analysis tools")
        
        return recommendations
    
    def _assess_compliance(self) -> Dict[str, str]:
        """Assess security compliance status"""
        compliance = {}
        
        # OWASP Top 10 assessment
        sql_injection_count = len([v for v in self.vulnerabilities if v.vulnerability_type == "SQL_INJECTION"])
        xss_count = len([v for v in self.vulnerabilities if v.vulnerability_type == "XSS"])
        auth_count = len([v for v in self.vulnerabilities if v.vulnerability_type == "AUTH_BYPASS"])
        
        compliance["OWASP_A03_Injection"] = "FAIL" if sql_injection_count > 0 else "PASS"
        compliance["OWASP_A07_XSS"] = "FAIL" if xss_count > 0 else "PASS"
        compliance["OWASP_A01_Access_Control"] = "FAIL" if auth_count > 0 else "PASS"
        
        # General security posture
        critical_count = len([v for v in self.vulnerabilities if v.severity == "CRITICAL"])
        high_count = len([v for v in self.vulnerabilities if v.severity == "HIGH"])
        
        if critical_count > 0:
            compliance["Overall_Security_Posture"] = "CRITICAL"
        elif high_count > 5:
            compliance["Overall_Security_Posture"] = "POOR"
        elif high_count > 0:
            compliance["Overall_Security_Posture"] = "MODERATE"
        else:
            compliance["Overall_Security_Posture"] = "GOOD"
        
        return compliance
    
    def print_security_summary(self):
        """Print security analysis summary"""
        print("\n" + "="*80)
        print("🔒 OSUSAPPS ODOO 17 - SECURITY VULNERABILITY ASSESSMENT")
        print("="*80)
        
        if not self.vulnerabilities:
            print("✅ No security vulnerabilities detected")
            return
        
        # Severity breakdown
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in self.vulnerabilities:
            severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1
        
        print(f"🚨 Total Vulnerabilities: {len(self.vulnerabilities)}")
        print(f"🚨 Risk Score: {severity_counts['CRITICAL'] * 10 + severity_counts['HIGH'] * 7 + severity_counts['MEDIUM'] * 4 + severity_counts['LOW'] * 1}")
        
        print(f"\n🚨 Severity Breakdown:")
        print(f"   CRITICAL: {severity_counts['CRITICAL']}")
        print(f"   HIGH:     {severity_counts['HIGH']}")
        print(f"   MEDIUM:   {severity_counts['MEDIUM']}")
        print(f"   LOW:      {severity_counts['LOW']}")
        
        # Top vulnerability types
        vuln_types = {}
        for vuln in self.vulnerabilities:
            vuln_types[vuln.vulnerability_type] = vuln_types.get(vuln.vulnerability_type, 0) + 1
        
        print(f"\n🔍 Top Vulnerability Types:")
        sorted_types = sorted(vuln_types.items(), key=lambda x: x[1], reverse=True)
        for vuln_type, count in sorted_types[:5]:
            print(f"   • {vuln_type.replace('_', ' ')}: {count}")
        
        # Critical issues requiring immediate attention
        critical_vulns = [v for v in self.vulnerabilities if v.severity == "CRITICAL"]
        if critical_vulns:
            print(f"\n🚨 CRITICAL Issues Requiring Immediate Attention:")
            for vuln in critical_vulns[:5]:  # Show top 5
                print(f"   • {Path(vuln.file_path).name}:{vuln.line_number} - {vuln.vulnerability_type}")
        
        print("="*80)

def main():
    """Main entry point for security scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OSUSAPPS Odoo 17 Security Vulnerability Scanner")
    parser.add_argument("workspace", help="Path to OSUSAPPS workspace")
    parser.add_argument("--module", help="Scan specific module only")
    parser.add_argument("--output", help="Output JSON report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workspace):
        print(f"❌ Workspace not found: {args.workspace}")
        sys.exit(1)
    
    scanner = OdooSecurityScanner(args.workspace)
    
    if args.module:
        # Scan specific module
        module_path = Path(args.workspace) / args.module
        if not module_path.exists():
            print(f"❌ Module not found: {args.module}")
            sys.exit(1)
        scanner.scan_module(module_path)
    else:
        # Scan all modules
        workspace_path = Path(args.workspace)
        for item in workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and (item / '__manifest__.py').exists():
                try:
                    scanner.scan_module(item)
                except Exception as e:
                    if args.verbose:
                        print(f"⚠️  Security scan error for {item.name}: {e}")
    
    # Display results
    scanner.print_security_summary()
    
    # Generate report
    output_file = args.output or f"security_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    scanner.generate_security_report(output_file)
    
    print(f"\n📄 Security assessment report: {output_file}")
    
    # Exit with error code if critical vulnerabilities found
    critical_count = len([v for v in scanner.vulnerabilities if v.severity == "CRITICAL"])
    if critical_count > 0:
        print(f"🚨 SECURITY ALERT: {critical_count} critical vulnerabilities require immediate attention!")
        sys.exit(1)

if __name__ == "__main__":
    main()