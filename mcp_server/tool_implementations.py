"""
Odoo 17 MCP Server - Tool Implementations

This module contains the actual implementation of all MCP tools for Odoo 17 development.
Each tool is implemented as an async method that returns a CallToolResult.
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from mcp.types import CallToolResult, TextContent, JSONRPCError, INTERNAL_ERROR


class Odoo17ToolImplementations:
    """Implementation class for all Odoo 17 MCP tools."""
    
    def __init__(self):
        self.logger = None  # Will be set by parent class
    
    async def _scaffold_odoo_module(self, module_name: str, module_title: str, 
                                   description: str = "", author: str = "OSUSAPPS",
                                   website: str = "https://osusapps.com", 
                                   depends: List[str] = None, 
                                   include_models: bool = True,
                                   include_views: bool = True,
                                   include_security: bool = True,
                                   include_reports: bool = False,
                                   include_controllers: bool = False,
                                   output_path: str = ".") -> CallToolResult:
        """Create a new Odoo 17 module with proper structure."""
        
        try:
            if depends is None:
                depends = ["base"]
                
            module_path = Path(output_path) / module_name
            
            # Check if module already exists
            if module_path.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Module '{module_name}' already exists at {module_path}")]
                )
            
            # Create module directory structure
            module_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            dirs_to_create = ["models", "views", "data", "static/src/js", "static/src/css", "static/src/xml"]
            
            if include_security:
                dirs_to_create.append("security")
            if include_reports:
                dirs_to_create.extend(["reports", "report_templates"])
            if include_controllers:
                dirs_to_create.append("controllers")
                
            for dir_name in dirs_to_create:
                (module_path / dir_name).mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files
            init_files = ["__init__.py", "models/__init__.py"]
            if include_controllers:
                init_files.append("controllers/__init__.py")
                
            for init_file in init_files:
                (module_path / init_file).write_text("# -*- coding: utf-8 -*-\n")
            
            # Create __manifest__.py
            manifest_content = self._generate_manifest(
                module_name, module_title, description, author, website, depends,
                include_models, include_views, include_security, include_reports, include_controllers
            )
            (module_path / "__manifest__.py").write_text(manifest_content)
            
            # Create models/__init__.py with imports
            if include_models:
                models_init = "# -*- coding: utf-8 -*-\nfrom . import models\n"
                (module_path / "models/__init__.py").write_text(models_init)
                
                # Create sample model
                model_content = self._generate_sample_model(module_name)
                (module_path / "models/models.py").write_text(model_content)
            
            # Create views
            if include_views:
                views_content = self._generate_sample_views(module_name)
                (module_path / "views/views.xml").write_text(views_content)
                
                menu_content = self._generate_menu_views(module_name, module_title)
                (module_path / "views/menu.xml").write_text(menu_content)
            
            # Create security files
            if include_security:
                security_content = self._generate_security_csv(module_name)
                (module_path / "security/ir.model.access.csv").write_text(security_content)
                
                groups_content = self._generate_security_groups(module_name)
                (module_path / "security/security.xml").write_text(groups_content)
            
            # Create controllers
            if include_controllers:
                controller_content = self._generate_sample_controller(module_name)
                (module_path / "controllers/main.py").write_text(controller_content)
            
            # Create static assets
            js_content = self._generate_sample_js(module_name)
            (module_path / "static/src/js/custom.js").write_text(js_content)
            
            css_content = self._generate_sample_css(module_name)
            (module_path / "static/src/css/style.css").write_text(css_content)
            
            # Create README
            readme_content = self._generate_readme(module_name, module_title, description, author)
            (module_path / "README.md").write_text(readme_content)
            
            result_text = f"""✅ Successfully created Odoo 17 module: {module_name}

📁 Module structure:
{module_path}/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── models.py
├── views/
│   ├── views.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── static/
│   └── src/
│       ├── js/custom.js
│       ├── css/style.css
│       └── xml/
└── data/

🚀 Next steps:
1. Install the module: docker-compose exec odoo odoo -i {module_name} --stop-after-init
2. Update app list in Odoo UI
3. Customize the models and views as needed

