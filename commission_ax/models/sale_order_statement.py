from odoo import models, fields, api


class SaleOrderStatement(models.Model):
    """Extend Sale Order with Commission Statement functionality."""
    
    _inherit = 'sale.order'
    
    commission_statement_count = fields.Integer(
        string='Commission Statement Count',
        compute='_compute_commission_statement_count',
        help="Number of commission partners eligible for statements"
    )
    
    @api.depends('agent1_partner_id', 'agent2_partner_id', 'broker_partner_id', 
                 'referrer_partner_id', 'cashback_partner_id', 'other_external_partner_id',
                 'consultant_id', 'manager_id', 'second_agent_id', 'director_id',
                 'manager_partner_id', 'director_partner_id')
    def _compute_commission_statement_count(self):
        """Compute number of commission partners for this order."""
        for order in self:
            partners = set()
            
            # Collect all commission partners
            commission_partners = [
                order.agent1_partner_id,
                order.agent2_partner_id,
                order.broker_partner_id,
                order.referrer_partner_id,
                order.cashback_partner_id,
                order.other_external_partner_id,
                order.consultant_id,
                order.manager_id,
                order.second_agent_id,
                order.director_id,
                order.manager_partner_id,
                order.director_partner_id,
            ]
            
            for partner in commission_partners:
                if partner:
                    partners.add(partner.id)
            
            order.commission_statement_count = len(partners)
    
    def action_view_commission_statement(self):
        """Open commission statement wizard for this order."""
        self.ensure_one()
        
        # Check if user has access rights
        if not self.env.user.has_group('base.group_user'):
            from odoo.exceptions import AccessError
            raise AccessError("You don't have permission to view commission statements.")
        
        # Get all commission partners for this order
        commission_partners = self._get_commission_partners()
        
        if not commission_partners:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Commission Partners',
                    'message': 'This sale order has no commission partners defined.',
                    'type': 'warning',
                }
            }
        
        # If only one partner, pre-select them
        context = {
            'default_sale_order_id': self.id,
            'default_date_from': self.date_order.date() if self.date_order else fields.Date.today(),
            'default_date_to': fields.Date.today(),
        }
        
        if len(commission_partners) == 1:
            context['default_partner_id'] = commission_partners[0].id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Statement',
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
    
    def _get_commission_partners(self):
        """Get all partners with commissions on this order."""
        partners = []
        
        commission_partner_fields = [
            'agent1_partner_id',
            'agent2_partner_id', 
            'broker_partner_id',
            'referrer_partner_id',
            'cashback_partner_id',
            'other_external_partner_id',
            'consultant_id',
            'manager_id',
            'second_agent_id',
            'director_id',
            'manager_partner_id',
            'director_partner_id',
        ]
        
        for field_name in commission_partner_fields:
            if hasattr(self, field_name):
                partner = getattr(self, field_name)
                if partner and partner not in partners:
                    partners.append(partner)
        
        return partners
    
    def get_commission_statement_data(self, partner_id):
        """Get commission statement data for a specific partner."""
        self.ensure_one()
        
        if not partner_id:
            return []
        
        partner = self.env['res.partner'].browse(partner_id)
        data = []
        
        # Map of partner fields to commission data
        commission_mappings = [
            ('agent1_partner_id', 'agent1_amount', 'agent1_rate', 'Internal - Agent 1'),
            ('agent2_partner_id', 'agent2_amount', 'agent2_rate', 'Internal - Agent 2'),
            ('broker_partner_id', 'broker_amount', 'broker_rate', 'External - Broker'),
            ('referrer_partner_id', 'referrer_amount', 'referrer_rate', 'External - Referrer'),
            ('cashback_partner_id', 'cashback_amount', 'cashback_rate', 'External - Cashback'),
            ('other_external_partner_id', 'other_external_amount', 'other_external_rate', 'External - Other'),
            ('consultant_id', 'salesperson_commission', 'consultant_comm_percentage', 'Legacy - Consultant'),
            ('manager_id', 'manager_commission', 'manager_comm_percentage', 'Legacy - Manager'),
            ('second_agent_id', 'second_agent_commission', 'second_agent_comm_percentage', 'Legacy - Second Agent'),
            ('director_id', 'director_commission', 'director_comm_percentage', 'Legacy - Director'),
            ('manager_partner_id', 'manager_amount', 'manager_rate', 'Internal - Manager'),
            ('director_partner_id', 'director_amount', 'director_rate', 'Internal - Director'),
        ]
        
        for partner_field, amount_field, rate_field, commission_type in commission_mappings:
            if (hasattr(self, partner_field) and 
                getattr(self, partner_field) == partner and
                hasattr(self, amount_field) and
                getattr(self, amount_field, 0) > 0):
                
                # Find related purchase order
                po = self.env['purchase.order'].search([
                    ('origin_so_id', '=', self.id),
                    ('partner_id', '=', partner.id),
                ], limit=1)
                
                # Calculate VAT (default 5% for UAE)
                gross_amount = getattr(self, amount_field, 0)
                vat_rate = 5.0  # Can be made configurable
                vat_amount = gross_amount * vat_rate / 100
                net_amount = gross_amount - vat_amount
                
                # Determine status
                status = 'Draft'
                if self.commission_processed:
                    status = 'Confirmed'
                elif self.commission_status == 'calculated':
                    status = 'Calculated'
                
                # Determine remarks
                remarks = []
                if po:
                    if po.commission_posted:
                        remarks.append('Posted')
                    if po.state == 'purchase':
                        remarks.append('Confirmed')
                    elif po.state == 'done':
                        remarks.append('Received')
                    elif po.state == 'cancel':
                        remarks.append('Cancelled')
                else:
                    remarks.append('No PO Created')
                
                if self.invoice_status == 'invoiced':
                    remarks.append('Invoiced')
                
                data.append({
                    'agent_name': partner.name,
                    'deal_date': self.date_order.date() if self.date_order else fields.Date.today(),
                    'commission_type': commission_type,
                    'rate': getattr(self, rate_field, 0),
                    'property_price': self.amount_total,
                    'gross_commission': gross_amount,
                    'vat_rate': vat_rate,
                    'vat_amount': vat_amount,
                    'net_commission': net_amount,
                    'status': status,
                    'po_number': po.name if po else '',
                    'remarks': ', '.join(remarks) if remarks else 'Pending',
                    'currency_id': self.currency_id.id,
                })
        
        return data