# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ScholarixCommissionStatement(models.Model):
    """SCHOLARIX Commission Statement Model for consolidated reporting"""
    _name = "scholarix.commission.statement"
    _description = "SCHOLARIX Commission Statement"
    _order = "period_start desc, agent_id"
    _rec_name = "display_name"

    # Core identification fields
    display_name = fields.Char(
        string="Statement Name",
        compute="_compute_display_name",
        store=True
    )
    
    # Period and agent information
    agent_id = fields.Many2one(
        "res.partner",
        string="Agent",
        required=True,
        domain=[("is_company", "=", False)],
        help="Commission agent/partner"
    )
    period_start = fields.Date(
        string="Period Start",
        required=True,
        help="Start date for commission period"
    )
    period_end = fields.Date(
        string="Period End", 
        required=True,
        help="End date for commission period"
    )
    
    # Commission calculation fields
    total_sales = fields.Monetary(
        string="Total Sales",
        help="Total sales amount for the period"
    )
    commission_rate = fields.Float(
        string="Commission Rate (%)",
        help="Commission rate percentage"
    )
    gross_commission = fields.Monetary(
        string="Gross Commission",
        help="Commission before deductions"
    )
    deductions = fields.Monetary(
        string="Deductions",
        help="Total deductions from commission"
    )
    net_commission = fields.Monetary(
        string="Net Commission",
        compute="_compute_net_commission",
        store=True,
        help="Final commission after deductions"
    )
    
    # SCHOLARIX specific fields
    direct_sales_commission = fields.Monetary(
        string="Direct Sales Commission",
        help="Commission from direct sales"
    )
    referral_bonus = fields.Monetary(
        string="Referral Bonus",
        help="Bonus from referrals"
    )
    team_override = fields.Monetary(
        string="Team Override",
        help="Team override commission"
    )
    
    # Status fields
    payment_status = fields.Selection([
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("partial", "Partially Paid"),
        ("cancelled", "Cancelled")
    ], string="Payment Status", default="pending")
    
    statement_status = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("approved", "Approved"),
        ("paid", "Paid")
    ], string="Statement Status", default="draft")
    
    # System fields
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        help="Currency for commission calculations"
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        help="Company"
    )
    
    # Related fields for convenience
    commission_line_ids = fields.One2many(
        "scholarix.commission.line",
        "statement_id",
        string="Commission Lines"
    )
    order_count = fields.Integer(
        string="Order Count",
        compute="_compute_order_count"
    )
    
    # Contact information
    agent_email = fields.Char(
        related="agent_id.email",
        string="Agent Email",
        readonly=True
    )
    agent_phone = fields.Char(
        related="agent_id.phone",
        string="Agent Phone",
        readonly=True
    )

    @api.depends("agent_id", "period_start", "period_end")
    def _compute_display_name(self):
        """Compute display name for the statement"""
        for record in self:
            if record.agent_id and record.period_start and record.period_end:
                record.display_name = f"{record.agent_id.name} - {record.period_start.strftime('%b %Y')}"
            else:
                record.display_name = "New Statement"

    @api.depends("gross_commission", "deductions")
    def _compute_net_commission(self):
        """Compute net commission after deductions"""
        for record in self:
            record.net_commission = record.gross_commission - record.deductions

    @api.depends("commission_line_ids")
    def _compute_order_count(self):
        """Compute number of orders in this statement"""
        for record in self:
            record.order_count = len(record.commission_line_ids)

    def generate_commission_data(self):
        """Generate commission data for the period"""
        self.ensure_one()
        
        # Get commission data from the partner
        commission_data = self.agent_id.commission_statement_query(
            self.period_start, 
            self.period_end
        )
        
        # Update totals
        self.total_sales = sum(line.get("order_total", 0) for line in commission_data["statement_lines"])
        self.gross_commission = commission_data["total_amount"]
        
        # Create commission lines
        self.commission_line_ids.unlink()  # Clear existing lines
        
        for line_data in commission_data["statement_lines"]:
            self.env["scholarix.commission.line"].create({
                "statement_id": self.id,
                "order_ref": line_data["order_ref"],
                "order_date": line_data["order_date"],
                "customer_name": line_data["customer_name"],
                "commission_type": line_data["commission_type"],
                "commission_category": line_data["commission_category"],
                "rate": line_data["rate"],
                "amount": line_data["amount"],
                "order_total": line_data["order_total"],
            })

    def action_confirm_statement(self):
        """Confirm the commission statement"""
        self.statement_status = "confirmed"

    def action_approve_statement(self):
        """Approve the commission statement"""
        self.statement_status = "approved"

    def action_mark_paid(self):
        """Mark statement as paid"""
        self.statement_status = "paid"
        self.payment_status = "paid"


class ScholarixCommissionLine(models.Model):
    """SCHOLARIX Commission Line Model"""
    _name = "scholarix.commission.line"
    _description = "SCHOLARIX Commission Line"
    _order = "order_date desc"

    statement_id = fields.Many2one(
        "scholarix.commission.statement",
        string="Statement",
        required=True,
        ondelete="cascade"
    )
    order_ref = fields.Char(
        string="Order Reference",
        help="Sale order reference"
    )
    order_date = fields.Date(
        string="Order Date",
        help="Date of the sale order"
    )
    customer_name = fields.Char(
        string="Customer",
        help="Customer name"
    )
    commission_type = fields.Char(
        string="Commission Type",
        help="Type of commission (Internal/External/Legacy)"
    )
    commission_category = fields.Char(
        string="Category",
        help="Commission category (Agent, Manager, etc.)"
    )
    rate = fields.Float(
        string="Rate (%)",
        help="Commission rate percentage"
    )
    amount = fields.Monetary(
        string="Commission Amount",
        help="Commission amount for this line"
    )
    order_total = fields.Monetary(
        string="Order Total",
        help="Total amount of the sale order"
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="statement_id.currency_id",
        readonly=True
    )
