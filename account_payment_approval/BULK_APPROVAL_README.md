# Account Payment Approval - Bulk Operations & Multiple Approvers Feature

## Overview
This module has been enhanced with comprehensive bulk operations and multiple approver support that allow authorized users to process multiple payments at once from the list view.

## New Features

### Multiple Approvers Support
The module now supports both single and multiple approver configurations:

#### Single Approver Mode
- Configure one user who can approve payments
- Backward compatible with existing installations

#### Multiple Approvers Mode  
- Configure multiple users who can approve payments
- Any user from the approved list can approve payments
- Takes precedence over single approver if both are configured
- Useful for teams or departments with multiple authorized personnel

### Bulk Operations Buttons
All buttons are located in the payment list view header:

#### 1. Bulk Approve & Post
- **Function**: Approves and posts multiple selected payments in one action
- **Target**: Payments in "Waiting for Approval" state
- **Access**: Only available to authorized approval users
- **Result**: Payments are approved and automatically posted

#### 2. Bulk Reject
- **Function**: Rejects multiple selected payments
- **Target**: Payments in "Waiting for Approval" state  
- **Access**: Only available to authorized approval users
- **Result**: Payments are set to "Rejected" state and unlocked for editing

#### 3. Bulk Set to Draft
- **Function**: Resets multiple payments back to draft state
- **Target**: Payments in "Rejected" or "Cancelled" state
- **Access**: Available to all users
- **Result**: Payments are reset to "Draft" state and unlocked for editing

#### 4. Bulk Submit for Approval
- **Function**: Submits multiple draft payments for approval workflow
- **Target**: Payments in "Draft" state
- **Access**: Available to all users
- **Result**: Payments exceeding approval threshold are moved to "Waiting for Approval" state

### Key Benefits
1. **Efficiency**: Process multiple payments simultaneously instead of one by one
2. **Complete Workflow Coverage**: Handle approve, reject, draft, and submit operations in bulk
3. **Multiple Approver Support**: Configure multiple users who can approve payments
4. **Flexible Configuration**: Support both single and multiple approver setups
5. **Override Singleton Constraint**: All bulk methods safely handle multiple records
6. **Smart Filtering**: Only processes eligible payments and informs users of filtered selections
7. **Intelligent Submission**: Automatically checks approval thresholds during bulk submit
8. **Error Handling**: Graceful handling of individual payment failures
9. **User Feedback**: Clear notifications about success/failure status

## Configuration

### Setting Up Approvers

1. Navigate to Accounting > Configuration > Settings
2. Scroll to "Payment Approval" section
3. Enable "Payment Approval"
4. Choose your approval setup:

#### For Single Approver:
- Select one user in "Single Approver" field
- Leave "Multiple Approvers" empty

#### For Multiple Approvers:
- Add multiple users in "Multiple Approvers" field using tags
- Single approver will be ignored if multiple approvers are set

5. Set the minimum amount requiring approval
6. Choose the currency for amount comparison
7. Save settings

## How to Use

### Bulk Approve & Post
1. Navigate to Accounting > Payments
2. Filter to show "Waiting for Approval" payments
3. Select multiple payments using checkboxes
4. Click "Bulk Approve & Post" button
5. Confirm the action
6. Review the success notification

### Bulk Reject
1. Navigate to Accounting > Payments
2. Filter to show "Waiting for Approval" payments
3. Select multiple payments to reject
4. Click "Bulk Reject" button
5. Confirm the action
6. Payments will be set to "Rejected" state

### Bulk Set to Draft
1. Navigate to Accounting > Payments
2. Filter to show "Rejected" or "Cancelled" payments
3. Select multiple payments to reset
4. Click "Action" menu > "Bulk Set to Draft"
5. Confirm the action
6. Payments will be reset to "Draft" state

### Bulk Submit for Approval
1. Navigate to Accounting > Payments
2. Filter to show "Draft" payments
3. Select multiple payments to submit
4. Click "Action" menu > "Bulk Submit for Approval"
5. Confirm the action
6. Payments exceeding approval threshold will be moved to "Waiting for Approval"
7. Payments below threshold will be skipped with notification

## Technical Implementation

### Python Model Enhancement
- Added `bulk_approve_payments()` method for bulk approval and posting
- Added `bulk_reject_payments()` method for bulk rejection
- Added `bulk_draft_payments()` method for bulk draft reset
- Added `bulk_submit_for_approval()` method for bulk submission to approval workflow
- Added `_is_user_authorized_approver()` helper method for authorization checks
- Added `get_authorized_approvers()` method to retrieve approver list
- Enhanced `_compute_is_approve_person()` to support multiple approvers
- Added `authorized_approvers_display` field to show approvers on forms
- All methods handle singleton constraint override
- Individual error handling per payment
- Comprehensive logging for all operations
- Smart threshold checking for approval requirements

### Configuration Enhancement
- Added `approval_user_ids` Many2many field for multiple approvers
- Added `get_current_approvers()` method in settings
- Enhanced configuration view with separate single/multiple approver sections
- Backward compatibility with existing single approver setups

### Server Actions Enhancement
- Four server actions for comprehensive bulk operations
- Separate file organization for better maintainability
- Smart filtering and validation for each operation type
- User-friendly notifications and error handling

### View Enhancement
- Extended list view with three header buttons
- Added visual state decorations:
  - Blue: Waiting for Approval
  - Green: Approved/Posted
  - Red: Rejected
  - Gray: Cancelled
- Confirmation dialogs for each bulk operation

### JavaScript Enhancement
- Custom list controller with smart filtering
- Separate handling for each bulk operation type
- Filters selection to only process eligible payments
- User-friendly notifications and warnings

## Error Handling
- If a payment fails during bulk operations, it maintains appropriate state
- Failed payments can be processed individually later
- Detailed error logging for troubleshooting
- User-friendly error messages with operation counts

## Security & Access Control
- Bulk approve and reject: Only authorized approval users (single or multiple)
- Bulk draft: Available to all users (for rejected/cancelled payments)
- Multiple approvers: Any user from the configured list can approve
- Single approver: Only the configured user can approve
- Respects existing approval workflow and amount limits
- Maintains complete audit trail for all actions
- Authorized approvers are displayed on payment forms for transparency

## States and Workflow
The bulk operations respect the existing workflow:

### Bulk Approve & Post
- Source: Waiting for Approval → Approved → Posted
- Automatic posting after approval
- Error handling keeps payments in appropriate recovery state

### Bulk Reject  
- Source: Waiting for Approval → Rejected
- Unlocks payments for editing
- Allows subsequent draft reset

### Bulk Draft
- Source: Rejected or Cancelled → Draft
- Unlocks payments for editing
- Enables workflow restart

### Bulk Submit for Approval
- Source: Draft → Waiting for Approval (if amount exceeds threshold)
- Intelligent threshold checking
- Skips payments below approval amount with notification
- Batch processing for efficient workflow initiation
