# -*- coding: utf-8 -*-

from odoo import models, api


class CommissionPartnerStatementReport(models.AbstractModel):
    _name = 'report.commission_ax.commission_partner_statement_report'
    _description = 'Commission Partner Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Generate report values for commission partner statement
        """
        try:
            if not data:
                data = {}
                
            # Get wizard record to access its methods
            wizard_model = self.env['commission.partner.statement.wizard']
            
            # If docids are provided, use them to get wizard instances
            if docids:
                wizards = wizard_model.browse(docids)
                if wizards:
                    wizard = wizards[0]  # Use first wizard instance
                    
                    # Get commission data using wizard method
                    report_data = wizard._get_commission_data()
                    
                    # Prepare the data structure for the template
                    report_context = {
                        'report_data': report_data,
                        'date_from': wizard.date_from.strftime('%d/%m/%Y') if wizard.date_from else '',
                        'date_to': wizard.date_to.strftime('%d/%m/%Y') if wizard.date_to else '',
                        'commission_state': wizard.commission_state,
                        'partner_names': ', '.join(wizard.partner_ids.mapped('name')) if wizard.partner_ids else 'All Partners',
                        'project_names': 'All Projects'  # Project module not available
                    }
                else:
                    # No wizard found, return empty data
                    report_context = {
                        'report_data': [],
                        'date_from': '',
                        'date_to': '',
                        'commission_state': 'all',
                        'partner_names': 'All Partners',
                        'project_names': 'All Projects'
                    }
            else:
                # Use data passed from wizard action
                report_context = data
                
            return {
                'doc_ids': docids,
                'doc_model': 'commission.partner.statement.wizard',
                'docs': self.env['commission.partner.statement.wizard'].browse(docids) if docids else [],
                'data': report_context,
            }
        except Exception as e:
            # Log error and return safe fallback data
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error generating commission partner statement report: {str(e)}")
            
            return {
                'doc_ids': docids or [],
                'doc_model': 'commission.partner.statement.wizard',
                'docs': self.env['commission.partner.statement.wizard'].browse(docids) if docids else [],
                'data': {
                    'report_data': [],
                    'date_from': '',
                    'date_to': '',
                    'commission_state': 'all',
                    'partner_names': 'All Partners',
                    'project_names': 'All Projects',
                    'error_message': f'Report generation failed: {str(e)}'
                },
            }