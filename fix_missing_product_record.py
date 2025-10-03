#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Missing Product Record Error
=================================

This script fixes the "Missing Record" error for product.product(11,)
Error: Record does not exist or has been deleted. (Record: product.product(11,), User: 288)

The script will:
1. Identify all references to the missing product record
2. Find and clean up orphaned references
3. Provide options to replace with valid products or remove references
4. Generate a comprehensive report

Usage:
    python fix_missing_product_record.py [OPTIONS]

Options:
    --product-id ID       Product ID to fix (default: 11)
    --database DB         Database name (default: odoo)
    --fix-mode MODE       Fix mode: report|replace|remove (default: report)
    --replacement-id ID   Replacement product ID (when using replace mode)
"""

import sys
import argparse
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductRecordFixer:
    """Fix missing product.product records and their references"""
    
    def __init__(self, product_id=11, db_name='odoo', fix_mode='report', replacement_id=None):
        self.product_id = product_id
        self.db_name = db_name
        self.fix_mode = fix_mode
        self.replacement_id = replacement_id
        self.issues_found = []
        self.fixes_applied = []
        
    def connect_odoo(self):
        """Connect to Odoo database"""
        try:
            import odoorpc
            odoo = odoorpc.ODOO('localhost', port=8069)
            odoo.login(self.db_name, 'admin', 'admin')
            return odoo
        except ImportError:
            logger.error("odoorpc not installed. Install with: pip install odoorpc")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            return None
    
    def check_product_exists(self, odoo):
        """Check if the product record exists"""
        try:
            Product = odoo.env['product.product']
            product = Product.browse([self.product_id])
            if product.exists():
                logger.info(f"✓ Product {self.product_id} exists: {product.name}")
                return True
            else:
                logger.warning(f"✗ Product {self.product_id} does NOT exist")
                return False
        except Exception as e:
            logger.error(f"Error checking product: {e}")
            return False
    
    def find_references_in_model(self, odoo, model_name, field_name):
        """Find references to the missing product in a specific model"""
        references = []
        try:
            Model = odoo.env[model_name]
            domain = [(field_name, '=', self.product_id)]
            records = Model.search(domain)
            
            if records:
                logger.info(f"Found {len(records)} references in {model_name}.{field_name}")
                for record_id in records:
                    record = Model.browse([record_id])
                    references.append({
                        'model': model_name,
                        'field': field_name,
                        'record_id': record_id,
                        'record_name': getattr(record, 'name', f'Record {record_id}'),
                    })
        except Exception as e:
            logger.debug(f"Could not search {model_name}.{field_name}: {e}")
        
        return references
    
    def find_all_references(self, odoo):
        """Find all references to the missing product across common models"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Searching for references to product.product({self.product_id})")
        logger.info(f"{'='*70}\n")
        
        # Models that commonly reference products
        models_to_check = [
            ('sale.order.line', 'product_id'),
            ('purchase.order.line', 'product_id'),
            ('account.move.line', 'product_id'),
            ('stock.move', 'product_id'),
            ('stock.picking', 'product_id'),
            ('mrp.bom.line', 'product_id'),
            ('product.supplierinfo', 'product_id'),
            ('product.template.attribute.line', 'product_id'),
            ('pack.product', 'product_id'),  # Custom sales kit
            ('product.based.sales.commission', 'product_id'),  # Sales commission
            ('subscription.package.product.line', 'product_id'),  # Subscriptions
            ('product.quantity.wizard.line', 'product_id'),  # AI Agent
            ('maintenance.product.line', 'product_id'),  # Rental management
        ]
        
        all_references = []
        for model_name, field_name in models_to_check:
            refs = self.find_references_in_model(odoo, model_name, field_name)
            all_references.extend(refs)
            self.issues_found.extend(refs)
        
        return all_references
    
    def generate_report(self, references):
        """Generate a detailed report of findings"""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"MISSING PRODUCT RECORD FIX REPORT")
        report.append(f"{'='*70}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Product ID: {self.product_id}")
        report.append(f"Database: {self.db_name}")
        report.append(f"Fix Mode: {self.fix_mode}")
        report.append(f"{'='*70}\n")
        
        if not references:
            report.append("✓ No references found to the missing product.")
            report.append("  The error may be transient or already resolved.")
        else:
            report.append(f"✗ Found {len(references)} references to the missing product:\n")
            
            # Group by model
            by_model = {}
            for ref in references:
                model = ref['model']
                if model not in by_model:
                    by_model[model] = []
                by_model[model].append(ref)
            
            for model, refs in sorted(by_model.items()):
                report.append(f"\n{model} ({len(refs)} records):")
                report.append(f"{'-'*70}")
                for ref in refs[:5]:  # Show first 5
                    report.append(f"  • Record ID: {ref['record_id']} - {ref['record_name']}")
                if len(refs) > 5:
                    report.append(f"  ... and {len(refs) - 5} more records")
        
        report.append(f"\n{'='*70}")
        report.append("RECOMMENDED ACTIONS:")
        report.append(f"{'='*70}")
        
        if references:
            report.append("\n1. REPLACE with valid product:")
            report.append(f"   python fix_missing_product_record.py --fix-mode replace --replacement-id <VALID_PRODUCT_ID>")
            
            report.append("\n2. REMOVE orphaned references:")
            report.append(f"   python fix_missing_product_record.py --fix-mode remove")
            
            report.append("\n3. Use Database Cleanup module in Odoo:")
            report.append("   Settings > Technical > Database Structure > Database Cleanup")
        else:
            report.append("\n✓ No action needed - no references found")
        
        report.append(f"\n{'='*70}\n")
        
        return '\n'.join(report)
    
    def replace_references(self, odoo, references):
        """Replace missing product with a valid product"""
        if not self.replacement_id:
            logger.error("Replacement product ID is required for replace mode")
            return False
        
        # Verify replacement product exists
        Product = odoo.env['product.product']
        replacement = Product.browse([self.replacement_id])
        if not replacement.exists():
            logger.error(f"Replacement product {self.replacement_id} does not exist")
            return False
        
        logger.info(f"\nReplacing product {self.product_id} with {self.replacement_id} ({replacement.name})")
        logger.info(f"{'='*70}\n")
        
        for ref in references:
            try:
                Model = odoo.env[ref['model']]
                record = Model.browse([ref['record_id']])
                if record.exists():
                    record.write({ref['field']: self.replacement_id})
                    logger.info(f"✓ Updated {ref['model']} ID:{ref['record_id']}")
                    self.fixes_applied.append(ref)
            except Exception as e:
                logger.error(f"✗ Failed to update {ref['model']} ID:{ref['record_id']}: {e}")
        
        return True
    
    def remove_references(self, odoo, references):
        """Remove records with references to missing product"""
        logger.info(f"\nRemoving records with references to product {self.product_id}")
        logger.info(f"{'='*70}\n")
        logger.warning("⚠ This will DELETE records. Use with caution!")
        
        # Ask for confirmation
        response = input("\nType 'YES' to confirm deletion: ")
        if response != 'YES':
            logger.info("Deletion cancelled")
            return False
        
        for ref in references:
            try:
                Model = odoo.env[ref['model']]
                record = Model.browse([ref['record_id']])
                if record.exists():
                    record.unlink()
                    logger.info(f"✓ Deleted {ref['model']} ID:{ref['record_id']}")
                    self.fixes_applied.append(ref)
            except Exception as e:
                logger.error(f"✗ Failed to delete {ref['model']} ID:{ref['record_id']}: {e}")
        
        return True
    
    def run(self):
        """Main execution method"""
        logger.info(f"\n{'#'*70}")
        logger.info("#" + " "*68 + "#")
        logger.info("#  Missing Product Record Fixer".ljust(69) + "#")
        logger.info("#" + " "*68 + "#")
        logger.info(f"{'#'*70}\n")
        
        # Try direct SQL connection first (for reporting without Odoo)
        if self.fix_mode == 'report':
            logger.info("Running in REPORT mode (read-only)")
            logger.info("\nNote: For SQL-based analysis, connect to database:")
            logger.info("  docker-compose exec db psql -U odoo -d odoo")
            logger.info("\nThen run these queries:")
            logger.info(f"""
  -- Check if product exists
  SELECT id, name, default_code FROM product_product WHERE id = {self.product_id};
  
  -- Find references in sale orders
  SELECT id, order_id, name FROM sale_order_line WHERE product_id = {self.product_id};
  
  -- Find references in purchase orders
  SELECT id, order_id, name FROM purchase_order_line WHERE product_id = {self.product_id};
  
  -- Find references in account moves
  SELECT id, move_id, name FROM account_move_line WHERE product_id = {self.product_id};
  
  -- Find references in stock moves
  SELECT id, name FROM stock_move WHERE product_id = {self.product_id};
""")
        
        # Try Odoo API connection
        odoo = self.connect_odoo()
        if not odoo:
            logger.warning("\nCould not connect to Odoo API")
            logger.info("Please ensure Odoo is running and odoorpc is installed")
            return False
        
        # Check if product exists
        exists = self.check_product_exists(odoo)
        
        # Find all references
        references = self.find_all_references(odoo)
        
        # Generate report
        report = self.generate_report(references)
        print(report)
        
        # Save report to file
        report_file = f"MISSING_PRODUCT_{self.product_id}_FIX_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"\n✓ Report saved to: {report_file}")
        
        # Apply fixes if requested
        if self.fix_mode == 'replace' and references:
            if self.replace_references(odoo, references):
                logger.info(f"\n✓ Successfully replaced {len(self.fixes_applied)} references")
        elif self.fix_mode == 'remove' and references:
            if self.remove_references(odoo, references):
                logger.info(f"\n✓ Successfully removed {len(self.fixes_applied)} references")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Fix missing product.product record references',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--product-id',
        type=int,
        default=11,
        help='Product ID to fix (default: 11)'
    )
    
    parser.add_argument(
        '--database',
        type=str,
        default='odoo',
        help='Database name (default: odoo)'
    )
    
    parser.add_argument(
        '--fix-mode',
        type=str,
        choices=['report', 'replace', 'remove'],
        default='report',
        help='Fix mode: report (read-only), replace (replace with valid product), remove (delete references)'
    )
    
    parser.add_argument(
        '--replacement-id',
        type=int,
        help='Replacement product ID (required for replace mode)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.fix_mode == 'replace' and not args.replacement_id:
        parser.error("--replacement-id is required when using --fix-mode replace")
    
    # Create and run fixer
    fixer = ProductRecordFixer(
        product_id=args.product_id,
        db_name=args.database,
        fix_mode=args.fix_mode,
        replacement_id=args.replacement_id
    )
    
    try:
        success = fixer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
