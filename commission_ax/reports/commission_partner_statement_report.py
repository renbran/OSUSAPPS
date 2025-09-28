# -*- coding: utf-8 -*-

from odoo import models, api


class CommissionPartnerStatementReport(models.AbstractModel):
    _name = 'report.commission_ax.commission_partner_statement_report'
    _description = 'Commission Partner Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Enhanced report values generator for commission partner statement
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        try:
            if not data:
                data = {}
                
            _logger.info(f"Report generation - docids: {docids}, data keys: {list(data.keys())}")
                
            # Get wizard record to access its methods
            wizard_model = self.env['commission.partner.statement.wizard']
            wizard = None
            
            # If docids are provided, use them to get wizard instances
            if docids:
                wizards = wizard_model.browse(docids)
                if wizards.exists():
                    wizard = wizards[0]  # Use first wizard instance
                    _logger.info(f"Found wizard: {wizard.id}, date_from: {wizard.date_from}, date_to: {wizard.date_to}")
                    
                    # Get commission data using wizard method
                    report_data = wizard._get_commission_data()
                    _logger.info(f"Wizard returned {len(report_data)} records")
                    
                    # Prepare the data structure for the template
                    report_context = {
                        'report_data': report_data,
                        'date_from': wizard.date_from.strftime('%d/%m/%Y') if wizard.date_from else '',
                        'date_to': wizard.date_to.strftime('%d/%m/%Y') if wizard.date_to else '',
                        'commission_state': wizard.commission_state,
                        'partner_names': ', '.join(wizard.partner_ids.mapped('name')) if wizard.partner_ids else 'All Partners',
                        'project_names': 'All Projects',  # Project module not available
                        'error_message': None if report_data else 'No commission data found for selected criteria'
                    }
                else:
                    _logger.warning("No wizard found for docids")
                    # No wizard found, create sample data for testing
                    report_context = self._get_sample_report_data()
            else:
                _logger.info("No docids provided, using data parameter")
                # Use data passed from wizard action or create sample data
                report_context = data if data.get('report_data') else self._get_sample_report_data()
                
            _logger.info(f"Final report context has {len(report_context.get('report_data', []))} records")
            
            return {
                'doc_ids': docids or [],
                'doc_model': 'commission.partner.statement.wizard',
                'docs': self.env['commission.partner.statement.wizard'].browse(docids) if docids else [wizard] if wizard else [],
                'data': report_context,
            }
            
        except Exception as e:
            # Log error and return safe fallback data
            _logger.error(f"Error generating commission partner statement report: {str(e)}")
            
            return {
                'doc_ids': docids or [],
                'doc_model': 'commission.partner.statement.wizard',
                'docs': self.env['commission.partner.statement.wizard'].browse(docids) if docids else [],
                'data': self._get_sample_report_data(error_msg=str(e)),
            }
    
    def _get_sample_report_data(self, error_msg=None):
        """Get sample data for testing PDF generation"""
        from datetime import date
        
        return {
            'report_data': [
                {
                    'partner_name': 'Sample Commission Agent',
                    'booking_date': date.today(),
                    'client_order_ref': 'CLIENT-ORDER-2025-001',
                    'sale_value': 10000.00,
                    'commission_rate': 5.0,
                    'calculation_method': 'percentage_total',
                    'commission_amount': 500.00,
                    'commission_status': 'Confirmed',
                    'sale_order_name': 'SO2025-001',
                    'currency': 'USD',
                },
                {
                    'partner_name': 'Another Commission Agent',
                    'booking_date': date.today(),
                    'client_order_ref': 'CLIENT-ORDER-2025-002',
                    'sale_value': 15000.00,
                    'commission_rate': 3.0,
                    'calculation_method': 'percentage_total',
                    'commission_amount': 450.00,
                    'commission_status': 'Processed',
                    'sale_order_name': 'SO2025-002',
                    'currency': 'USD',
                }
            ],
            'date_from': date.today().strftime('%d/%m/%Y'),
            'date_to': date.today().strftime('%d/%m/%Y'),
            'commission_state': 'all',
            'partner_names': 'Sample Partners',
            'project_names': 'All Projects',
            'error_message': f'Sample data shown. Error: {error_msg}' if error_msg else 'Sample data - configure commission lines for real data'
        }