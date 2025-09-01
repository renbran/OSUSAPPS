from odoo import models, api

class DashboardInvoiceBooking(models.Model):
    _inherit = 'account.move'

    def get_dashboard_booking_group(self, booking_date=None):
        # Optionally filter by booking_date
        moves = self.search([('state', '!=', 'cancel')])
        if booking_date:
            moves = moves.filtered(lambda m: m.booking_date == booking_date)
        # Group by booking_date
        grouped = {}
        for move in moves:
            key = move.booking_date or 'No Date'
            grouped.setdefault(key, []).append(move)
        return grouped
