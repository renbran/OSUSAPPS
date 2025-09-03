{
  // ====== EARS REQUIREMENTS SNIPPETS ======
  "EARS Requirement Template": {
    "prefix": "ears-req",
    "body": [
      "### Requirement ${1:number}",
      "",
      "**User Story:** As a ${2:role}, I want ${3:feature}, so that ${4:benefit}",
      "",
      "#### Acceptance Criteria",
      "",
      "1. WHEN ${5:event} THEN ${6:system} SHALL ${7:response}",
      "2. IF ${8:precondition} THEN ${9:system} SHALL ${10:response}",
      "$0"
    ],
    "description": "Create EARS format requirement with user story"
  },
  
  "EARS WHEN Requirement": {
    "prefix": "ears-when",
    "body": [
      "WHEN ${1:event} THEN ${2:system} SHALL ${3:response}"
    ],
    "description": "EARS WHEN requirement format"
  },
  
  "EARS IF Requirement": {
    "prefix": "ears-if", 
    "body": [
      "IF ${1:precondition} THEN ${2:system} SHALL ${3:response}"
    ],
    "description": "EARS IF requirement format"
  },
  
  "EARS WHERE Requirement": {
    "prefix": "ears-where",
    "body": [
      "WHERE ${1:location} WHEN ${2:event} THEN ${3:system} SHALL ${4:response}"
    ],
    "description": "EARS WHERE requirement format"
  },
  
  "EARS WHILE Requirement": {
    "prefix": "ears-while",
    "body": [
      "WHILE ${1:state} THEN ${2:system} SHALL ${3:response}"
    ],
    "description": "EARS WHILE requirement format"
  },
  
  "User Story Template": {
    "prefix": "user-story",
    "body": [
      "**User Story:** As a ${1:role}, I want ${2:feature}, so that ${3:benefit}"
    ],
    "description": "Standard user story format"
  },
  
  // ====== DESIGN DOCUMENT SNIPPETS ======
  "Design Document Template": {
    "prefix": "design-doc",
    "body": [
      "# Design Document",
      "",
      "## Overview",
      "${1:Design goal and scope}",
      "",
      "## Architecture Design",
      "",
      "### System Architecture Diagram",
      "```mermaid",
      "graph TB",
      "    A[${2:Component A}] --> B[${3:Component B}]",
      "    B --> C[${4:Component C}]",
      "```",
      "",
      "### Data Flow Diagram", 
      "```mermaid",
      "graph LR",
      "    A[${5:Input}] --> B[${6:Process}]",
      "    B --> C[${7:Output}]",
      "```",
      "",
      "## Component Design",
      "",
      "### ${8:Component Name}",
      "- **Responsibilities:** ${9:What this component does}",
      "- **Interfaces:** ${10:Public methods and APIs}",
      "- **Dependencies:** ${11:What this component depends on}",
      "",
      "## Data Model",
      "```typescript",
      "interface ${12:ModelName} {",
      "  ${13:property}: ${14:type};",
      "}",
      "```",
      "",
      "## Business Process",
      "",
      "### ${15:Process Name}",
      "```mermaid",
      "flowchart TD",
      "    A[${16:Start}] --> B[${17:Step 1}]",
      "    B --> C[${18:Step 2}]",
      "    C --> D[${19:End}]",
      "```",
      "",
      "## Error Handling Strategy",
      "${20:Error handling approach}",
      "",
      "## Testing Strategy",
      "${21:Testing approach}",
      "$0"
    ],
    "description": "Complete design document template"
  },
  
  "Mermaid Architecture Diagram": {
    "prefix": "mermaid-arch",
    "body": [
      "```mermaid",
      "graph TB",
      "    A[${1:Frontend}] --> B[${2:API Gateway}]",
      "    B --> C[${3:Business Service}]", 
      "    C --> D[${4:Database}]",
      "    C --> E[${5:Cache Service}]",
      "```"
    ],
    "description": "Mermaid architecture diagram template"
  },
  
  "Mermaid Data Flow": {
    "prefix": "mermaid-flow",
    "body": [
      "```mermaid",
      "graph LR",
      "    A[${1:Input Data}] --> B[${2:Processor}]",
      "    B --> C{${3:Decision}}",
      "    C -->|${4:Yes}| D[${5:Success Path}]",
      "    C -->|${6:No}| E[${7:Error Path}]",
      "```"
    ],
    "description": "Mermaid data flow diagram template"
  },
  
  "Mermaid Business Process": {
    "prefix": "mermaid-process",
    "body": [
      "```mermaid",
      "flowchart TD",
      "    A[${1:Start}] --> B[${2:componentName.methodName}]",
      "    B --> C{${3:Condition}}",
      "    C -->|${4:True}| D[${5:Success Action}]",
      "    C -->|${6:False}| E[${7:Error Action}]",
      "    D --> F[${8:End}]",
      "    E --> F",
      "```"
    ],
    "description": "Mermaid business process flowchart template"
  },
  
  "TypeScript Interface": {
    "prefix": "ts-interface",
    "body": [
      "interface ${1:InterfaceName} {",
      "  ${2:property}: ${3:type};",
      "  ${4:method}(${5:params}): ${6:returnType};",
      "}"
    ],
    "description": "TypeScript interface for data models"
  },
  
  // ====== ODOO 17 SPEC-COMPLIANT SNIPPETS ======
  "Odoo Model with Spec": {
    "prefix": "odoo-model-spec",
    "body": [
      "# -*- coding: utf-8 -*-",
      "\"\"\"",
      "${1:Model Description}",
      "",
      "This model implements requirements from:",
      "- Requirement ${2:REQ-001}: ${3:requirement description}",
      "- Requirement ${4:REQ-002}: ${5:requirement description}", 
      "\"\"\"",
      "",
      "from odoo import models, fields, api",
      "from odoo.exceptions import ValidationError",
      "",
      "",
      "class ${6:ModelName}(models.Model):",
      "    \"\"\"${7:Model docstring describing purpose and functionality}\"\"\"",
      "    _name = '${8:module.model.name}'",
      "    _description = '${9:Model Description}'",
      "    _order = '${10:name}'",
      "",
      "    # Core Fields - Implements REQ-${11:001}",
      "    name = fields.Char(",
      "        string='${12:Name}',",
      "        required=True,",
      "        help='${13:Field description}'",
      "    )",
      "",
      "    # Computed Fields - Implements REQ-${14:002}",
      "    @api.depends('${15:dependency_field}')",
      "    def _compute_${16:computed_field}(self):",
      "        \"\"\"Compute ${17:field description} based on ${18:dependency description}\"\"\"",
      "        for record in self:",
      "            record.${19:computed_field} = ${20:computation_logic}",
      "",
      "    ${21:computed_field} = fields.${22:FieldType}(",
      "        string='${23:Field Label}',",
      "        compute='_compute_${24:computed_field}',",
      "        store=True,",
      "        help='${25:Field help text}'",
      "    )",
      "",
      "    # Constraints - Implements data integrity requirements",
      "    @api.constrains('${26:field_name}')",
      "    def _check_${27:constraint_name}(self):",
      "        \"\"\"Validate ${28:constraint description}\"\"\"",
      "        for record in self:",
      "            if ${29:validation_condition}:",
      "                raise ValidationError('${30:Error message}')",
      "",
      "    # SQL Constraints",
      "    _sql_constraints = [",
      "        ('${31:constraint_name}', '${32:constraint_sql}', '${33:Error message}'),",
      "    ]",
      "$0"
    ],
    "description": "Odoo model template with spec traceability"
  },
  
  "Odoo View with Spec": {
    "prefix": "odoo-view-spec",
    "body": [
      "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
      "<!--",
      "View for ${1:Model Name}",
      "",
      "Implements UI requirements:",
      "- REQ-${2:001}: ${3:UI requirement description}",
      "- REQ-${4:002}: ${5:UI requirement description}",
      "-->",
      "<odoo>",
      "    <data>",
      "",
      "        <!-- ${6:View Type} View - Implements REQ-${7:001} -->",
      "        <record id=\"view_${8:model_name}_${9:view_type}\" model=\"ir.ui.view\">",
      "            <field name=\"name\">${10:model.name}.${11:view.type}</field>",
      "            <field name=\"model\">${12:model.technical.name}</field>",
      "            <field name=\"arch\" type=\"xml\">",
      "                <${13:view_type}>",
      "                    <field name=\"${14:field_name}\"/>",
      "                    <!-- Add more fields as per design specifications -->",
      "                </${15:view_type}>",
      "            </field>",
      "        </record>",
      "",
      "        <!-- Action - Implements REQ-${16:002} -->",
      "        <record id=\"action_${17:model_name}\" model=\"ir.actions.act_window\">",
      "            <field name=\"name\">${18:Action Name}</field>",
      "            <field name=\"res_model\">${19:model.technical.name}</field>",
      "            <field name=\"view_mode\">${20:tree,form}</field>",
      "            <field name=\"help\" type=\"html\">",
      "                <p class=\"o_view_nocontent_smiling_face\">",
      "                    ${21:Help text as per UX requirements}",
      "                </p>",
      "            </field>",
      "        </record>",
      "",
      "    </data>",
      "</odoo>",
      "$0"
    ],
    "description": "Odoo view template with requirement traceability"
  },
  
  "Odoo Security with Spec": {
    "prefix": "odoo-security-spec",
    "body": [
      "# Security configuration implementing:",
      "# REQ-${1:001}: ${2:Security requirement description}",
      "# REQ-${3:002}: ${4:Access control requirement}",
      "",
      "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink",
      "access_${5:model_name}_user,${6:model.name} User,model_${7:model_name},${8:group_name},1,0,0,0",
      "access_${9:model_name}_manager,${10:model.name} Manager,model_${11:model_name},${12:manager_group},1,1,1,1",
      "$0"
    ],
    "description": "Odoo security access rights with requirement traceability"
  },
  
  "Odoo Test with Spec": {
    "prefix": "odoo-test-spec",
    "body": [
      "# -*- coding: utf-8 -*-",
      "\"\"\"",
      "Test cases for ${1:Model Name}",
      "",
      "Tests validate the following requirements:",
      "- REQ-${2:001}: ${3:requirement description}",
      "- REQ-${4:002}: ${5:requirement description}",
      "\"\"\"",
      "",
      "from odoo.tests.common import TransactionCase",
      "from odoo.exceptions import ValidationError",
      "",
      "",
      "class Test${6:ModelName}(TransactionCase):",
      "    \"\"\"Test cases for ${7:model_name} model\"\"\"",
      "",
      "    def setUp(self):",
      "        super().setUp()",
      "        self.${8:model_var} = self.env['${9:model.technical.name}']",
      "",
      "    def test_${10:requirement_id}_${11:test_description}(self):",
      "        \"\"\"",
      "        Test REQ-${12:001}: ${13:Requirement description}",
      "        ",
      "        WHEN ${14:event condition}",
      "        THEN ${15:expected system behavior} SHALL occur",
      "        \"\"\"",
      "        # Arrange",
      "        ${16:test_setup}",
      "        ",
      "        # Act",
      "        ${17:action_to_test}",
      "        ",
      "        # Assert",
      "        ${18:assertion_validating_requirement}",
      "",
      "    def test_${19:requirement_id}_${20:validation_test}(self):",
      "        \"\"\"",
      "        Test REQ-${21:002}: ${22:Validation requirement}",
      "        ",
      "        IF ${23:invalid_condition}",
      "        THEN system SHALL ${24:expected_validation_behavior}",
      "        \"\"\"",
      "        with self.assertRaises(ValidationError):",
      "            ${25:invalid_action}",
      "$0"
    ],
    "description": "Odoo test template with EARS requirement validation"
  },
  
  // ====== MANIFEST AND MODULE STRUCTURE ======
  "Odoo Manifest with Spec": {
    "prefix": "odoo-manifest-spec",
    "body": [
      "# -*- coding: utf-8 -*-",
      "{",
      "    'name': '${1:Module Name}',",
      "    'version': '17.0.1.0.0',",
      "    'category': '${2:Category}',",
      "    'summary': '${3:Module summary implementing spec requirements}',",
      "    'description': '''",
      "${4:Detailed module description}",
      "",
      "Implements requirements:",
      "- REQ-${5:001}: ${6:requirement description}",
      "- REQ-${7:002}: ${8:requirement description}",
      "",
      "Design documents: .claude/specs/${9:feature-name}/",
      "    ''',",
      "    'author': '${10:Your Name}',",
      "    'website': '${11:https://your-website.com}',",
      "    'license': 'LGPL-3',",
      "    'depends': [",
      "        'base',",
      "        '${12:dependency}',",
      "    ],",
      "    'data': [",
      "        'security/ir.model.access.csv',",
      "        'views/${13:model_name}_views.xml',",
      "        'data/${14:data_file}.xml',",
      "    ],",
      "    'demo': [",
      "        'demo/${15:demo_file}.xml',",
      "    ],",
      "    'installable': True,",
      "    'application': ${16:False},",
      "    'auto_install': False,",
      "}",
      "$0"
    ],
    "description": "Odoo manifest template with spec documentation"
  },
  
  // ====== WORKFLOW VALIDATION SNIPPETS ======
  "Requirement Validation Comment": {
    "prefix": "req-validate",
    "body": [
      "# REQ-${1:001} Validation:",
      "# WHEN ${2:condition} THEN system SHALL ${3:behavior}",
      "# Implementation: ${4:how this code satisfies the requirement}",
      "$0"
    ],
    "description": "Comment template for requirement validation"
  },
  
  "Design Traceability Comment": {
    "prefix": "design-trace",
    "body": [
      "\"\"\"",
      "Component: ${1:ComponentName}",
      "Design Reference: .claude/specs/${2:feature-name}/design.md#${3:section}",
      "Implements: ${4:specific design element}",
      "\"\"\"",
      "$0"
    ],
    "description": "Docstring template for design traceability"
  },
  
  "Spec File Header": {
    "prefix": "spec-header",
    "body": [
      "\"\"\"",
      "${1:Module/File Name}",
      "",
      "Feature: ${2:feature-name}",
      "Spec Location: .claude/specs/${3:feature-name}/",
      "Requirements: requirements.md",
      "Design: design.md",
      "",
      "Implements:",
      "- REQ-${4:001}: ${5:requirement summary}",
      "- REQ-${6:002}: ${7:requirement summary}",
      "",
      "Author: ${8:Your Name}",
      "Date: ${9:YYYY-MM-DD}",
      "\"\"\"",
      "$0"
    ],
    "description": "Standard file header with spec references"
  }
}