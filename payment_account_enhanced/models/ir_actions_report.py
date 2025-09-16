# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import get_lang
import logging
import os
import subprocess

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _prepare_html_url(self, res_ids, report_ref=None):
        """Override to add SSL-safe options for wkhtmltopdf"""
        result = super()._prepare_html_url(res_ids, report_ref)
        return result

    def _get_wkhtmltopdf_command(self, paperformat, landscape, specific_paperformat_args=None, set_viewport_size=False):
        """Override to add SSL-safe options and error handling"""
        command = super()._get_wkhtmltopdf_command(
            paperformat, landscape, specific_paperformat_args, set_viewport_size
        )
        
        # Add SSL-safe options to prevent empty PDF errors
        ssl_safe_options = [
            '--load-error-handling', 'ignore',
            '--load-media-error-handling', 'ignore',
            '--javascript-delay', '1000',
            '--no-stop-slow-scripts',
            '--debug-javascript',
        ]
        
        # Insert SSL-safe options before the output file parameter
        # The command structure is typically: [wkhtmltopdf, options..., input, output]
        if len(command) >= 2:
            # Insert before the last two arguments (input and output)
            insert_position = len(command) - 2
            for i, option in enumerate(ssl_safe_options):
                command.insert(insert_position + i, option)
        
        _logger.info(f"Enhanced wkhtmltopdf command: {' '.join(command)}")
        return command

    def _run_wkhtmltopdf(self, bodies, **kwargs):
        """Override to add environment variables and better error handling"""
        # Set environment variables for Qt/SSL issues
        env = os.environ.copy()
        env.update({
            'QT_QPA_PLATFORM': 'offscreen',
            'QTWEBKIT_DPI': '96',
            'QT_QPA_FONTDIR': '/usr/share/fonts',
        })
        
        try:
            # Try the enhanced command first
            return super()._run_wkhtmltopdf(bodies, **kwargs)
        except Exception as e:
            _logger.warning(f"Enhanced wkhtmltopdf failed: {str(e)}")
            
            # Fallback: Try with minimal options
            try:
                paperformat = kwargs.get('paperformat', False)
                landscape = kwargs.get('landscape', False)
                
                # Get minimal command
                command = [
                    'wkhtmltopdf',
                    '--page-size', paperformat.format if paperformat else 'A4',
                    '--orientation', 'Landscape' if landscape else 'Portrait',
                    '--margin-top', str(paperformat.margin_top) if paperformat else '15',
                    '--margin-bottom', str(paperformat.margin_bottom) if paperformat else '15',
                    '--margin-left', str(paperformat.margin_left) if paperformat else '15',
                    '--margin-right', str(paperformat.margin_right) if paperformat else '15',
                    '--load-error-handling', 'ignore',
                    '--load-media-error-handling', 'ignore',
                    '--quiet',
                    '-',  # input from stdin
                    '-'   # output to stdout
                ]
                
                _logger.info(f"Fallback wkhtmltopdf command: {' '.join(command)}")
                
                # Run with environment variables
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                # Combine all bodies
                combined_body = b''.join(bodies) if isinstance(bodies, list) else bodies
                stdout, stderr = process.communicate(input=combined_body)
                
                if process.returncode != 0:
                    _logger.error(f"wkhtmltopdf error: {stderr.decode()}")
                    raise Exception(f"wkhtmltopdf failed with return code {process.returncode}")
                
                if not stdout:
                    _logger.error("wkhtmltopdf produced empty output")
                    raise Exception("Empty PDF generated")
                
                return stdout
                
            except Exception as fallback_error:
                _logger.error(f"Fallback wkhtmltopdf also failed: {str(fallback_error)}")
                raise Exception(f"PDF generation failed: {str(e)}. Fallback also failed: {str(fallback_error)}")


class IrQWebPdf(models.AbstractModel):
    _inherit = 'ir.qweb.pdf'

    def _get_pdf_html(self, docs, docargs):
        """Override to ensure clean HTML for PDF generation"""
        html = super()._get_pdf_html(docs, docargs)
        
        # Add meta tags for better PDF rendering
        meta_tags = '''
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        '''
        
        # Insert meta tags after <head>
        if '<head>' in html:
            html = html.replace('<head>', f'<head>{meta_tags}')
        elif '<html>' in html:
            html = html.replace('<html>', f'<html><head>{meta_tags}</head>')
        
        return html
