#!/usr/bin/env python3
"""
COA Migration Validation Script
Validates and processes Chart of Accounts migration data for OSUSAPPS (Odoo 17)

Usage:
    python coa_migration_validator.py --validate-balances
    python coa_migration_validator.py --generate-mapping
    python coa_migration_validator.py --export-report
"""

import csv
import json
import argparse
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class COAMigrationValidator:
    """Validates and processes Chart of Accounts migration data"""
    
    def __init__(self):
        self.osus_properties_data = []
        self.legacy_system_data = []
        self.account_mappings = []
        self.validation_errors = []
        self.validation_warnings = []
        
    def load_trial_balance_data(self, file_path: str, system_type: str) -> bool:
        """Load trial balance data from CSV file"""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
                
                if system_type == 'osus_properties':
                    self.osus_properties_data = data
                elif system_type == 'legacy_system':
                    self.legacy_system_data = data
                else:
                    raise ValueError(f"Invalid system type: {system_type}")
                
                logger.info(f"Loaded {len(data)} accounts from {system_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return False
    
    def validate_trial_balance(self, data: List[Dict], system_name: str) -> Tuple[bool, Dict]:
        """Validate that trial balance totals are equal"""
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')
        account_count = len(data)
        
        for account in data:
            try:
                debit = Decimal(account.get('Debit_Balance', '0.00'))
                credit = Decimal(account.get('Credit_Balance', '0.00'))
                
                total_debits += debit
                total_credits += credit
                
                # Validate account has either debit or credit, but not both (significant amounts)
                if debit > 0 and credit > 0:
                    self.validation_warnings.append(
                        f"{system_name}: Account {account.get('Account_Code')} has both debit and credit balances"
                    )
                
            except Exception as e:
                self.validation_errors.append(
                    f"{system_name}: Error processing account {account.get('Account_Code', 'Unknown')}: {str(e)}"
                )
        
        balance_difference = total_debits - total_credits
        is_balanced = abs(balance_difference) < Decimal('0.01')  # Allow for rounding differences
        
        if not is_balanced:
            self.validation_errors.append(
                f"{system_name}: Trial balance does not balance. Difference: ${balance_difference}"
            )
        
        return is_balanced, {
            'total_debits': total_debits,
            'total_credits': total_credits,
            'balance_difference': balance_difference,
            'account_count': account_count,
            'is_balanced': is_balanced
        }
    
    def generate_account_mapping(self) -> List[Dict]:
        """Generate account mapping suggestions based on account names and types"""
        mappings = []
        
        # Define account code ranges for Odoo 17
        account_ranges = {
            'Asset': {
                'cash': (101001, 101999),
                'receivable': (120001, 120999),
                'current': (130001, 139999),
                'prepayments': (140001, 140999),
                'fixed': (150001, 159999)
            },
            'Liability': {
                'payable': (200001, 209999),
                'current': (210001, 219999),
                'non_current': (220001, 229999)
            },
            'Equity': {
                'capital': (300001, 309999),
                'retained': (310001, 319999)
            },
            'Revenue': {
                'income': (400001, 409999),
                'other': (410001, 419999)
            },
            'Expense': {
                'direct_cost': (500001, 509999),
                'operating': (600001, 699999)
            }
        }
        
        # Counter for generating new account codes
        code_counters = defaultdict(int)
        
        # Process OSUS Properties accounts
        for account in self.osus_properties_data:
            mapping = self._create_account_mapping(account, 'OSUS_Properties', account_ranges, code_counters)
            mappings.append(mapping)
        
        # Process Legacy System accounts  
        for account in self.legacy_system_data:
            mapping = self._create_account_mapping(account, 'Legacy_System', account_ranges, code_counters)
            mappings.append(mapping)
        
        self.account_mappings = mappings
        return mappings
    
    def _create_account_mapping(self, account: Dict, source_system: str, 
                               account_ranges: Dict, code_counters: defaultdict) -> Dict:
        """Create individual account mapping"""
        account_type = account.get('Account_Type', '').title()
        account_name = account.get('Account_Name', '')
        legacy_code = account.get('Account_Code', '')
        
        # Determine Odoo account type and range
        odoo_type = self._determine_odoo_account_type(account_type, account_name)
        new_code = self._generate_new_account_code(account_type, account_name, 
                                                  account_ranges, code_counters)
        
        return {
            'source_system': source_system,
            'legacy_code': legacy_code,
            'legacy_name': account_name,
            'new_code': new_code,
            'new_name': self._standardize_account_name(account_name),
            'odoo_account_type': odoo_type,
            'account_category': account_type,
            'notes': f"Migrated from {source_system}"
        }
    
    def _determine_odoo_account_type(self, account_type: str, account_name: str) -> str:
        """Determine appropriate Odoo account type"""
        account_type = account_type.lower()
        account_name = account_name.lower()
        
        type_mapping = {
            'asset': {
                'cash': 'asset_cash',
                'receivable': 'asset_receivable',
                'inventory': 'asset_current',
                'prepaid': 'asset_prepayments',
                'equipment': 'asset_fixed',
                'fixed': 'asset_fixed',
                'depreciation': 'asset_fixed',
                'default': 'asset_current'
            },
            'liability': {
                'payable': 'liability_payable',
                'credit card': 'liability_credit_card',
                'accrued': 'liability_current',
                'notes payable': 'liability_non_current',
                'loan': 'liability_non_current',
                'default': 'liability_current'
            },
            'equity': {
                'stock': 'equity',
                'capital': 'equity',
                'retained': 'equity_unaffected',
                'earnings': 'equity_unaffected',
                'default': 'equity'
            },
            'revenue': {
                'other': 'income_other',
                'default': 'income'
            },
            'expense': {
                'cost of goods': 'expense_direct_cost',
                'depreciation': 'expense_depreciation',
                'default': 'expense'
            }
        }
        
        if account_type in type_mapping:
            category_map = type_mapping[account_type]
            
            # Check for specific keywords in account name
            for keyword, odoo_type in category_map.items():
                if keyword != 'default' and keyword in account_name:
                    return odoo_type
            
            # Return default for category
            return category_map['default']
        
        return 'expense'  # Default fallback
    
    def _generate_new_account_code(self, account_type: str, account_name: str,
                                  account_ranges: Dict, code_counters: defaultdict) -> str:
        """Generate new account code based on type and name"""
        account_type = account_type.title()
        account_name = account_name.lower()
        
        if account_type == 'Asset':
            if 'cash' in account_name:
                base_code = 101001
                key = 'asset_cash'
            elif 'receivable' in account_name:
                base_code = 120001
                key = 'asset_receivable'
            elif 'inventory' in account_name:
                base_code = 130001
                key = 'asset_current'
            elif 'prepaid' in account_name:
                base_code = 140001
                key = 'asset_prepayments'
            elif any(word in account_name for word in ['equipment', 'fixed', 'depreciation']):
                base_code = 150001
                key = 'asset_fixed'
            else:
                base_code = 130001
                key = 'asset_current'
        
        elif account_type == 'Liability':
            if 'payable' in account_name:
                base_code = 200001
                key = 'liability_payable'
            elif any(word in account_name for word in ['accrued', 'current']):
                base_code = 210001
                key = 'liability_current'
            else:
                base_code = 220001
                key = 'liability_non_current'
        
        elif account_type == 'Equity':
            if any(word in account_name for word in ['retained', 'earnings']):
                base_code = 310001
                key = 'equity_retained'
            else:
                base_code = 300001
                key = 'equity_capital'
        
        elif account_type == 'Revenue':
            base_code = 400001
            key = 'revenue'
        
        elif account_type == 'Expense':
            if 'cost of goods' in account_name:
                base_code = 500001
                key = 'expense_cogs'
            else:
                base_code = 600001
                key = 'expense_operating'
        
        else:
            base_code = 600001
            key = 'expense_other'
        
        # Generate unique code
        code_counters[key] += 1
        return str(base_code + code_counters[key] - 1)
    
    def _standardize_account_name(self, name: str) -> str:
        """Standardize account name for consistency"""
        # Remove common prefixes/suffixes and standardize format
        name = name.strip()
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in name.split())
    
    def generate_migration_report(self) -> Dict:
        """Generate comprehensive migration report"""
        # Validate both systems
        osus_balanced, osus_summary = self.validate_trial_balance(
            self.osus_properties_data, "OSUS Properties"
        )
        legacy_balanced, legacy_summary = self.validate_trial_balance(
            self.legacy_system_data, "Legacy System"
        )
        
        # Generate mappings if not already done
        if not self.account_mappings:
            self.generate_account_mapping()
        
        # Calculate combined totals
        combined_debits = osus_summary['total_debits'] + legacy_summary['total_debits']
        combined_credits = osus_summary['total_credits'] + legacy_summary['total_credits']
        combined_accounts = osus_summary['account_count'] + legacy_summary['account_count']
        
        report = {
            'migration_summary': {
                'migration_date': '2025-09-07',
                'source_systems': ['OSUS Properties', 'Legacy System'],
                'target_system': 'OSUSAPPS (Odoo 17)',
                'total_accounts_migrated': combined_accounts,
                'migration_status': 'Completed' if (osus_balanced and legacy_balanced) else 'Issues Found'
            },
            'balance_validation': {
                'osus_properties': osus_summary,
                'legacy_system': legacy_summary,
                'combined_totals': {
                    'total_debits': combined_debits,
                    'total_credits': combined_credits,
                    'total_accounts': combined_accounts,
                    'is_balanced': abs(combined_debits - combined_credits) < Decimal('0.01')
                }
            },
            'account_mappings': self.account_mappings,
            'validation_results': {
                'errors': self.validation_errors,
                'warnings': self.validation_warnings,
                'error_count': len(self.validation_errors),
                'warning_count': len(self.validation_warnings)
            }
        }
        
        return report
    
    def export_report_to_file(self, report: Dict, output_file: str = 'coa_migration_report.json'):
        """Export migration report to JSON file"""
        try:
            # Convert Decimal objects to float for JSON serialization
            def decimal_to_float(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {k: decimal_to_float(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decimal_to_float(item) for item in obj]
                return obj
            
            serializable_report = decimal_to_float(report)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Migration report exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            return False
    
    def export_mappings_to_csv(self, output_file: str = 'account_mappings.csv'):
        """Export account mappings to CSV file"""
        try:
            if not self.account_mappings:
                self.generate_account_mapping()
            
            fieldnames = ['source_system', 'legacy_code', 'legacy_name', 'new_code', 
                         'new_name', 'odoo_account_type', 'account_category', 'notes']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.account_mappings)
            
            logger.info(f"Account mappings exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting mappings: {str(e)}")
            return False

def main():
    """Main function to run COA migration validation"""
    parser = argparse.ArgumentParser(description='COA Migration Validation Tool')
    parser.add_argument('--osus-data', type=str, help='Path to OSUS Properties trial balance CSV')
    parser.add_argument('--legacy-data', type=str, help='Path to Legacy System trial balance CSV')
    parser.add_argument('--validate-balances', action='store_true', help='Validate trial balance totals')
    parser.add_argument('--generate-mapping', action='store_true', help='Generate account mappings')
    parser.add_argument('--export-report', action='store_true', help='Export complete migration report')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory for reports')
    
    args = parser.parse_args()
    
    validator = COAMigrationValidator()
    
    # Load data if provided
    if args.osus_data:
        validator.load_trial_balance_data(args.osus_data, 'osus_properties')
    
    if args.legacy_data:
        validator.load_trial_balance_data(args.legacy_data, 'legacy_system')
    
    # Perform requested operations
    if args.validate_balances:
        if validator.osus_properties_data:
            balanced, summary = validator.validate_trial_balance(
                validator.osus_properties_data, "OSUS Properties"
            )
            print(f"OSUS Properties: {'✓ Balanced' if balanced else '✗ Not Balanced'}")
            print(f"  Total Debits: ${summary['total_debits']}")
            print(f"  Total Credits: ${summary['total_credits']}")
            print(f"  Difference: ${summary['balance_difference']}")
        
        if validator.legacy_system_data:
            balanced, summary = validator.validate_trial_balance(
                validator.legacy_system_data, "Legacy System"
            )
            print(f"Legacy System: {'✓ Balanced' if balanced else '✗ Not Balanced'}")
            print(f"  Total Debits: ${summary['total_debits']}")
            print(f"  Total Credits: ${summary['total_credits']}")
            print(f"  Difference: ${summary['balance_difference']}")
    
    if args.generate_mapping:
        mappings = validator.generate_account_mapping()
        output_file = f"{args.output_dir}/account_mappings.csv"
        validator.export_mappings_to_csv(output_file)
        print(f"Generated {len(mappings)} account mappings")
    
    if args.export_report:
        report = validator.generate_migration_report()
        output_file = f"{args.output_dir}/coa_migration_report.json"
        validator.export_report_to_file(report, output_file)
        
        # Print summary
        print("Migration Report Summary:")
        print(f"  Total Accounts: {report['migration_summary']['total_accounts_migrated']}")
        print(f"  Status: {report['migration_summary']['migration_status']}")
        print(f"  Errors: {report['validation_results']['error_count']}")
        print(f"  Warnings: {report['validation_results']['warning_count']}")
    
    # Print any validation errors or warnings
    if validator.validation_errors:
        print("\nValidation Errors:")
        for error in validator.validation_errors:
            print(f"  ✗ {error}")
    
    if validator.validation_warnings:
        print("\nValidation Warnings:")
        for warning in validator.validation_warnings:
            print(f"  ⚠ {warning}")

if __name__ == "__main__":
    main()
