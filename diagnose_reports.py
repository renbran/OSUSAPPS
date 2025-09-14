#!/usr/bin/env python3
"""
Comprehensive Odoo Report Generation Diagnostic Script
"""

def test_report_generation():
    """Test and diagnose report generation issues"""
    
    print("=" * 60)
    print("🔍 ODOO REPORT GENERATION DIAGNOSTIC")
    print("=" * 60)
    
    try:
        # 1. Check report infrastructure
        print("\n1. REPORT INFRASTRUCTURE CHECK")
        print("-" * 40)
        
        # Check report models
        report_model = env['ir.actions.report']
        all_reports = report_model.search([])
        print(f"✅ Total reports registered: {len(all_reports)}")
        
        # Check payment reports specifically
        payment_reports = report_model.search([('model', '=', 'account.payment')])
        print(f"📊 Payment reports found: {len(payment_reports)}")
        
        for report in payment_reports:
            print(f"  - ID: {report.id}")
            print(f"    Name: {report.name}")
            print(f"    Report Name: {report.report_name}")
            print(f"    Report Type: {report.report_type}")
            print(f"    Binding Type: {report.binding_type}")
            print()
        
        # 2. Check template availability
        print("2. TEMPLATE AVAILABILITY CHECK")
        print("-" * 40)
        
        template_model = env['ir.ui.view']
        
        # Check our payment templates
        templates = template_model.search([
            ('name', 'ilike', 'payment'),
            ('type', '=', 'qweb')
        ])
        
        print(f"✅ Payment-related templates: {len(templates)}")
        for template in templates:
            print(f"  - {template.name}: {template.key}")
        
        # Check specific templates
        our_templates = template_model.search([
            ('key', 'like', 'payment_account_enhanced%')
        ])
        print(f"✅ Our module templates: {len(our_templates)}")
        for template in our_templates:
            print(f"  - {template.name}: {template.key}")
            if template.arch_db:
                print(f"    Template size: {len(template.arch_db)} characters")
            else:
                print("    ❌ Template has no content!")
        
        # 3. Test report generation
        print("\n3. REPORT GENERATION TEST")
        print("-" * 40)
        
        # Find a test payment
        payments = env['account.payment'].search([], limit=1)
        if payments:
            payment = payments[0]
            print(f"✅ Test payment found: {payment.name} (ID: {payment.id})")
            
            # Try to generate our payment voucher report
            if payment_reports:
                for report in payment_reports:
                    print(f"\n🧪 Testing report: {report.name}")
                    try:
                        # Get the report data
                        report_data = report._render_qweb_pdf([payment.id])
                        if report_data and len(report_data[0]) > 0:
                            print(f"✅ Report generated successfully: {len(report_data[0])} bytes")
                        else:
                            print("❌ Report generated but empty")
                    except Exception as e:
                        print(f"❌ Report generation failed: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                print("❌ No payment reports to test")
        else:
            print("⚠️  No test payments found")
        
        # 4. Check wkhtmltopdf integration
        print("\n4. WKHTMLTOPDF INTEGRATION CHECK")
        print("-" * 40)
        
        try:
            import subprocess
            result = subprocess.run(['wkhtmltopdf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ wkhtmltopdf version: {result.stdout.strip()}")
            else:
                print(f"❌ wkhtmltopdf error: {result.stderr}")
        except Exception as e:
            print(f"❌ wkhtmltopdf check failed: {e}")
        
        # 5. Check for common issues
        print("\n5. COMMON ISSUES CHECK")
        print("-" * 40)
        
        # Check if base report templates are available
        base_templates = template_model.search([('key', '=', 'web.html_container')])
        if base_templates:
            print("✅ Base report templates available")
        else:
            print("❌ Base report templates missing!")
        
        external_layout = template_model.search([('key', '=', 'web.external_layout')])
        if external_layout:
            print("✅ External layout template available")
        else:
            print("❌ External layout template missing!")
        
        # Check report permissions
        user = env.user
        print(f"✅ Current user: {user.name} (ID: {user.id})")
        print(f"✅ User groups: {[g.name for g in user.groups_id]}")
        
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSTIC COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ DIAGNOSTIC FAILED: {e}")
        import traceback
        traceback.print_exc()

def check_report_assets():
    """Check if CSS assets are properly loaded for reports"""
    
    print("\n📄 REPORT ASSETS CHECK")
    print("-" * 40)
    
    try:
        # Check if our CSS is loaded in assets
        asset_model = env['ir.asset']
        assets = asset_model.search([('path', 'like', 'payment_account_enhanced%')])
        
        print(f"✅ Found {len(assets)} asset entries for our module")
        for asset in assets:
            print(f"  - Bundle: {asset.bundle}")
            print(f"    Path: {asset.path}")
            print(f"    Active: {asset.active}")
        
        # Check CSS content
        import os
        css_path = "/mnt/extra-addons/payment_account_enhanced/static/src/css/payment_enhanced.css"
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css_content = f.read()
            print(f"✅ CSS file exists: {len(css_content)} characters")
            
            # Check for report-specific styles
            if "payment_voucher" in css_content:
                print("✅ Payment voucher styles found in CSS")
            else:
                print("⚠️  Payment voucher styles may be missing")
        else:
            print("❌ CSS file not found!")
            
    except Exception as e:
        print(f"❌ Asset check failed: {e}")

if __name__ == "__main__":
    test_report_generation()
    check_report_assets()