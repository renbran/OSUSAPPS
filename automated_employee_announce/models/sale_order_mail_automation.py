from odoo import models, api, fields, _
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super().create(vals)
        return order

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Override to send agent notification after invoice creation.
        """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        for order in self:
            # Check if agent1_partner_id field exists and is populated
            if hasattr(order, 'agent1_partner_id') and order.agent1_partner_id and order.state in ('sale', 'done'):
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_invoiced_agent1', raise_if_not_found=False)
                if template:
                    try:
                        template.send_mail(order.id, force_send=True)
                        order.message_post(body=_("Automated: Invoiced notification email sent to agent1_partner_id."))
                        _logger.info(f"Invoice notification sent for order {order.name}")
                    except Exception as e:
                        _logger.error(f"Failed to send invoice notification for order {order.name}: {str(e)}")
        return invoices

    @api.model
    def send_deal_status_reminders(self):
        """
        Send reminder to agent1_partner_id for deals not invoiced after 30 days from booking_date.
        """
        today = date.today()
        # Build domain dynamically based on available fields
        domain = [
            ('state', 'not in', ['sale', 'done', 'cancel']),
        ]
        
        # Add booking_date filter if field exists
        if 'booking_date' in self._fields:
            domain.append(('booking_date', '!=', False))
        
        # Add agent filter if field exists  
        if 'agent1_partner_id' in self._fields:
            domain.append(('agent1_partner_id', '!=', False))
        
        orders = self.search(domain)
        sent_count = 0
        
        for order in orders:
            booking_date = getattr(order, 'booking_date', False)
            agent = getattr(order, 'agent1_partner_id', False)
            
            if booking_date and agent and (today - booking_date).days >= 30:
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_deal_status_reminder_agent1', raise_if_not_found=False)
                if template:
                    try:
                        template.send_mail(order.id, force_send=True)
                        order.message_post(body=_("Automated: Deal status reminder email sent to agent1_partner_id."))
                        _logger.info(f"Deal reminder sent for order {order.name}")
                        sent_count += 1
                    except Exception as e:
                        _logger.error(f"Failed to send deal reminder for order {order.name}: {str(e)}")
                        
        _logger.info(f"Deal status reminder job completed. Sent {sent_count} emails.")
        return sent_count


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _message_post_after_payment(self, payment, move):
        """Override to send payment notification to agent."""
        # Call super if it exists (Odoo 17+)
        res = super()._message_post_after_payment(payment, move) if hasattr(super(), '_message_post_after_payment') else None
        
        # Automated notification to agent1_partner_id on payment receipt
        if move and move.move_type == 'out_invoice' and move.invoice_origin:
            sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
            agent = getattr(sale_order, 'agent1_partner_id', False) if sale_order else False
            
            if sale_order and agent:
                template = self.env.ref('automated_employee_announce.mail_template_saleorder_payment_initiated_agent1', raise_if_not_found=False)
                if template:
                    try:
                        template.send_mail(sale_order.id, force_send=True)
                        sale_order.message_post(body=_("Automated: Payment receipt notification email sent to agent1_partner_id."))
                        _logger.info(f"Payment notification sent for order {sale_order.name}")
                    except Exception as e:
                        _logger.error(f"Failed to send payment notification for order {sale_order.name}: {str(e)}")
        return res
