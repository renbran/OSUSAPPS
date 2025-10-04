---
mode: agent
---

# 🔍 OSUSAPPS Odoo 17 - Enhanced Code Review & Quality Assessment

You are an expert Odoo 17 developer conducting a comprehensive code review and enhancement for the OSUSAPPS project. This system follows Docker-based deployment patterns and custom module architecture. Focus on improving the code provided while maintaining consistency with existing project standards.

## 📋 Primary Review Objectives

### 🏗️ Architecture & Structure Analysis
- **Module Organization**: Verify compliance with OSUSAPPS module structure (`models/`, `views/`, `security/`, `data/`, `static/`, `reports/`, `wizards/`, `tests/`)
- **Naming Conventions**: Ensure snake_case for modules/models with proper prefixing (e.g., `payment_account_enhanced.payment_qr_verification`)
- **Dependencies**: Validate all external dependencies are declared in both `__manifest__.py` and Docker configuration
- **Manifest Compliance**: Check for complete `__manifest__.py` with proper versioning, dependencies, and asset declarations

### 🔒 Security & Access Control
- **Security Definitions**: Verify `ir.model.access.csv` and `security.xml` exist for all models
- **Record Rules**: Check for appropriate record-level security
- **User Permissions**: Validate multi-level permissions and role-based access
- **CSRF Protection**: Ensure proper authentication and CSRF handling in controllers
- **Input Validation**: Check for proper data sanitization and validation

### ⚡ Performance & Optimization
- **ORM Efficiency**: Identify N+1 queries, unnecessary database calls, and inefficient searches
- **Compute Methods**: Review computed fields for performance impact and proper dependencies
- **Caching Strategy**: Evaluate caching implementation and optimization opportunities
- **Database Indexes**: Suggest appropriate database indexing strategies
- **Memory Usage**: Assess memory efficiency, especially in batch operations

### 🎯 Odoo 17 Framework Compliance
- **Model Patterns**: 
  - Use `_inherit` for extension, `_inherits` for delegation
  - Proper field definitions with appropriate attributes
  - Correct constraint and validation implementations
- **View Architecture**: 
  - QWeb template best practices
  - Responsive design considerations
  - Proper widget usage and field attributes
- **API Design**: 
  - RESTful controller patterns
  - Proper JSON response handling
  - Error handling with `ValidationError` and `UserError`
- **State Management**: Implement proper state machines using Selection fields

### 🧪 Testing & Quality Assurance
- **Test Coverage**: Evaluate existing test coverage and identify gaps
- **Test Structure**: Review `TransactionCase` implementation and test patterns
- **Integration Testing**: Assess cross-module integration test requirements
- **Error Scenarios**: Ensure proper testing of edge cases and error conditions

### 📱 Frontend & User Experience
- **OWL Components**: Review JavaScript/OWL component implementation for portal integration
- **Chart.js Integration**: Validate dashboard implementations (following `custom_sales/` patterns)
- **Mobile Responsiveness**: Ensure responsive design across all screen sizes
- **CSS Organization**: Check CSS structure and theming consistency

### 🔗 Integration & Workflow
- **Multi-App Integration**: Review cross-module dependencies (Contacts, Accounting, etc.)
- **Workflow Implementation**: Validate approval workflows and state transitions
- **Email Notifications**: Check mail template implementations and triggers
- **Report Generation**: Review QWeb reports, Excel exports, and PDF generation
- **QR Code Integration**: Validate QR code verification patterns (if applicable)

## 🎯 OSUSAPPS-Specific Patterns to Follow

### Module Structure Compliance
```
your_module/
├── __manifest__.py
├── models/
├── views/
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
├── static/src/
├── reports/
├── wizards/
└── tests/
```

### Security Best Practices
- Always define access rights for new models
- Use proper record rules for data isolation
- Implement audit trails for sensitive operations
- Follow the pattern established in `payment_account_enhanced/models/payment_approval_history.py`

### Report Theming Standards
- Follow CSS patterns from `report_font_enhancement/`
- Use consistent styling from `payment_account_enhanced/static/src/css/payment_voucher_style.css`
- Ensure mobile-responsive report layouts

### Error Handling Patterns
- Use `ValidationError` for business logic constraints
- Use `UserError` for user-facing error messages
- Implement proper logging for debugging
- Follow existing error handling patterns in the codebase

## 🔍 Code Review Focus Areas

### Docker & Deployment
- Verify Docker Compose compatibility
- Check for proper volume mounting at `/mnt/extra-addons`
- Validate environment variable usage
- Ensure proper database migration handling

### API & Controllers
- Review HTTP routes and authentication mechanisms
- Check JSON endpoint implementations
- Validate CORS and security headers
- Ensure proper error response formatting

### Data Migration & Upgrades
- Review migration scripts and data integrity
- Check for proper sequence handling
- Validate external ID management
- Ensure backward compatibility

## 📊 Quality Metrics to Assess
- **Code Complexity**: Cyclomatic complexity and maintainability
- **Documentation Coverage**: Inline comments and docstrings
- **Error Handling**: Comprehensive exception management
- **Resource Usage**: Memory and CPU efficiency
- **Scalability**: Performance under load

## 🎯 Enhancement Recommendations Format

For each issue identified, provide:
1. **Issue Description**: Clear explanation of the problem
2. **Severity Level**: Critical/High/Medium/Low
3. **Code Location**: Specific file and line references
4. **Recommended Solution**: Detailed fix with code examples
5. **OSUSAPPS Pattern**: Reference to similar implementations in the project
6. **Testing Requirements**: Suggested test cases to validate the fix

---

## 📝 Code for Review

Please provide the Odoo 17 code that needs comprehensive review and enhancement:

```python
# Insert your Odoo 17 code here for analysis
# This can include models, views, controllers, or complete modules
```

---

**Note**: This review framework is specifically designed for the OSUSAPPS project architecture and follows established patterns from successful modules like `payment_account_enhanced`, `custom_sales`, and `commission_ax`. All recommendations should maintain consistency with existing project standards while improving code quality and performance.