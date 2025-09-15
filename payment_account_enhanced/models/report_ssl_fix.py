# -*- coding: utf-8 -*-

from odoo import models, api
import logging
import os
import subprocess

_logger = logging.getLogger(__name__)

class IrActionsReportSSLFix(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
        """
        Override wkhtmltopdf execution to handle SSL issues
        Fixes QSslSocket OpenSSL function resolution errors
        """
        try:
            # Call parent method but catch SSL warnings
            result = super(IrActionsReportSSLFix, self)._run_wkhtmltopdf(
                bodies, header, footer, landscape, specific_paperformat_args, set_viewport_size
            )
            return result
        except Exception as e:
            error_msg = str(e)
            # Check if it's an SSL-related error
            if any(ssl_term in error_msg.lower() for ssl_term in ['qsslsocket', 'crypto_', 'ssl_', 'openssl']):
                _logger.warning("wkhtmltopdf SSL warning suppressed: %s", error_msg)
                # Try alternative PDF generation approach
                return self._run_wkhtmltopdf_with_ssl_disabled(bodies, header, footer, landscape, specific_paperformat_args)
            else:
                # Re-raise non-SSL errors
                raise

    @api.model
    def _run_wkhtmltopdf_with_ssl_disabled(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None):
        """
        Alternative PDF generation with SSL verification disabled
        """
        try:
            # Get the standard command
            command_args = self._prepare_html_report_command(landscape, specific_paperformat_args)
            
            # Add SSL-disabled options
            ssl_disabled_args = [
                '--disable-ssl-verification',
                '--disable-javascript',
                '--no-stop-slow-scripts',
                '--load-error-handling=ignore',
                '--load-media-error-handling=ignore'
            ]
            
            # Insert SSL options after the wkhtmltopdf command
            if command_args and len(command_args) > 0:
                command_args = command_args[:1] + ssl_disabled_args + command_args[1:]
            
            _logger.info("Using SSL-disabled wkhtmltopdf for PDF generation")
            
            # Execute the modified command
            return self._execute_wkhtmltopdf_command(command_args, bodies, header, footer)
            
        except Exception as e:
            _logger.error("PDF generation failed even with SSL disabled: %s", str(e))
            # Return a basic error PDF or re-raise
            raise

    @api.model
    def _prepare_html_report_command(self, landscape=False, specific_paperformat_args=None):
        """
        Prepare base wkhtmltopdf command arguments
        """
        command_args = ['wkhtmltopdf']
        
        # Add basic options
        command_args.extend([
            '--page-size', 'A4',
            '--orientation', 'Landscape' if landscape else 'Portrait',
            '--margin-top', '0.7in',
            '--margin-right', '0.7in',
            '--margin-bottom', '0.7in',
            '--margin-left', '0.7in',
            '--encoding', 'utf-8',
            '--quiet'
        ])
        
        # Add specific paperformat arguments if provided
        if specific_paperformat_args:
            command_args.extend(specific_paperformat_args)
            
        return command_args

    @api.model
    def _execute_wkhtmltopdf_command(self, command_args, bodies, header=None, footer=None):
        """
        Execute wkhtmltopdf command with proper error handling
        """
        try:
            # Add input/output arguments
            command_args.extend(['-', '-'])  # stdin to stdout
            
            # Prepare input HTML
            html_input = '\n'.join(bodies)
            
            # Execute command
            process = subprocess.Popen(
                command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=html_input.encode('utf-8'))
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8')
                # Suppress SSL warnings but log other errors
                if not any(ssl_term in error_msg.lower() for ssl_term in ['qsslsocket', 'crypto_', 'ssl_']):
                    _logger.error("wkhtmltopdf error: %s", error_msg)
                else:
                    _logger.debug("wkhtmltopdf SSL warning suppressed")
            
            return stdout
            
        except Exception as e:
            _logger.error("Failed to execute wkhtmltopdf: %s", str(e))
            raise
