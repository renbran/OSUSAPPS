"""
Configuration script to set up QR code generation properly
"""
import logging

_logger = logging.getLogger(__name__)


def setup_qr_code_configuration(env):
    """Setup QR code configuration for the system"""
    
    # Set the base URL if not already configured
    config_param = env['ir.config_parameter'].sudo()
    
    # Get current base URL
    current_base_url = config_param.get_param('web.base.url')
    
    if not current_base_url or current_base_url == 'http://localhost:8069':
        # You should replace this with your actual domain
        suggested_base_url = 'https://osusbrokers.cloudpepper.site'
        
        _logger.warning(
            f"Base URL not properly configured. Current: {current_base_url}. "
            f"Consider setting it to: {suggested_base_url}"
        )
        
        # Uncomment the following line to automatically set the base URL
        # config_param.set_param('web.base.url', suggested_base_url)
    
    return current_base_url


def test_qr_code_generation(env):
    """Test QR code generation for a sample invoice"""
    
    # Find a sample invoice
    sample_invoice = env['account.move'].search([
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted')
    ], limit=1)
    
    if sample_invoice:
        try:
            # Test QR code generation
            qr_url = sample_invoice.get_qr_code_url()
            _logger.info(f"Sample QR URL for invoice {sample_invoice.name}: {qr_url}")
            
            # Regenerate QR code
            sample_invoice.regenerate_qr_code()
            
            if sample_invoice.qr_image:
                _logger.info(f"QR code successfully generated for invoice {sample_invoice.name}")
            else:
                _logger.error(f"Failed to generate QR code for invoice {sample_invoice.name}")
                
        except Exception as e:
            _logger.error(f"Error testing QR code generation: {str(e)}")
    else:
        _logger.warning("No posted invoices found for testing")


if __name__ == '__main__':
    # This would be run from Odoo shell
    # python -c "exec(open('setup_qr_config.py').read())"
    print("Run this script from Odoo shell to configure QR code generation")