📋 Module details:
- Name: {module_name}
- Title: {module_title}
- Author: {author}
- Dependencies: {', '.join(depends)}
"""
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error creating module: {str(e)}")]
            )
    
    def _generate_manifest(self, module_name: str, module_title: str, description: str,
                          author: str, website: str, depends: List[str],
                          include_models: bool, include_views: bool, include_security: bool,
                          include_reports: bool, include_controllers: bool) -> str:
        """Generate __manifest__.py content."""
        
        data_files = []
        if include_security:
            data_files.extend([
                'security/ir.model.access.csv',
                'security/security.xml'
            ])
        if include_views:
            data_files.extend([
                'views/views.xml',
                'views/menu.xml'
            ])
        
        data_str = "[\n        " + ",\n        ".join([f"'{f}'" for f in data_files]) + "\n    ]" if data_files else "[]"
        
        return f"""# -*- coding: utf-8 -*-
{{
    'name': '{module_title}',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': '{description or module_title}',
    'description': '''
        {description or module_title}
        
        Features:
        - Modern Odoo 17 architecture
        - Proper security implementation
        - Responsive UI design
        - Comprehensive documentation
    ''',
    'author': '{author}',
    'website': '{website}',
    'license': 'LGPL-3',
    'depends': {depends},
    'data': {data_str},
    'assets': {{
        'web.assets_backend': [
            '{module_name}/static/src/js/custom.js',
            '{module_name}/static/src/css/style.css',
        ],
    }},
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
}}
"""

    def _generate_sample_model(self, module_name: str) -> str:
        """Generate sample model content."""
        
        model_class = ''.join(word.capitalize() for word in module_name.split('_'))
        
        return f"""# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class {model_class}(models.Model):
    _name = '{module_name}.record'
    _description = '{model_class} Record'
    _order = 'create_date desc'
    _rec_name = 'name'
    
    # Basic Fields
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help='Record name'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the record'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to hide the record'
    )
    
    # Status Field with Selection
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Date Fields
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True
    )
    
    deadline = fields.Datetime(
        string='Deadline',
        help='Deadline for completion'
    )
    
    # Numeric Fields
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='0')
    
    progress = fields.Float(
        string='Progress (%)',
        digits=(3, 2),
        help='Completion progress percentage'
    )
    
    # Relational Fields
    user_id = fields.Many2one(
        'res.users',
        string='Assigned User',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed Fields
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True
    )
    
    display_name_full = fields.Char(
        string='Full Display Name',
        compute='_compute_display_name_full'
    )
    
    @api.depends('deadline')
    def _compute_is_overdue(self):
        \"\"\"Check if record is overdue.\"\"\"
        today = fields.Datetime.now()
        for record in self:
            record.is_overdue = record.deadline and record.deadline < today
    
    @api.depends('name', 'state')
    def _compute_display_name_full(self):
        \"\"\"Compute full display name.\"\"\"
        for record in self:
            record.display_name_full = f"[{{record.state.upper()}}] {{record.name}}"
    
    # Constraints
    @api.constrains('progress')
    def _check_progress(self):
        \"\"\"Validate progress percentage.\"\"\"
        for record in self:
            if not (0 <= record.progress <= 100):
                raise ValidationError(_('Progress must be between 0 and 100.'))
    
    @api.constrains('deadline', 'date')
    def _check_deadline(self):
        \"\"\"Validate deadline is after date.\"\"\"
        for record in self:
            if record.deadline and record.date and record.deadline.date() < record.date:
                raise ValidationError(_('Deadline cannot be before the record date.'))
    
    # Actions
    def action_confirm(self):
        \"\"\"Confirm the record.\"\"\"
        self.write({{'state': 'confirmed'}})
        return True
    
    def action_done(self):
        \"\"\"Mark record as done.\"\"\"
        self.write({{'state': 'done', 'progress': 100.0}})
        return True
    
    def action_cancel(self):
        \"\"\"Cancel the record.\"\"\"
        self.write({{'state': 'cancelled'}})
        return True
    
    def action_reset_to_draft(self):
        \"\"\"Reset to draft state.\"\"\"
        self.write({{'state': 'draft'}})
        return True
    
    # Onchange Methods
    @api.onchange('state')
    def _onchange_state(self):
        \"\"\"Update progress based on state.\"\"\"
        if self.state == 'done':
            self.progress = 100.0
        elif self.state == 'cancelled':
            self.progress = 0.0
    
    # Override Methods
    def name_get(self):
        \"\"\"Custom name_get method.\"\"\"
        result = []
        for record in self:
            name = f"[{{record.state.upper()}}] {{record.name}}"
            result.append((record.id, name))
        return result
    
    @api.model
    def create(self, vals):
        \"\"\"Override create method.\"\"\"
        # Add custom logic here if needed
        return super({model_class}, self).create(vals)
    
    def write(self, vals):
        \"\"\"Override write method.\"\"\"
        # Add custom logic here if needed
        return super({model_class}, self).write(vals)
