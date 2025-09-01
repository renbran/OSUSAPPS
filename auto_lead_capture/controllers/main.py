from odoo import http
from odoo.http import request

class AutoLeadCaptureController(http.Controller):
    @http.route('/auto_lead_capture/submit', type='json', auth='public', csrf=True)
    def submit_lead(self, **kwargs):
        # Example: capture lead from web form
        name = kwargs.get('name')
        source = kwargs.get('source', 'web')
        lead = request.env['auto.lead.capture'].sudo().create({
            'name': name,
            'source': source,
        })
        return {'success': True, 'lead_id': lead.id}
