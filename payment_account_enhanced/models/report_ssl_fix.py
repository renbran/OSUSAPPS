# -*- coding: utf-8 -*-

from odoo import models, api, tools
import logging
import os

_logger = logging.getLogger(__name__)

class IrActionsReportSSLFix(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _build_wkhtmltopdf_args(self, paperformat, landscape, specific_paperformat_args=None, set_viewport_size=False):
        """
        Override to add SSL-disabled arguments to wkhtmltopdf command
        This is the most reliable way to fix SSL issues in Odoo 17
        """
        # Get the standard arguments first
        command_args = super()._build_wkhtmltopdf_args(
            paperformat, landscape, specific_paperformat_args, set_viewport_size
        )
        
        # Add SSL-disabled options to prevent QSslSocket errors
        ssl_fix_args = [
            '--disable-ssl-verification',
            '--disable-javascript',
            '--no-stop-slow-scripts',
            '--load-error-handling=ignore',
            '--load-media-error-handling=ignore',
            '--disable-smart-shrinking'
        ]
        
        # Insert SSL fix arguments after wkhtmltopdf but before other options
        if command_args and len(command_args) > 1:
            # Find where to insert (after 'wkhtmltopdf' command)
            insert_pos = 1
            command_args = command_args[:insert_pos] + ssl_fix_args + command_args[insert_pos:]
            
        _logger.debug("Applied SSL fix to wkhtmltopdf command")
        return command_args

    @api.model  
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
        """
        Override to set SSL-safe environment before running wkhtmltopdf
        """
        # Set environment variables for SSL compatibility
        old_env = os.environ.copy()
        try:
            # Set SSL-safe environment
            os.environ.update({
                'QTWEBKIT_DPI': '96',
                'QT_QPA_PLATFORM': 'offscreen',
                'OPENSSL_CONF': '',  # Disable OpenSSL config to avoid conflicts
            })
            
            # Call parent method with SSL-safe environment
            return super()._run_wkhtmltopdf(
                bodies, header, footer, landscape, specific_paperformat_args, set_viewport_size
            )
        except Exception as e:
            error_msg = str(e)
            # Log SSL warnings as debug instead of warnings to reduce noise
            if any(ssl_term in error_msg.lower() for ssl_term in ['qsslsocket', 'crypto_', 'ssl_', 'openssl']):
                _logger.debug("wkhtmltopdf SSL warning suppressed: %s", error_msg)
                # Try one more time with minimal environment
                try:
                    os.environ.clear()
                    os.environ.update({
                        'PATH': old_env.get('PATH', ''),
                        'HOME': old_env.get('HOME', '/tmp'),
                        'QT_QPA_PLATFORM': 'offscreen'
                    })
                    return super()._run_wkhtmltopdf(
                        bodies, header, footer, landscape, specific_paperformat_args, set_viewport_size
                    )
                except:
                    pass
            raise
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(old_env)