"""

    def _generate_sample_views(self, module_name: str) -> str:
        """Generate sample views content."""
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_{module_name}_tree" model="ir.ui.view">
        <field name="name">{module_name}.record.tree</field>
        <field name="model">{module_name}.record</field>
        <field name="arch" type="xml">
            <tree string="Records" decoration-danger="is_overdue" decoration-success="state=='done'">
                <field name="name"/>
                <field name="user_id"/>
                <field name="date"/>
                <field name="deadline"/>
                <field name="state" decoration-bf="1" widget="badge" 
                       decoration-success="state=='done'" 
                       decoration-info="state=='confirmed'"
                       decoration-warning="state=='draft'"
                       decoration-danger="state=='cancelled'"/>
                <field name="progress" widget="progressbar"/>
                <field name="priority" widget="priority"/>
                <field name="is_overdue" invisible="1"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_{module_name}_form" model="ir.ui.view">
        <field name="name">{module_name}.record.form</field>
        <field name="model">{module_name}.record</field>
        <field name="arch" type="xml">
            <form string="Record">
                <header>
                    <button name="action_confirm" string="Confirm" type="object" 
                            states="draft" class="btn-primary"/>
                    <button name="action_done" string="Mark Done" type="object" 
                            states="confirmed" class="btn-success"/>
                    <button name="action_cancel" string="Cancel" type="object" 
                            states="draft,confirmed" class="btn-secondary"/>
                    <button name="action_reset_to_draft" string="Reset to Draft" type="object" 
                            states="cancelled,done" class="btn-warning"/>
                    <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button class="oe_stat_button" type="action" icon="fa-tasks">
                            <field string="Progress" name="progress" widget="statinfo"/>
                        </button>
                    </div>
                    
                    <widget name="web_ribbon" title="Overdue" bg_color="bg-danger" 
                            attrs="{{'invisible': [('is_overdue', '=', False)]}}"/>
                    
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Record Name..."/>
                        </h1>
                    </div>
                    
                    <group>
                        <group name="basic_info">
                            <field name="user_id"/>
                            <field name="date"/>
                            <field name="deadline"/>
                            <field name="priority" widget="priority"/>
                        </group>
                        <group name="progress_info">
                            <field name="progress" widget="percentpie"/>
                            <field name="active"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="is_overdue" invisible="1"/>
                        </group>
                    </group>
                    
                    <notebook>
                        <page string="Description" name="description">
                            <field name="description" placeholder="Add a description..."/>
                        </page>
                        <page string="Technical Info" name="technical" groups="base.group_no_one">
                            <group>
                                <field name="create_date"/>
                                <field name="create_uid"/>
                                <field name="write_date"/>
                                <field name="write_uid"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_{module_name}_search" model="ir.ui.view">
        <field name="name">{module_name}.record.search</field>
        <field name="model">{module_name}.record</field>
        <field name="arch" type="xml">
            <search string="Search Records">
                <field name="name" string="Name" filter_domain="[('name','ilike',self)]"/>
                <field name="user_id"/>
                <field name="date"/>
                <field name="state"/>
                
                <filter string="My Records" name="my_records" 
                        domain="[('user_id','=',uid)]"/>
                <filter string="Active" name="active" 
                        domain="[('active','=',True)]"/>
                <filter string="Overdue" name="overdue" 
                        domain="[('is_overdue','=',True)]"/>
                
                <separator/>
                <filter string="Draft" name="draft" 
                        domain="[('state','=','draft')]"/>
                <filter string="Confirmed" name="confirmed" 
                        domain="[('state','=','confirmed')]"/>
                <filter string="Done" name="done" 
                        domain="[('state','=','done')]"/>
                
                <separator/>
                <filter string="This Month" name="this_month" 
                        domain="[('date','&gt;=',datetime.datetime.now().replace(day=1))]"/>
                
                <group expand="0" string="Group By">
                    <filter string="Assigned User" name="group_user" 
                            context="{{'group_by':'user_id'}}"/>
                    <filter string="Status" name="group_state" 
                            context="{{'group_by':'state'}}"/>
                    <filter string="Date" name="group_date" 
                            context="{{'group_by':'date'}}"/>
                    <filter string="Priority" name="group_priority" 
                            context="{{'group_by':'priority'}}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Kanban View -->
    <record id="view_{module_name}_kanban" model="ir.ui.view">
        <field name="name">{module_name}.record.kanban</field>
        <field name="model">{module_name}.record</field>
        <field name="arch" type="xml">
            <kanban default_group_by="state" class="o_kanban_small_column">
                <field name="name"/>
                <field name="user_id"/>
                <field name="date"/>
                <field name="deadline"/>
                <field name="state"/>
                <field name="priority"/>
                <field name="progress"/>
                <field name="is_overdue"/>
                <templates>
                    <t t-name="kanban-box">
                        <div t-attf-class="oe_kanban_card oe_kanban_global_click {{record.is_overdue.raw_value ? 'oe_kanban_card_danger' : ''}}">
                            <div class="oe_kanban_content">
                                <div class="o_kanban_record_top">
                                    <div class="o_kanban_record_headings">
                                        <strong class="o_kanban_record_title">
                                            <field name="name"/>
                                        </strong>
                                    </div>
                                    <div class="o_kanban_record_top_right">
                                        <field name="priority" widget="priority"/>
                                    </div>
                                </div>
                                <div class="o_kanban_record_body">
                                    <field name="user_id" widget="many2one_avatar_user"/>
                                    <t t-if="record.deadline.raw_value">
                                        <br/>
                                        <i class="fa fa-clock-o" title="Deadline"/>
                                        <field name="deadline"/>
                                    </t>
                                </div>
                                <div class="o_kanban_record_bottom">
                                    <div class="oe_kanban_bottom_left">
                                        <field name="progress" widget="progressbar"/>
                                    </div>
                                    <div class="oe_kanban_bottom_right">
                                        <field name="date"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>
</odoo>
"""

    def _generate_menu_views(self, module_name: str, module_title: str) -> str:
        """Generate menu views content."""
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Actions -->
    <record id="action_{module_name}_records" model="ir.actions.act_window">
        <field name="name">{module_title}</field>
        <field name="res_model">{module_name}.record</field>
        <field name="view_mode">kanban,tree,form</field>
        <field name="context">{{'search_default_my_records': 1}}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first record!
            </p>
            <p>
                Click the "New" button to create a new record.
            </p>
        </field>
    </record>

    <!-- Main Menu -->
    <menuitem id="menu_{module_name}_main"
              name="{module_title}"
              sequence="100"
              web_icon="{module_name},static/description/icon.png"/>

    <!-- Sub Menus -->
    <menuitem id="menu_{module_name}_records"
              name="Records"
              parent="menu_{module_name}_main"
              action="action_{module_name}_records"
              sequence="10"/>

    <!-- Configuration Menu -->
    <menuitem id="menu_{module_name}_config"
              name="Configuration"
              parent="menu_{module_name}_main"
              sequence="100"
              groups="base.group_system"/>
