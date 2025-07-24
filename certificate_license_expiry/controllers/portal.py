# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError

class CertificatePortal(CustomerPortal):

    @http.route(['/certificate/upload/<int:certificate_id>/<access_token>'], type='http', auth='public', website=True)
    def certificate_upload_documents(self, certificate_id, access_token, **kw):
        """Certificate document upload portal page"""
        try:
            certificate_sudo = self._document_check_access('certificates', certificate_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = self._certificate_get_page_view_values(certificate_sudo, access_token, **kw)
        return request.render("certificate_license_expiry.portal_certificate_upload", values)
    
    @http.route(['/certificate/upload/submit/<int:certificate_id>/<access_token>'], type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def certificate_upload_submit(self, certificate_id, access_token, **kw):
        """Process certificate document upload"""
        try:
            certificate_sudo = self._document_check_access('certificates', certificate_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        # Process uploaded files
        update_vals = {}
        upload_status = {}
        
        # Developer Doc 1
        if 'developer_doc1' in request.httprequest.files:
            file = request.httprequest.files['developer_doc1']
            if file:
                update_vals['developer_document1'] = file.read()
                update_vals['developer_document1_filename'] = file.filename
                update_vals['developer_doc1_uploaded'] = True
                upload_status['developer_doc1'] = True
        
        # Developer Doc 2
        if 'developer_doc2' in request.httprequest.files:
            file = request.httprequest.files['developer_doc2']
            if file:
                update_vals['developer_document2'] = file.read()
                update_vals['developer_document2_filename'] = file.filename
                update_vals['developer_doc2_uploaded'] = True
                upload_status['developer_doc2'] = True
        
        # Signed Doc 1
        if 'signed_doc1' in request.httprequest.files:
            file = request.httprequest.files['signed_doc1']
            if file:
                update_vals['signed_document1'] = file.read()
                update_vals['signed_document1_filename'] = file.filename
                update_vals['signed_doc1_uploaded'] = True
                upload_status['signed_doc1'] = True
        
        # Signed Doc 2
        if 'signed_doc2' in request.httprequest.files:
            file = request.httprequest.files['signed_doc2']
            if file:
                update_vals['signed_document2'] = file.read()
                update_vals['signed_document2_filename'] = file.filename
                update_vals['signed_doc2_uploaded'] = True
                upload_status['signed_doc2'] = True
        
        # Update certificate
        if update_vals:
            certificate_sudo.write(update_vals)
            
            # Send notification to certificate owner
            certificate_sudo.message_post(
                body=_("Documents uploaded by %s") % certificate_sudo.customer_id.name,
                subtype_xmlid="mail.mt_note"
            )
        
        values = self._certificate_get_page_view_values(certificate_sudo, access_token, **kw)
        values.update({
            'upload_status': upload_status,
            'upload_success': bool(upload_status)
        })
        return request.render("certificate_license_expiry.portal_certificate_upload_result", values)
    
    def _document_check_access(self, model_name, document_id, access_token=None):
        """Check access to the document for the current user"""
        document = request.env[model_name].sudo().browse(document_id)
        if not document.exists():
            raise MissingError(_("This document does not exist."))
            
        if access_token:
            if not document.access_token or access_token != document.access_token:
                raise AccessError(_("Invalid access token"))
            return document
        else:
            return self._document_check_access_rights(model_name, document.id)
    
    def _certificate_get_page_view_values(self, certificate, access_token, **kwargs):
        """Values for rendering the certificate upload templates"""
        return {
            'certificate': certificate,
            'access_token': access_token,
            'page_name': 'certificate_upload',
            'bootstrap_formatting': True,
        }