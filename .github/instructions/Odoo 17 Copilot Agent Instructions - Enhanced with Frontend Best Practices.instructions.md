# Odoo 17 Development Context

## Project Structure
- This is an Odoo 17 ERP development project
- Follow Odoo 17 MVC architecture patterns
- Use PostgreSQL as primary database
- Python 3.8+ required

## Coding Standards
- Follow PEP 8 for Python code
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use type hints where possible

## Odoo-Specific Guidelines
- Always use proper model inheritance
- Implement security groups and access rights
- Use @api.depends for computed fields
- Follow proper field naming conventions
- Implement proper ondelete cascading

## File Naming Conventions
- Models: snake_case (e.g., sale_order.py)
- Views: descriptive names (e.g., sale_order_view.xml)
- Data files: purpose-based (e.g., security.xml, data.xml)