# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class NewAppController(http.Controller):

    @http.route('/new_app/hello', type='http', auth='public', website=True)
    def hello_world(self, **kwargs):
        return "Hello from New App!"

    @http.route('/new_app/data', type='json', auth='user')
    def get_data(self, **kwargs):
        records = request.env['new.app.model'].search([])
        return {
            'success': True,
            'data': [{
                'id': rec.id,
                'name': rec.name,
                'state': rec.state,
            } for rec in records]
        }
