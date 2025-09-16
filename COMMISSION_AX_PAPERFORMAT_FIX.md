# Commission Module Fix: Paperformat Reference# Commission Module Fix: Paperformat Reference



## Issue Summary## Issue Summary



The commission_ax module was failing to initialize on staging-erposus.com due to a missing external ID reference:The commission_ax module was failing to initialize on staging-erposus.com due to a missing external ID reference:



```plain```plain

ValueError: External ID not found in the system: base.paperformat_a4ValueError: External ID not found in the system: base.paperformat_a4

``````



This error occurred in the `deals_commission_report.xml` file where the report action was referencing a paper format that wasn't available in the database.This error occurred in the `deals_commission_report.xml` file where the report action was referencing a paper format that wasn't available in the database.



## Fix Applied## Fix Applied

1. **Created a new paperformat data file**: 

1. **Created a new paperformat data file**:   - Added `data/paperformat_data.xml` to define the A4 paper format within the module

   - This ensures the paper format exists before it's referenced

   - Added `data/paperformat_data.xml` to define the A4 paper format within the module

   - This ensures the paper format exists before it's referenced2. **Updated the report action reference**:

   - Changed the paperformat reference from `base.paperformat_a4` to `commission_ax.paperformat_a4`

2. **Updated the report action reference**:   - This points to our newly defined paper format



   - Changed the paperformat reference from `base.paperformat_a4` to `commission_ax.paperformat_a4`3. **Updated the module manifest**:

   - This points to our newly defined paper format   - Added the new data file to the manifest's data list

   - Ensures the paper format is loaded when the module is installed/updated

3. **Updated the module manifest**:

## Files Changed

   - Added the new data file to the manifest's data list1. `commission_ax/data/paperformat_data.xml` (new file)

   - Ensures the paper format is loaded when the module is installed/updated2. `commission_ax/reports/deals_commission_report.xml`

3. `commission_ax/__manifest__.py`

## Files Changed

## Deployment Instructions

1. `commission_ax/data/paperformat_data.xml` (new file)

2. `commission_ax/reports/deals_commission_report.xml`### On Development Environment

3. `commission_ax/__manifest__.py`1. Restart Odoo and update the module:

   ```bash

## Deployment Instructions   docker-compose restart odoo

   docker-compose exec odoo odoo --update=commission_ax --stop-after-init -d your_database

### On Development Environment   ```



1. Restart Odoo and update the module:### On Production/Staging

1. Apply the same changes to the production codebase:

   ```bash   - Add the new paperformat_data.xml file

   docker-compose restart odoo   - Update the deals_commission_report.xml reference

   docker-compose exec odoo odoo --update=commission_ax --stop-after-init -d your_database   - Update the manifest

   ```   

2. Update the module on the server:

### On Production/Staging   ```bash

   cd /path/to/odoo

1. Apply the same changes to the production codebase:   ./odoo-bin --update=commission_ax --stop-after-init -d your_database

   ```

   - Add the new paperformat_data.xml file   

   - Update the deals_commission_report.xml reference3. Restart the Odoo service:

   - Update the manifest   ```bash

      service odoo restart

2. Update the module on the server:   # OR

   systemctl restart odoo

   ```bash   ```

   cd /path/to/odoo

   ./odoo-bin --update=commission_ax --stop-after-init -d your_database## Verification

   ```After applying the changes, verify that:

   1. The module updates without errors

3. Restart the Odoo service:2. The commission reports can be generated successfully

3. The PDF output uses the correct A4 paper format

   ```bash

   service odoo restart## Notes

   # ORThis issue occurred because Odoo 17 might have changed how some base paper formats are defined or referenced. By explicitly defining the paperformat in our module, we ensure it's always available regardless of the base module's configuration.
   systemctl restart odoo
   ```

## Verification

After applying the changes, verify that:

1. The module updates without errors
2. The commission reports can be generated successfully
3. The PDF output uses the correct A4 paper format

## Notes

This issue occurred because Odoo 17 might have changed how some base paper formats are defined or referenced. By explicitly defining the paperformat in our module, we ensure it's always available regardless of the base module's configuration.
