from odoo import http
from odoo.http import request

class EliteDashboard(http.Controller):
    @http.route('/elite_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, agent_type='internal'):
        return request.env['elite.agent.dashboard'].get_dashboard_data(agent_type)
        
    @http.route('/elite_dashboard/settings', type='json', auth='user')
    def get_dashboard_settings(self):
        return request.env['elite.dashboard.settings'].get_settings()