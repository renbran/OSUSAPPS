# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenAIBusinessAgent(models.Model):
    """Enhanced AI Agent optimized for OpenAI integration with advanced business intelligence"""
    
    _name = 'openai.business.agent'
    _description = 'OpenAI Business Intelligence Agent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, sequence, name'
    _rec_name = 'name'

    name = fields.Char('Agent Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    description = fields.Text('Description')
    
    # Enhanced Agent Configuration
    agent_category = fields.Selection([
        ('sales_intelligence', 'Sales Intelligence'),
        ('inventory_optimization', 'Inventory Optimization'), 
        ('financial_analysis', 'Financial Analysis'),
        ('customer_insights', 'Customer Insights'),
        ('project_intelligence', 'Project Intelligence'),
        ('hr_analytics', 'HR Analytics'),
        ('business_forecasting', 'Business Forecasting'),
        ('risk_assessment', 'Risk Assessment'),
        ('performance_monitoring', 'Performance Monitoring'),
        ('custom_intelligence', 'Custom Intelligence'),
    ], string='Agent Category', required=True, tracking=True)
    
    # Priority and Urgency
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'), 
        ('2', 'High'),
        ('3', 'Critical'),
    ], string='Priority', default='1', tracking=True)
    
    urgency_level = fields.Selection([
        ('routine', 'Routine Analysis'),
        ('important', 'Important Insights'),
        ('urgent', 'Urgent Alerts'),
        ('critical', 'Critical Warnings'),
    ], string='Urgency Level', default='routine')
    
    # OpenAI Specific Configuration
    openai_model = fields.Selection([
        ('gpt-4o', 'GPT-4o (Latest, Most Capable)'),
        ('gpt-4o-mini', 'GPT-4o Mini (Fast & Efficient)'),
        ('gpt-4-turbo', 'GPT-4 Turbo (Advanced Reasoning)'),
        ('gpt-4', 'GPT-4 (High Quality)'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo (Cost Effective)'),
    ], string='OpenAI Model', default='gpt-4o-mini', required=True)
    
    max_tokens = fields.Integer('Max Tokens', default=2000, help="Maximum tokens for response (controls length and cost)")
    temperature = fields.Float('Temperature', default=0.3, help="0.0=Focused, 1.0=Creative")
    
    # Advanced Prompt Engineering
    system_prompt = fields.Text('System Prompt', required=True, help="Define the agent's expertise and behavior")
    business_context = fields.Text('Business Context', help="Specific context about your business")
    analysis_focus = fields.Text('Analysis Focus', help="What specific insights to focus on")
    output_format = fields.Selection([
        ('insights', 'Business Insights'),
        ('alerts', 'Alert Notifications'),
        ('recommendations', 'Action Recommendations'),
        ('reports', 'Detailed Reports'),
        ('forecasts', 'Predictions & Forecasts'),
        ('analysis', 'Data Analysis'),
    ], string='Output Format', default='insights')
    
    # Execution Configuration
    execution_mode = fields.Selection([
        ('manual', 'Manual Execution'),
        ('scheduled', 'Scheduled Analysis'),
        ('triggered', 'Event Triggered'),
        ('realtime', 'Real-time Monitoring'),
    ], string='Execution Mode', default='manual', tracking=True)
    
    # Enhanced Scheduling
    schedule_frequency = fields.Selection([
        ('hourly', 'Every Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),  
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('custom', 'Custom Schedule'),
    ], string='Frequency', default='daily')
    
    schedule_time = fields.Float('Execution Time', default=9.0, help="Hour of day (0-24)")
    custom_cron = fields.Char('Custom Cron Expression', help="For advanced scheduling")
    
    last_run = fields.Datetime('Last Execution', readonly=True)
    next_run = fields.Datetime('Next Execution')
    
    # Business Data Access
    monitored_models = fields.Many2many('ir.model', string='Monitored Models',
                                       help="Odoo models this agent can analyze")
    data_filters = fields.Text('Data Filters', help="JSON filters for data selection")
    analysis_period = fields.Integer('Analysis Period (Days)', default=30,
                                   help="How many days of data to analyze")
    
    # Intelligence Configuration  
    enable_trend_analysis = fields.Boolean('Trend Analysis', default=True)
    enable_anomaly_detection = fields.Boolean('Anomaly Detection', default=True)
    enable_predictive_analysis = fields.Boolean('Predictive Analysis', default=False)
    enable_comparative_analysis = fields.Boolean('Comparative Analysis', default=True)
    
    # Notification & Alert System
    notification_enabled = fields.Boolean('Enable Notifications', default=True)
    notification_threshold = fields.Selection([
        ('all', 'All Results'),
        ('important', 'Important Only'),
        ('critical', 'Critical Only'),
    ], string='Notification Threshold', default='important')
    
    notification_channels = fields.Selection([
        ('internal', 'Internal Messages'),
        ('email', 'Email Notifications'),
        ('both', 'Both'),
    ], string='Notification Channels', default='internal')
    
    notification_users = fields.Many2many('res.users', string='Notify Users')
    
    # Performance Metrics
    total_executions = fields.Integer('Total Executions', readonly=True, default=0)
    successful_executions = fields.Integer('Successful Executions', readonly=True, default=0)
    failed_executions = fields.Integer('Failed Executions', readonly=True, default=0)
    total_tokens_used = fields.Integer('Total Tokens Used', readonly=True, default=0)
    estimated_cost = fields.Float('Estimated Cost ($)', readonly=True, default=0.0)
    
    # Agent Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('running', 'Running Analysis'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('paused', 'Paused'),
    ], string='Status', default='draft', tracking=True)
    
    # Results and History
    execution_history_ids = fields.One2many('openai.execution.history', 'agent_id', 
                                          string='Execution History')
    
    # Relationships
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible User', 
                            default=lambda self: self.env.user, tracking=True)
    
    @api.onchange('agent_category')
    def _onchange_agent_category(self):
        """Set default configuration based on agent category"""
        prompts = {
            'sales_intelligence': {
                'system_prompt': """You are a Sales Intelligence AI specialized in analyzing sales performance and identifying opportunities.

ROLE: Expert Sales Analyst with deep knowledge of sales metrics, customer behavior, and revenue optimization.

ANALYZE:
- Sales trends and patterns over time
- Top performing products, customers, and sales representatives  
- Pipeline health and conversion rates
- Revenue forecasts and goal achievement
- Customer acquisition and retention metrics
- Seasonal and cyclical sales patterns

PROVIDE:
1. Key performance indicators and trends
2. Actionable insights for sales improvement
3. Specific recommendations with expected impact
4. Risk alerts and opportunity identification
5. Comparative analysis with previous periods

Always include specific numbers, percentages, and clear action items.""",
                'output_format': 'insights',
                'openai_model': 'gpt-4o-mini',
                'temperature': 0.2,
            },
            
            'inventory_optimization': {
                'system_prompt': """You are an Inventory Optimization AI focused on stock management and supply chain efficiency.

ROLE: Expert Supply Chain Analyst with expertise in inventory management, demand forecasting, and cost optimization.

ANALYZE:
- Current stock levels vs. optimal levels
- Stock turnover rates and aging inventory
- Demand patterns and seasonality
- Supplier performance and lead times
- Stock-out risks and overstock situations
- Purchase timing optimization

PROVIDE:
1. Immediate reorder recommendations with quantities
2. Overstock alerts and liquidation suggestions  
3. Demand forecasts for key products
4. Supplier performance insights
5. Cost optimization opportunities

Always prioritize preventing stock-outs while minimizing carrying costs.""",
                'output_format': 'recommendations',
                'openai_model': 'gpt-4o-mini',
                'temperature': 0.1,
            },
            
            'financial_analysis': {
                'system_prompt': """You are a Financial Analysis AI specializing in business financial health and performance.

ROLE: Expert Financial Analyst with deep knowledge of accounting, cash flow, profitability, and financial risk assessment.

ANALYZE:
- Revenue and profitability trends
- Cash flow patterns and forecasts
- Expense analysis and cost optimization
- Account receivables and payables aging
- Financial ratios and KPIs
- Budget vs. actual performance

PROVIDE:
1. Financial health assessment
2. Cash flow forecasts and alerts
3. Profitability analysis by product/customer
4. Cost reduction opportunities
5. Financial risk warnings

Focus on actionable financial insights that drive business decisions.""",
                'output_format': 'analysis',
                'openai_model': 'gpt-4o',
                'temperature': 0.1,
            },
        }
        
        if self.agent_category in prompts:
            config = prompts[self.agent_category]
            for field, value in config.items():
                setattr(self, field, value)
    
    def execute_intelligence_analysis(self):
        """Execute the AI agent analysis"""
        if not self.active:
            raise ValidationError(_('Agent is not active'))
            
        self.status = 'running'
        self.last_run = fields.Datetime.now()
        
        try:
            # Create execution history record
            execution = self.env['openai.execution.history'].create({
                'agent_id': self.id,
                'execution_type': 'scheduled' if self.env.context.get('from_cron') else 'manual',
                'status': 'running',
                'started_at': fields.Datetime.now(),
            })
            
            # Gather business data
            business_data = self._gather_business_intelligence()
            
            # Prepare OpenAI request
            messages = self._prepare_openai_messages(business_data)
            
            # Execute OpenAI analysis
            result = self._execute_openai_analysis(messages)
            
            # Process and store results
            self._process_analysis_results(result, execution)
            
            # Send notifications if configured
            if self.notification_enabled:
                self._send_notifications(result)
            
            # Update statistics
            self.total_executions += 1
            self.successful_executions += 1
            self.status = 'completed'
            
            # Schedule next execution
            self._schedule_next_execution()
            
            return self._return_execution_result(True, execution)
            
        except Exception as e:
            _logger.error("Intelligence analysis failed for agent %s: %s", self.name, str(e))
            self.status = 'error'
            self.failed_executions += 1
            execution.status = 'failed'
            execution.error_message = str(e)
            raise
    
    def _gather_business_intelligence(self):
        """Gather relevant business data for analysis"""
        data = {
            'analysis_period': self.analysis_period,
            'current_date': fields.Date.today().strftime('%Y-%m-%d'),
            'business_context': self.business_context or 'General business analysis',
        }
        
        # Gather data from monitored models
        for model in self.monitored_models:
            try:
                model_obj = self.env[model.model]
                
                # Apply date filters
                domain = []
                if hasattr(model_obj, 'create_date'):
                    cutoff_date = fields.Date.today() - timedelta(days=self.analysis_period)
                    domain.append(('create_date', '>=', cutoff_date))
                
                # Apply custom filters if configured
                if self.data_filters:
                    try:
                        custom_filters = json.loads(self.data_filters)
                        domain.extend(custom_filters)
                    except:
                        pass
                
                records = model_obj.search(domain, limit=1000)
                record_count = len(records)
                
                data[model.model] = {
                    'count': record_count,
                    'model_name': model.name,
                }
                
                # Add model-specific insights
                if model.model == 'sale.order':
                    total_amount = sum(records.mapped('amount_total'))
                    data[model.model].update({
                        'total_revenue': total_amount,
                        'average_order': total_amount / max(record_count, 1),
                        'states': dict(records.read_group([], ['state'], ['state'])),
                    })
                    
            except Exception as e:
                _logger.warning("Failed to gather data from model %s: %s", model.model, str(e))
        
        return data
        
    def _prepare_openai_messages(self, business_data):
        """Prepare messages for OpenAI API"""
        system_message = f"""{self.system_prompt}

BUSINESS CONTEXT:
{self.business_context or 'Standard business analysis'}

ANALYSIS FOCUS:
{self.analysis_focus or 'General performance analysis'}

OUTPUT REQUIREMENTS:
- Format: {self.output_format}
- Urgency Level: {self.urgency_level}
- Include specific metrics and numbers
- Provide actionable recommendations
- Highlight critical issues requiring immediate attention
"""

        user_message = f"""Please analyze the following business data and provide {self.output_format}:

ANALYSIS PERIOD: Last {self.analysis_period} days (until {business_data['current_date']})

BUSINESS DATA:
{json.dumps(business_data, indent=2, default=str)}

Please provide your analysis focusing on:
1. Key insights and trends
2. Performance assessment
3. Specific recommendations
4. Risk alerts or opportunities
5. Next steps and action items

Make your response practical and actionable for business decision-making."""

        return [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message}
        ]
    
    def _execute_openai_analysis(self, messages):
        """Execute analysis using OpenAI API"""
        # Get OpenAI provider
        provider = self.env['ai.provider'].search([
            ('provider_type', '=', 'openai'),
            ('active', '=', True)
        ], limit=1)
        
        if not provider:
            raise ValidationError(_('No active OpenAI provider configured'))
        
        # Send request to OpenAI
        response = provider.send_request(
            messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            model=self.openai_model
        )
        
        # Update token usage
        tokens_used = response.get('tokens_used', 0)
        self.total_tokens_used += tokens_used
        
        # Estimate cost (approximate rates)
        cost_per_token = 0.000002  # Rough estimate for GPT models
        self.estimated_cost += tokens_used * cost_per_token
        
        return response
    
    def _process_analysis_results(self, result, execution):
        """Process and store analysis results"""
        execution.write({
            'response_content': result['content'],
            'raw_response': str(result.get('raw_response', {})),
            'tokens_used': result.get('tokens_used', 0),
            'ai_model': result.get('model', self.openai_model),
            'status': 'completed',
            'completed_at': fields.Datetime.now(),
        })
    
    def _send_notifications(self, result):
        """Send notifications based on configuration"""
        if not self.notification_users:
            return
            
        subject = f"AI Analysis: {self.name}"
        body = f"""
        <h3>AI Intelligence Report</h3>
        <p><strong>Agent:</strong> {self.name}</p>
        <p><strong>Category:</strong> {dict(self._fields['agent_category'].selection)[self.agent_category]}</p>
        <p><strong>Execution Time:</strong> {self.last_run}</p>
        
        <h4>Analysis Results:</h4>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            {result['content'][:500]}...
        </div>
        
        <p><a href="/web#id={self.id}&model=openai.business.agent&view_type=form">View Full Analysis</a></p>
        """
        
        for user in self.notification_users:
            self.message_post(
                subject=subject,
                body=body,
                partner_ids=[user.partner_id.id],
                message_type='notification'
            )
    
    def _schedule_next_execution(self):
        """Schedule the next execution based on frequency"""
        if self.execution_mode != 'scheduled':
            return
            
        if self.schedule_frequency == 'hourly':
            self.next_run = self.last_run + timedelta(hours=1)
        elif self.schedule_frequency == 'daily':
            self.next_run = self.last_run + timedelta(days=1)
        elif self.schedule_frequency == 'weekly':
            self.next_run = self.last_run + timedelta(weeks=1)
        elif self.schedule_frequency == 'monthly':
            self.next_run = self.last_run + relativedelta(months=1)
        elif self.schedule_frequency == 'quarterly':
            self.next_run = self.last_run + relativedelta(months=3)
    
    def _return_execution_result(self, success, execution):
        """Return execution result to user"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analysis Results',
            'res_model': 'openai.execution.history',
            'res_id': execution.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    @api.model
    def run_scheduled_intelligence(self):
        """Cron method to run scheduled intelligence analysis"""
        current_time = fields.Datetime.now()
        agents_to_run = self.search([
            ('active', '=', True),
            ('execution_mode', '=', 'scheduled'),
            ('next_run', '<=', current_time),
            ('status', '!=', 'running'),
        ])
        
        for agent in agents_to_run:
            try:
                _logger.info("Running scheduled intelligence agent: %s", agent.name)
                agent.with_context(from_cron=True).execute_intelligence_analysis()
            except Exception as e:
                _logger.error("Failed to run scheduled agent %s: %s", agent.name, str(e))