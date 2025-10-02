#!/usr/bin/env python3
"""
Fix script for missing external ID: rental_management.property_payment_plan_action

This script helps resolve the missing external ID issue by:
1. Checking if the external ID exists in ir.model.data
2. Recreating it if missing
3. Verifying the associated action record exists

Usage:
- Run this via Odoo shell: odoo-bin shell -d your_database < fix_payment_plan_action.py
- Or execute in Odoo backend via developer mode
"""

import logging

_logger = logging.getLogger(__name__)

def fix_payment_plan_action_external_id():
    """Fix the missing external ID for property_payment_plan_action"""
    
    try:
        # Check if the external ID exists
        external_id_domain = [
            ('module', '=', 'rental_management'),
            ('name', '=', 'property_payment_plan_action')
        ]
        
        existing_external_id = env['ir.model.data'].search(external_id_domain)
        
        if existing_external_id:
            _logger.info("External ID rental_management.property_payment_plan_action already exists")
            action_id = existing_external_id.res_id
        else:
            _logger.info("External ID rental_management.property_payment_plan_action not found, checking for action...")
            
            # Look for the action by name and model
            action_domain = [
                ('name', '=', 'Payment Plan Templates'),
                ('res_model', '=', 'property.payment.plan'),
                ('type', '=', 'ir.actions.act_window')
            ]
            
            existing_action = env['ir.actions.act_window'].search(action_domain, limit=1)
            
            if existing_action:
                _logger.info(f"Found existing action with ID {existing_action.id}, creating external ID...")
                action_id = existing_action.id
            else:
                _logger.info("No existing action found, creating new one...")
                
                # Create the action
                action_vals = {
                    'name': 'Payment Plan Templates',
                    'type': 'ir.actions.act_window',
                    'res_model': 'property.payment.plan',
                    'view_mode': 'tree,form',
                    'context': '{}',
                    'domain': '[]',
                    'help': """<p class="o_view_nocontent_smiling_face">
                        Create a Payment Plan Template
                    </p>
                    <p>
                        Define reusable payment plan templates for properties.<br/>
                        Example: 10% Booking, 10% after 30 days, 15% on construction, etc.
                    </p>"""
                }
                
                new_action = env['ir.actions.act_window'].create(action_vals)
                action_id = new_action.id
                _logger.info(f"Created new action with ID {action_id}")
            
            # Create the external ID
            external_id_vals = {
                'module': 'rental_management',
                'name': 'property_payment_plan_action',
                'model': 'ir.actions.act_window',
                'res_id': action_id,
            }
            
            env['ir.model.data'].create(external_id_vals)
            _logger.info(f"Created external ID rental_management.property_payment_plan_action for action ID {action_id}")
        
        # Verify the fix
        try:
            action_ref = env.ref('rental_management.property_payment_plan_action')
            _logger.info(f"✅ Fix successful! Action can now be referenced: {action_ref}")
            return True
        except Exception as e:
            _logger.error(f"❌ Fix failed - action still cannot be referenced: {e}")
            return False
            
    except Exception as e:
        _logger.error(f"❌ Error during fix: {e}")
        return False

def check_payment_plan_model():
    """Verify that the property.payment.plan model exists and is accessible"""
    try:
        model = env['property.payment.plan']
        count = model.search_count([])
        _logger.info(f"✅ Model property.payment.plan exists and contains {count} records")
        return True
    except Exception as e:
        _logger.error(f"❌ Model property.payment.plan not accessible: {e}")
        return False

if __name__ == '__main__':
    _logger.info("=== Starting Payment Plan Action Fix ===")
    
    # Check model first
    model_ok = check_payment_plan_model()
    if not model_ok:
        _logger.error("Cannot proceed - model is not accessible")
        exit(1)
    
    # Fix the external ID
    fix_ok = fix_payment_plan_action_external_id()
    
    if fix_ok:
        _logger.info("=== Fix completed successfully ===")
        # Commit the transaction
        env.cr.commit()
    else:
        _logger.error("=== Fix failed ===")