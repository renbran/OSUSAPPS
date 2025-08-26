<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- Enhanced Invoice/Bill Form View with Approval Workflow -->
        <record id="view_move_form_enhanced" model="ir.ui.view">
            <field name="name">account.move.form.enhanced</field>
            <field name="model">account.move</field>
            <field name="inherit_id" ref="account.view_move_form"/>
            <field name="arch" type="xml">

                <!-- Add approval workflow statusbar -->
                <xpath expr="//header" position="inside">
                    <!-- Approval Workflow Statusbar for Invoices/Bills -->
                    <field name="approval_state" widget="statusbar" 
                           statusbar_visible="draft,under_review,for_approval,approved,posted" 
                           statusbar_colors='{"draft":"secondary","under_review":"info","for_approval":"warning","approved":"success","posted":"success"}' 
                           attrs="{'invisible': [('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'])]}"/>

                    <!-- Hidden fields for button conditions -->
                    <field name="can_submit_for_review" invisible="1"/>
                    <field name="can_review" invisible="1"/>
                    <field name="can_approve" invisible="1"/>
                    <field name="can_post_manual" invisible="1"/>

                    <!-- Approval Workflow Buttons -->
                    <button name="action_submit_for_review" 
                            string="Submit for Review" 
                            type="object" 
                            class="btn-primary" 
                            attrs="{'invisible': ['|', ('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']), ('can_submit_for_review', '=', False)]}"/>

                    <button name="action_review_approve" 
                            string="Review & Approve" 
                            type="object" 
                            class="btn-success" 
                            groups="account_payment_final.group_payment_reviewer" 
                            attrs="{'invisible': ['|', ('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']), ('can_review', '=', False)]}"/>

                    <button name="action_final_approve" 
                            string="Final Approve" 
                            type="object" 
                            class="btn-success" 
                            groups="account_payment_final.group_payment_approver" 
                            attrs="{'invisible': ['|', ('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']), ('can_approve', '=', False)]}"/>

                    <button name="action_reject_invoice_bill" 
                            string="Reject" 
                            type="object" 
                            class="btn-danger" 
                            groups="account_payment_final.group_payment_approver" 
                            attrs="{'invisible': [('approval_state', 'not in', ['under_review', 'for_approval'])]}" 
                            confirm="Are you sure you want to reject this document?"/>
                </xpath>

                <!-- Add QR code field for invoices -->
                <xpath expr="//field[@name='name']" position="after">
                    <field name="qr_code_invoice" widget="image" 
                           options="{'size': [150, 150]}" 
                           attrs="{'invisible': ['|', ('qr_code_invoice', '=', False), ('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'])]}"/>
                </xpath>

                <!-- Add approval tracking fields -->
                <xpath expr="//notebook" position="inside">
                    <page string="Approval Workflow" 
                          name="approval_workflow" 
                          attrs="{'invisible': ['|', ('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']), ('approval_state', '=', False)]}">
                        <group>
                            <group string="Approval Status">
                                <field name="approval_state" readonly="1"/>
                                <field name="verification_status" readonly="1"/>
                                <field name="reviewer_id" readonly="1"/>
                                <field name="approver_id" readonly="1"/>
                            </group>
                            <group string="Approval Dates">
                                <field name="reviewer_date" readonly="1"/>
                                <field name="approver_date" readonly="1"/>
                            </group>
                        </group>
                    </page>
                </xpath>

            </field>
        </record>

        <!-- Enhanced Invoice/Bill Tree View -->
        <record id="view_invoice_tree_enhanced" model="ir.ui.view">
            <field name="name">account.move.tree.enhanced</field>
            <field name="model">account.move</field>
            <field name="inherit_id" ref="account.view_move_tree"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='state']" position="after">
                    <field name="approval_state" widget="badge" optional="show" 
                           decoration-info="approval_state == 'draft'" 
                           decoration-warning="approval_state in ['under_review', 'for_approval']" 
                           decoration-success="approval_state in ['approved', 'posted']"
                           attrs="{'invisible': [('move_type', 'not in', ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'])]}"/>
                    
                    <field name="verification_status" widget="badge" optional="hide" 
                           decoration-info="verification_status == 'pending'" 
                           decoration-success="verification_status == 'verified'" 
                           decoration-danger="verification_status == 'rejected'"/>
                </xpath>

                <xpath expr="//field[@name='partner_id']" position="after">
                    <field name="reviewer_id" optional="hide"/>
                    <field name="approver_id" optional="hide"/>
                </xpath>
            </field>
        </record>

    </data>
</odoo>