</odoo>
"""

    def _generate_security_csv(self, module_name: str) -> str:
        """Generate security CSV content."""
        
        return f"""id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{module_name}_record_user,{module_name}.record.user,model_{module_name}_record,base.group_user,1,1,1,0
access_{module_name}_record_manager,{module_name}.record.manager,model_{module_name}_record,base.group_system,1,1,1,1
"""

    def _generate_security_groups(self, module_name: str) -> str:
        """Generate security groups XML content."""
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Custom Groups -->
        <record id="group_{module_name}_user" model="res.groups">
            <field name="name">{module_name.replace('_', ' ').title()} User</field>
            <field name="category_id" ref="base.module_category_operations"/>
        </record>

        <record id="group_{module_name}_manager" model="res.groups">
            <field name="name">{module_name.replace('_', ' ').title()} Manager</field>
            <field name="category_id" ref="base.module_category_operations"/>
            <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
        </record>

        <!-- Record Rules -->
        <record id="rule_{module_name}_record_user" model="ir.rule">
            <field name="name">{module_name.replace('_', ' ').title()}: User can see own records</field>
            <field name="model_id" ref="model_{module_name}_record"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('group_{module_name}_user'))]"/>
        </record>

        <record id="rule_{module_name}_record_manager" model="ir.rule">
            <field name="name">{module_name.replace('_', ' ').title()}: Manager can see all records</field>
            <field name="model_id" ref="model_{module_name}_record"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('group_{module_name}_manager'))]"/>
        </record>
    </data>
</odoo>
"""

    def _generate_sample_controller(self, module_name: str) -> str:
        """Generate sample controller content."""
        
        return f"""# -*- coding: utf-8 -*-

import json
import logging
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class {module_name.replace('_', '').title()}Controller(http.Controller):
    \"\"\"Controller for {module_name} module web endpoints.\"\"\"

    @http.route('/{module_name}/api/records', auth='user', type='json', methods=['GET'])
    def get_records(self, **kwargs):
        \"\"\"Get records via JSON API.\"\"\"
        try:
            domain = kwargs.get('domain', [])
            limit = kwargs.get('limit', 10)
            offset = kwargs.get('offset', 0)
            
            records = request.env['{module_name}.record'].search(
                domain, limit=limit, offset=offset
            )
            
            return {{
                'success': True,
                'data': records.read(['name', 'state', 'date', 'user_id', 'progress']),
                'total': len(records)
            }}
        except Exception as e:
            _logger.error(f"Error getting records: {{e}}")
            return {{'success': False, 'error': str(e)}}

    @http.route('/{module_name}/api/record/<int:record_id>', auth='user', type='json', methods=['GET'])
    def get_record(self, record_id, **kwargs):
        \"\"\"Get single record by ID.\"\"\"
        try:
            record = request.env['{module_name}.record'].browse(record_id)
            if not record.exists():
                return {{'success': False, 'error': 'Record not found'}}
            
            return {{
                'success': True,
                'data': record.read()[0] if record else None
            }}
        except Exception as e:
            _logger.error(f"Error getting record {{record_id}}: {{e}}")
            return {{'success': False, 'error': str(e)}}

    @http.route('/{module_name}/api/record', auth='user', type='json', methods=['POST'])
    def create_record(self, **kwargs):
        \"\"\"Create new record via API.\"\"\"
        try:
            vals = kwargs.get('data', {{}})
            record = request.env['{module_name}.record'].create(vals)
            
            return {{
                'success': True,
                'data': record.read()[0],
                'message': 'Record created successfully'
            }}
        except ValidationError as e:
            return {{'success': False, 'error': str(e)}}
        except Exception as e:
            _logger.error(f"Error creating record: {{e}}")
            return {{'success': False, 'error': str(e)}}

    @http.route('/{module_name}/api/record/<int:record_id>', auth='user', type='json', methods=['PUT'])
    def update_record(self, record_id, **kwargs):
        \"\"\"Update existing record via API.\"\"\"
        try:
            record = request.env['{module_name}.record'].browse(record_id)
            if not record.exists():
                return {{'success': False, 'error': 'Record not found'}}
            
            vals = kwargs.get('data', {{}})
            record.write(vals)
            
            return {{
                'success': True,
                'data': record.read()[0],
                'message': 'Record updated successfully'
            }}
        except ValidationError as e:
            return {{'success': False, 'error': str(e)}}
        except Exception as e:
            _logger.error(f"Error updating record {{record_id}}: {{e}}")
            return {{'success': False, 'error': str(e)}}

    @http.route('/{module_name}/dashboard', auth='user', type='http', website=True)
    def dashboard(self, **kwargs):
        \"\"\"Dashboard page for module.\"\"\"
        try:
            records = request.env['{module_name}.record'].search([])
            stats = {{
                'total': len(records),
                'draft': len(records.filtered(lambda r: r.state == 'draft')),
                'confirmed': len(records.filtered(lambda r: r.state == 'confirmed')),
                'done': len(records.filtered(lambda r: r.state == 'done')),
                'overdue': len(records.filtered('is_overdue'))
            }}
            
            values = {{
                'records': records[:5],  # Latest 5 records
                'stats': stats
            }}
            
            return request.render('{module_name}.dashboard_template', values)
        except Exception as e:
            _logger.error(f"Error loading dashboard: {{e}}")
            return request.not_found()
"""

    def _generate_sample_js(self, module_name: str) -> str:
        """Generate sample JavaScript content."""
        
        return f"""/** @odoo-module **/

import {{ Component }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";

/**
 * {module_name.replace('_', ' ').title()} Custom Widget
 */
class {module_name.replace('_', '').title()}Widget extends Component {{
    setup() {{
        this.orm = useService("orm");
        this.notification = useService("notification");
    }}

    async loadData() {{
        try {{
            const records = await this.orm.searchRead(
                "{module_name}.record",
                [],
                ["name", "state", "progress"]
            );
            return records;
        }} catch (error) {{
            this.notification.add("Error loading data", {{
                type: "danger",
            }});
            console.error("Error loading data:", error);
        }}
    }}

    onRecordClick(recordId) {{
        this.env.services.action.doAction({{
            type: "ir.actions.act_window",
            res_model: "{module_name}.record",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        }});
    }}
}}

{module_name.replace('_', '').title()}Widget.template = "web.{module_name}_widget";

registry.category("view_widgets").add("{module_name}_widget", {module_name.replace('_', '').title()}Widget);

/**
 * Dashboard functionality
 */
odoo.define('{module_name}.dashboard', function (require) {{
    'use strict';

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');

    var Dashboard = Widget.extend({{
        template: '{module_name}.dashboard_template',
        
        events: {{
            'click .refresh-stats': '_refreshStats',
            'click .record-item': '_openRecord',
        }},

        init: function (parent, options) {{
            this._super.apply(this, arguments);
            this.options = options || {{}};
        }},

        start: function () {{
            var self = this;
            return this._super().then(function () {{
                self._loadDashboardData();
            }});
        }},

        _loadDashboardData: function () {{
            var self = this;
            return rpc.query({{
                route: '/{module_name}/api/records',
                params: {{
                    limit: 10
                }}
            }}).then(function (result) {{
                if (result.success) {{
                    self._updateDashboard(result.data);
                }} else {{
                    self._showError(result.error);
                }}
            }});
        }},

        _updateDashboard: function (data) {{
            // Update dashboard with fresh data
            this.$('.record-count').text(data.length);
            this._renderRecordList(data);
        }},

        _renderRecordList: function (records) {{
            var $list = this.$('.record-list');
            $list.empty();
            
            records.forEach(function (record) {{
                var $item = $('<div class="record-item" data-id="' + record.id + '">');
                $item.html(`
                    <h5>${{record.name}}</h5>
                    <p>Status: <span class="badge badge-${{record.state}}">${{record.state}}</span></p>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${{record.progress}}%"></div>
                    </div>
                `);
                $list.append($item);
            }});
        }},

        _refreshStats: function () {{
            this._loadDashboardData();
        }},

        _openRecord: function (event) {{
            var recordId = $(event.currentTarget).data('id');
            this.do_action({{
                type: 'ir.actions.act_window',
                res_model: '{module_name}.record',
                res_id: recordId,
                views: [[false, 'form']],
                target: 'current'
            }});
        }},

        _showError: function (message) {{
            this.displayNotification({{
                title: 'Error',
                message: message,
                type: 'danger'
            }});
        }}
    }});

    return Dashboard;
}});
"""

    def _generate_sample_css(self, module_name: str) -> str:
        """Generate sample CSS content."""
        
        return f"""/* {module_name.replace('_', ' ').title()} Custom Styles */

.o_{module_name}_dashboard {{
    padding: 20px;
    background: #f8f9fa;
}}

.o_{module_name}_stats {{
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
}}

.o_{module_name}_stat_card {{
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    flex: 1;
    text-align: center;
}}

.o_{module_name}_stat_card .number {{
    font-size: 2.5rem;
    font-weight: bold;
    color: #007bff;
}}

.o_{module_name}_stat_card .label {{
    font-size: 0.9rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.o_{module_name}_record_list {{
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

.o_{module_name}_record_item {{
    padding: 15px 20px;
    border-bottom: 1px solid #e9ecef;
    cursor: pointer;
    transition: background-color 0.2s;
}}

.o_{module_name}_record_item:hover {{
    background-color: #f8f9fa;
}}

.o_{module_name}_record_item:last-child {{
    border-bottom: none;
}}

.o_{module_name}_record_item h5 {{
    margin: 0 0 8px 0;
    color: #495057;
}}

.o_{module_name}_record_item .meta {{
    font-size: 0.85rem;
    color: #6c757d;
}}

.o_{module_name}_progress_bar {{
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 8px;
}}

.o_{module_name}_progress_fill {{
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997);
    transition: width 0.3s ease;
}}

/* Status badges */
.badge-draft {{
    background-color: #6c757d;
}}

.badge-confirmed {{
    background-color: #007bff;
}}

.badge-done {{
    background-color: #28a745;
}}

.badge-cancelled {{
    background-color: #dc3545;
}}

/* Form enhancements */
.o_form_view .o_{module_name}_form {{
    max-width: 1200px;
    margin: 0 auto;
}}

.o_{module_name}_form .o_group {{
    margin-bottom: 20px;
}}

.o_{module_name}_form .o_field_widget {{
    margin-bottom: 10px;
}}

/* Responsive design */
@media (max-width: 768px) {{
    .o_{module_name}_stats {{
        flex-direction: column;
        gap: 15px;
    }}
    
    .o_{module_name}_stat_card .number {{
        font-size: 2rem;
    }}
    
    .o_{module_name}_dashboard {{
        padding: 15px;
    }}
}}

/* Kanban enhancements */
.o_kanban_view .o_{module_name}_kanban_card {{
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}}

.o_kanban_view .o_{module_name}_kanban_card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}}

.o_kanban_view .o_{module_name}_priority_high {{
    border-left: 4px solid #dc3545;
}}

.o_kanban_view .o_{module_name}_priority_medium {{
    border-left: 4px solid #ffc107;
}}

.o_kanban_view .o_{module_name}_priority_low {{
    border-left: 4px solid #28a745;
}}

/* Animation classes */
.o_{module_name}_fade_in {{
    animation: fadeIn 0.5s ease-in;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.o_{module_name}_slide_up {{
    animation: slideUp 0.3s ease-out;
}}

@keyframes slideUp {{
    from {{ transform: translateY(20px); opacity: 0; }}
    to {{ transform: translateY(0); opacity: 1; }}
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
    .o_{module_name}_stat_card {{
        background: #2d2d2d;
        color: #ffffff;
    }}
    
    .o_{module_name}_record_list {{
        background: #2d2d2d;
    }}
    
    .o_{module_name}_record_item {{
        border-bottom-color: #444444;
    }}
    
    .o_{module_name}_record_item:hover {{
        background-color: #3d3d3d;
    }}
}}
"""

    def _generate_readme(self, module_name: str, module_title: str, description: str, author: str) -> str:
        """Generate README content."""
        
        return f"""# {module_title}

{description or f"A comprehensive Odoo 17 module for {module_title.lower()}."}

## Features

- 🚀 **Modern Architecture**: Built with Odoo 17 best practices
- 🔒 **Security**: Comprehensive access rights and record rules
- 📱 **Responsive UI**: Works seamlessly on desktop and mobile
- 🎨 **Rich Views**: Tree, Form, Kanban, and Search views
- 📊 **Dashboard**: Real-time statistics and insights
- 🔄 **State Management**: Workflow with draft, confirmed, done states
- 📈 **Progress Tracking**: Visual progress indicators
- 🔔 **Notifications**: Smart alerts and overdue detection
- 🎯 **Priority System**: Flexible priority management
- 👥 **Multi-user**: User assignment and ownership
- 🌐 **API Ready**: RESTful JSON API endpoints
- 📋 **Reporting**: Built-in report templates

## Installation

### Prerequisites

- Odoo 17.0 or later
- Python 3.8+
- PostgreSQL 12+

### Method 1: Using Docker (Recommended)

1. **Copy the module to your Odoo addons directory:**
   ```bash
   cp -r {module_name} /path/to/odoo/addons/
   ```

2. **Update Odoo apps list:**
   ```bash
   docker-compose exec odoo odoo --update=all --stop-after-init
   ```

3. **Install the module:**
   ```bash
   docker-compose exec odoo odoo -i {module_name} --stop-after-init -d your_database
   ```

### Method 2: Manual Installation

1. **Navigate to Odoo directory and restart:**
   ```bash
   cd /path/to/odoo
   ./odoo-bin -u {module_name} -d your_database
   ```

2. **Install via Odoo UI:**
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "{module_title}"
   - Click **Install**

## Configuration

### Access Rights

The module includes predefined user groups:

- **{module_title} User**: Basic access to create and manage own records
- **{module_title} Manager**: Full administrative access

### Settings

Configure the module through:
- **Settings** → **Technical** → **Parameters** → **System Parameters**

Key parameters:
- `{module_name}.default_priority`: Default priority for new records
- `{module_name}.auto_deadline`: Auto-set deadline (days from creation)

## Usage

### Creating Records

1. Navigate to **{module_title}** → **Records**
2. Click **New** to create a record
3. Fill in the required information:
   - **Name**: Descriptive title
   - **Assigned User**: Responsible person
   - **Date**: Start date
   - **Deadline**: Target completion date
   - **Priority**: Importance level

### Managing Workflow

Records follow a simple workflow:

```
Draft → Confirmed → Done
  ↓         ↓
Cancelled ←---
```

Use the status bar buttons to change states:
- **Confirm**: Mark record as confirmed and in progress
- **Mark Done**: Complete the record (sets progress to 100%)
- **Cancel**: Cancel the record
- **Reset to Draft**: Return to draft state

### Dashboard

Access the dashboard at: `http://your-odoo-instance/{module_name}/dashboard`

Features:
- Real-time statistics
- Recent records overview
- Progress indicators
- Quick actions

### API Usage

The module provides RESTful JSON API endpoints:

#### Get Records
```bash
curl -X GET "http://your-odoo/web/dataset/call_kw/{module_name}.record/search_read" \\
  -H "Content-Type: application/json" \\
  --data '{{"params": {{"domain": [], "fields": ["name", "state", "progress"]}}}}'
```

#### Create Record
```bash
curl -X POST "http://your-odoo/{module_name}/api/record" \\
  -H "Content-Type: application/json" \\
  --data '{{"data": {{"name": "New Record", "description": "Test record"}}}}'
```

## Development

### Module Structure

```
{module_name}/
├── __init__.py              # Module initialization
├── __manifest__.py          # Module manifest
├── README.md               # This file
├── models/                 # Data models
│   ├── __init__.py
│   └── models.py          # Main model definitions
├── views/                  # UI definitions
│   ├── views.xml          # Form, tree, kanban views
│   └── menu.xml           # Menu structure
├── security/               # Access control
│   ├── ir.model.access.csv # Model permissions
│   └── security.xml       # Groups and record rules
├── controllers/            # Web controllers
│   └── main.py            # API endpoints
├── static/                 # Static assets
│   └── src/
│       ├── js/custom.js   # JavaScript functionality
│       ├── css/style.css  # Custom styling
│       └── xml/           # QWeb templates
└── data/                  # Data files
    └── demo_data.xml      # Demo/sample data
```

### Testing

Run module tests:
```bash
docker-compose exec odoo odoo --test-enable --stop-after-init -d test_db -i {module_name}
```

### Customization

#### Adding Fields

1. Edit `models/models.py` to add new fields
2. Update views in `views/views.xml`
3. Update security in `security/ir.model.access.csv`
4. Restart Odoo and update the module

#### Custom Actions

Add custom actions to the model:
```python
def custom_action(self):
    \"\"\"Custom action implementation.\"\"\"
    # Your code here
    return True
```

## Troubleshooting

### Common Issues

1. **Module not appearing in Apps list**
   - Ensure the module is in the correct addons path
   - Check `__manifest__.py` syntax
   - Update apps list: Apps → Update Apps List

2. **Permission errors**
   - Check user groups assignment
   - Verify `ir.model.access.csv` entries
   - Review record rules in `security.xml`

3. **View errors**
   - Validate XML syntax in view files
   - Check field names match model definitions
   - Verify action and menu references

### Debugging

Enable developer mode:
1. Go to **Settings**
2. Activate **Developer Tools**
3. Use **Technical** menus for debugging

View logs:
```bash
# Docker setup
docker-compose logs -f odoo

# Manual setup
tail -f /var/log/odoo/odoo.log
```

## API Reference

### Models

#### {module_name}.record

Main model for managing records.

**Fields:**
- `name` (Char): Record name
- `description` (Text): Detailed description
- `state` (Selection): Current status
- `date` (Date): Start date
- `deadline` (Datetime): Target completion
- `priority` (Selection): Priority level
- `progress` (Float): Completion percentage
- `user_id` (Many2one): Assigned user
- `company_id` (Many2one): Company
- `active` (Boolean): Active flag

**Methods:**
- `action_confirm()`: Confirm the record
- `action_done()`: Mark as completed
- `action_cancel()`: Cancel the record
- `action_reset_to_draft()`: Reset to draft

### Controllers

#### /{module_name}/api/records [GET]
Get list of records with filtering and pagination.

#### /{module_name}/api/record [POST]
Create a new record.

#### /{module_name}/api/record/<int:id> [GET]
Get specific record by ID.

#### /{module_name}/api/record/<int:id> [PUT]
Update existing record.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines

- Follow Odoo coding standards
- Add proper docstrings
- Include unit tests
- Update documentation
- Maintain backward compatibility

## Support

For support and customizations:
- **Author**: {author}
- **Email**: support@osusapps.com
- **Website**: https://osusapps.com
- **Documentation**: https://docs.osusapps.com/{module_name}

## License

This module is licensed under LGPL-3.0.

## Changelog

### Version 1.0.0
- Initial release
- Basic CRUD operations
- Workflow management
- Dashboard implementation
- API endpoints
- Security implementation

---

*Built with ❤️ by {author} for the Odoo community.*
"""

    # Continue with more tool implementations...
    # (The rest of the tools will be implemented similarly)
