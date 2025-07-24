from odoo import models

class ReportCustomBill(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_bills'
    _description = 'OSUS Custom Bill Report'

    def _get_report_values(self, docids, data=None):
        # Filter to only get active (non-cancelled) account moves
        docs = self.env['account.move'].browse(docids).filtered(lambda m: m.state != 'cancel')
        return {
            'docs': docs,
        }
