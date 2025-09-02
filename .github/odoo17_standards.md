# Odoo 17 Development Standards

## Module Structure
- models/ - Model definitions
- views/ - XML views and templates  
- controllers/ - HTTP routes
- data/ - Demo and data XML
- security/ - Access rights and rules
- static/ - Web assets (js, css, img)
- wizard/ - Transient models
- report/ - Reports and SQL views
- tests/ - Python tests

## Naming Conventions
- Models: Use singular form (res.partner, sale.order)
- Fields: Many2one suffix with _id, One2many/Many2many with _ids
- XML IDs: model_name_view_form, model_name_action
- Methods: _compute_field_name, _onchange_field_name

## Code Organization in Models
1. Private attributes (_name, _description, _inherit)
2. Default methods
3. Field declarations
4. Compute/inverse/search methods
5. Selection methods
6. Constraints (@api.constrains) and onchange (@api.onchange)
7. CRUD method overrides
8. Action methods
9. Business methods
