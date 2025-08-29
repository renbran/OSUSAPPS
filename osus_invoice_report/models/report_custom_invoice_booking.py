from odoo import models, api

class ReportCustomInvoiceBooking(models.AbstractModel):
    _inherit = 'report.osus_invoice_report.report_invoice'

    def _get_report_values(self, docids, data=None):
        # Get booking_date filter from context or data
        booking_date = False
        if data and 'booking_date' in data:
            booking_date = data['booking_date']
        elif self.env.context.get('booking_date'):
            booking_date = self.env.context['booking_date']

        docs = self.env['account.move'].browse(docids).filtered(lambda m: m.state != 'cancel')
        if booking_date:
            docs = docs.filtered(lambda m: m.booking_date == booking_date)

        # Group by booking_date
        grouped = {}
        for doc in docs:
            key = doc.booking_date or 'No Date'
            grouped.setdefault(key, []).append(doc)

        return {
            'docs': docs,
            'grouped_by_booking_date': grouped,
            'booking_date': booking_date,
        }
