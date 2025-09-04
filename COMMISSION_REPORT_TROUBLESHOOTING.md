# Commission Statement Report - Installation and Setup Guide

## Current Issue: "No commission data found for the selected criteria"

### Quick Diagnosis Steps:

1. **Check if commission_ax module is installed:**
   - Go to Apps menu
   - Search for "commission_ax" 
   - Ensure it's installed (not just "commission_statement")

2. **Verify module dependencies:**
   - commission_statement module depends on commission_ax
   - Both modules must be installed for reports to work

3. **Check sale orders:**
   - Ensure there are confirmed sale orders (state = 'sale' or 'done') in the selected date range
   - Ensure sale orders have commission data populated (partners assigned to commission fields)

4. **Commission fields required:**
   The report looks for these fields on sale orders:
   - consultant_id, manager_id, director_id (legacy commissions)  
   - broker_partner_id, referrer_partner_id, etc. (external commissions)
   - agent1_partner_id, agent2_partner_id, etc. (internal commissions)

### Installation Order:
1. Install commission_ax first
2. Install commission_statement second
3. Update sale orders to include commission partner assignments

### Test Data Setup:
1. Create a sale order
2. Assign partners to commission fields (consultant_id, manager_id, etc.)  
3. Confirm the sale order
4. Run the commission statement report

The enhanced error messages will now show exactly what's missing!
