from odoo import http
from odoo.http import request

class OsusMainController(http.Controller):
    @http.route('/osus/hello', type='http', auth='user', csrf=True)
    def hello(self, **kw):
        return request.render('osus_enterprise_module.hello_template', {})
