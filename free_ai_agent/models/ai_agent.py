# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AIAgent(models.Model):
    _name = 'free.ai.agent'
    _description = 'Free AI Agent'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char('Agent Name', required=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    
    # Agent Configuration
    agent_type = fields.Selection([
        ('sales', 'Sales Assistant'),
        ('inventory', 'Inventory Manager'),
        ('accounting', 'Accounting Helper'),
        ('crm', 'CRM Assistant'),
        ('project', 'Project Manager'),
        ('hr', 'HR Assistant'),
        ('custom', 'Custom Agent'),
    ], string='Agent Type', required=True, default='custom')
    
    # AI Configuration
    ai_provider_id = fields.Many2one('ai.provider', string='AI Provider', required=True)
    system_prompt = fields.Text('System Prompt', required=True, 
                               help="Instructions that define the agent's role and behavior")
    max_tokens = fields.Integer('Max Tokens', default=2000)
    temperature = fields.Float('Temperature', default=0.7)
    
    # Execution Settings
    execution_mode = fields.Selection([
        ('manual', 'Manual Only'),
        ('scheduled', 'Scheduled'),
        ('triggered', 'Event Triggered'),
    ], string='Execution Mode', default='manual')
    
    # Scheduling
    execute_every = fields.Integer('Execute Every', default=1)
    execute_unit = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string='Execute Unit', default='days')
    
    last_run = fields.Datetime('Last Run', readonly=True)
    next_run = fields.Datetime('Next Run')
    
    # Model Access
    model_ids = fields.Many2many('ir.model', string='Accessible Models',
                                help="Models this agent can access and analyze")
    
    # Agent Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('running', 'Running'),
        ('error', 'Error'),
    ], string='Status', default='draft')
    
    # Usage Statistics
    total_executions = fields.Integer('Total Executions', readonly=True, default=0)
    successful_executions = fields.Integer('Successful Executions', readonly=True, default=0)
    failed_executions = fields.Integer('Failed Executions', readonly=True, default=0)
    total_tokens_used = fields.Integer('Total Tokens Used', readonly=True, default=0)
    
    # Relationships
    response_history_ids = fields.One2many('free.ai.response.history', 'agent_id', 
                                         string='Response History')
    
    sequence = fields.Integer('Sequence', default=10)
    user_ids = fields.Many2many('res.users', string='Shared With')
    is_favorite = fields.Boolean('Is Favorite')
    
    # Context and Data
    context_data = fields.Text('Context Data', help="Additional context or data for the agent")
    
    @api.onchange('execute_every', 'execute_unit', 'last_run')
    def _onchange_schedule_fields(self):
        """Update next_run based on schedule settings"""
        if self.execute_every and self.execute_unit and self.last_run:
            self.next_run = self.last_run + relativedelta(**{self.execute_unit: self.execute_every})
    
    @api.onchange('agent_type')
    def _onchange_agent_type(self):
        """Set default system prompt based on agent type"""
        prompts = {
            'sales': """You are a Sales Assistant AI for an Odoo ERP system. Your role is to:
- Analyze sales data and trends
- Identify opportunities and risks
- Generate sales reports and insights
- Suggest actions to improve sales performance
- Help with customer relationship management

Always provide actionable insights based on the data available.""",
            
            'inventory': """You are an Inventory Manager AI for an Odoo ERP system. Your role is to:
- Monitor stock levels and inventory movements
- Identify low stock situations and overstock issues
- Analyze inventory turnover and trends
- Suggest reorder points and quantities
- Optimize inventory management processes

Focus on maintaining optimal inventory levels while minimizing costs.""",
            
            'accounting': """You are an Accounting Helper AI for an Odoo ERP system. Your role is to:
- Analyze financial data and transactions
- Identify accounting discrepancies and issues
- Generate financial reports and insights
- Help with reconciliation processes
- Ensure compliance with accounting standards

Provide accurate financial analysis and recommendations.""",
            
            'crm': """You are a CRM Assistant AI for an Odoo ERP system. Your role is to:
- Analyze customer data and interactions
- Identify sales opportunities and lead quality
- Track customer satisfaction and retention
- Suggest follow-up actions and strategies
- Help optimize the sales pipeline

Focus on improving customer relationships and conversion rates.""",
            
            'project': """You are a Project Manager AI for an Odoo ERP system. Your role is to:
- Monitor project progress and milestones
- Identify bottlenecks and risks
- Analyze resource allocation and utilization
- Track time and budget consumption
- Suggest improvements to project workflows

Help ensure projects are delivered on time and within budget.""",
            
            'hr': """You are an HR Assistant AI for an Odoo ERP system. Your role is to:
- Analyze employee data and performance
- Monitor attendance and leave patterns
- Identify HR trends and issues
- Help with recruitment and onboarding processes
- Ensure compliance with HR policies

Focus on improving employee satisfaction and organizational efficiency.""",
        }
        
        if self.agent_type in prompts:
            self.system_prompt = prompts[self.agent_type]
    
    def execute_agent(self):
        """Execute the AI agent"""
        if not self.active:
            raise ValidationError(_('Agent is not active'))
        
        if not self.ai_provider_id:
            raise ValidationError(_('No AI provider configured'))
        
        # Update status
        self.status = 'running'
        self.last_run = fields.Datetime.now()
        
        try:
            # Create response history record
            response_history = self.env['free.ai.response.history'].create({
                'agent_id': self.id,
                'execution_type': 'scheduled' if self.env.context.get('from_cron') else 'manual',
                'status': 'running',
                'started_at': fields.Datetime.now(),
            })
            
            # Execute the agent logic
            result = self._execute_agent_logic(response_history)
            
            # Update statistics
            self.total_executions += 1
            if result.get('success'):
                self.successful_executions += 1
                self.status = 'active'
                response_history.status = 'completed'
            else:
                self.failed_executions += 1
                self.status = 'error'
                response_history.status = 'failed'
                response_history.error_message = result.get('error', 'Unknown error')
            
            # Update tokens used
            if result.get('tokens_used'):
                self.total_tokens_used += result['tokens_used']
            
            # Schedule next run
            if self.execution_mode == 'scheduled':
                self.next_run = self.last_run + relativedelta(**{self.execute_unit: self.execute_every})
            
            response_history.completed_at = fields.Datetime.now()
            
            return self._return_execution_result(result, response_history)
            
        except Exception as e:
            _logger.error("Agent execution failed: %s", str(e))
            self.status = 'error'
            self.failed_executions += 1
            raise
    
    def _execute_agent_logic(self, response_history):
        """Core agent execution logic"""
        try:
            # Prepare context data
            context_info = self._prepare_context_data()
            
            # Build messages for AI
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"""
Please analyze the current state of the system and provide insights and recommendations.

Context Information:
{context_info}

Agent Type: {self.agent_type}
Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please provide:
1. Current situation analysis
2. Key insights and findings
3. Specific recommendations
4. Suggested actions to take

Be specific and actionable in your recommendations.
"""}
            ]
            
            # Send request to AI provider
            ai_response = self.ai_provider_id.send_request(
                messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Store the response
            response_history.write({
                'response_content': ai_response['content'],
                'raw_response': str(ai_response.get('raw_response', {})),
                'tokens_used': ai_response.get('tokens_used', 0),
                'ai_model': ai_response.get('model', ''),
            })
            
            return {
                'success': True,
                'response': ai_response['content'],
                'tokens_used': ai_response.get('tokens_used', 0),
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def _prepare_context_data(self):
        """Prepare context data for the AI agent"""
        context_parts = []
        
        # Add accessible model information
        if self.model_ids:
            context_parts.append("Available Data Models:")
            for model in self.model_ids:
                try:
                    model_obj = self.env[model.model]
                    record_count = model_obj.search_count([])
                    context_parts.append(f"- {model.name}: {record_count} records")
                except Exception:
                    context_parts.append(f"- {model.name}: Access restricted")
        
        # Add custom context data
        if self.context_data:
            context_parts.append("Additional Context:")
            context_parts.append(self.context_data)
        
        # Add recent activity summary (last 7 days)
        context_parts.append("\\nRecent Activity Summary:")
        context_parts.append(f"Last execution: {self.last_run or 'Never'}")
        context_parts.append(f"Total executions: {self.total_executions}")
        context_parts.append(f"Success rate: {(self.successful_executions / max(self.total_executions, 1)) * 100:.1f}%")
        
        return "\\n".join(context_parts)
    
    def _return_execution_result(self, result, response_history):
        """Return execution result to user"""
        if self.env.context.get('from_form'):
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'free.ai.response.history',
                'res_id': response_history.id,
                'view_mode': 'form',
                'target': 'new',
            }
        
        message_type = 'success' if result.get('success') else 'danger'
        message = result.get('response', result.get('error', 'Execution completed'))[:200]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': message_type,
                'message': message,
            }
        }
    
    def show_response_history(self):
        """Show agent response history"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Response History',
            'res_model': 'free.ai.response.history',
            'view_mode': 'tree,form',
            'domain': [('agent_id', '=', self.id)],
            'context': {'default_agent_id': self.id},
        }
    
    def show_last_response(self):
        """Show the last response"""
        last_response = self.response_history_ids.filtered(lambda r: r.status == 'completed').sorted('id', reverse=True)[:1]
        if not last_response:
            raise ValidationError(_('No completed responses found'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Last Response',
            'res_model': 'free.ai.response.history',
            'res_id': last_response.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    @api.model
    def run_scheduled_agents(self):
        """Cron method to run scheduled agents"""
        current_time = fields.Datetime.now()
        agents_to_run = self.search([
            ('active', '=', True),
            ('execution_mode', '=', 'scheduled'),
            ('next_run', '<=', current_time),
            ('status', '!=', 'running'),
        ])
        
        for agent in agents_to_run:
            try:
                _logger.info("Running scheduled agent: %s", agent.name)
                agent.with_context(from_cron=True).execute_agent()
            except Exception as e:
                _logger.error("Failed to run scheduled agent %s: %s", agent.name, str(e))
    
    def test_ai_connection(self):
        """Test AI provider connection"""
        if not self.ai_provider_id:
            raise ValidationError(_('No AI provider configured'))
        
        return self.ai_provider_id.test_connection()