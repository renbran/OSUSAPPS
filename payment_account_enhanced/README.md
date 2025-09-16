# Payment Account Enhanced

## Overview

The Payment Account Enhanced module provides a comprehensive payment management system for Odoo 17 with advanced features including a 4-stage approval workflow, QR code verification, professional payment vouchers, and an audit trail for payment processes.

## Key Features

- **4-Stage Approval Workflow**: Draft → Review → Approval → Authorization → Posted
- **QR Code Verification**: Generate and verify payment vouchers with secure QR codes
- **Professional Voucher Templates**: Customizable payment and receipt templates
- **Email Notifications**: Automated notifications for each workflow stage
- **Dashboard**: Real-time approval status tracking
- **Audit Trail**: Complete history of payment approvals and changes
- **Security**: Role-based access control for each approval stage

## Module Structure

### Core Models

- **account_payment.py**: Extends account.payment with approval workflow, QR codes, and verification
- **payment_approval_history.py**: Records all approval actions for audit purposes
- **payment_qr_verification.py**: Manages QR code verification logs and security
- **payment_workflow_stage.py**: Configurable workflow stages and transition rules
- **payment_reminder.py**: Automatic reminders for pending approvals
- **payment_dashboard.py**: Real-time dashboard for monitoring approval processes

### Email Templates

- **mail_template_data.xml**: Contains all email templates for:
  - Payment submission notifications
  - Review requests
  - Approval requests
  - Authorization requests
  - Approval/rejection notifications
  - Posting confirmations
  - Reminder emails
  - Escalation emails

### Reports

- **payment_voucher_report.xml**: Professional payment voucher with QR code

### Security

- **payment_security.xml**: Custom security groups and access rules
- **ir.model.access.csv**: Model access control for all payment models

## Workflow Integration

The Payment Account Enhanced module integrates several components:

1. **Core Payment Process**:
   - Main functionality in account_payment.py
   - Handles state transitions, validation, and business logic

2. **Approval Tracking**:
   - payment_approval_history.py records all approval actions
   - Maintains complete audit trail

3. **QR Verification System**:
   - QR codes generated in account_payment.py
   - Verification handled by controllers/main.py and payment_qr_verification.py
   - Public access verification portal in website_verification_templates.xml

4. **Email Notification System**:
   - Templates defined in mail_template_data.xml
   - Email sending managed by _send_workflow_email in account_payment.py
   - Used by both workflow transitions and automatic reminders

5. **Reminder System**:
   - Implemented in payment_reminder.py
   - Uses cron jobs defined in cron_data.xml
   - Leverages core email functionality from account_payment.py

## Dependencies Between Components

- payment_reminder.py uses the \_send\_workflow\_email method from account_payment.py
- account_payment.py uses mail templates defined in mail_template_data.xml
- payment_approval_history.py is updated by state change methods in account_payment.py
- website_verification_templates.xml displays data from payment_qr_verification.py

## Configuration

The module can be configured at both company and user levels:

1. **Company Settings**:
   - QR code verification URL
   - Default approval thresholds
   - Email notification preferences

2. **User Permissions**:
   - Reviewer role (account.group_account_manager)
   - Approver role (payment_account_enhanced.group_payment_approver)
   - Authorizer role (payment_account_enhanced.group_payment_authorizer)

## Maintenance Notes

- When extending functionality, follow the existing pattern of extending account.payment
- Consider consolidating extensions to keep related functionality together
- Document dependencies between components in docstrings
- Avoid duplicating models across multiple files
