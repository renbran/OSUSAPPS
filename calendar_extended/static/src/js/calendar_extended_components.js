/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class DepartmentGroupSelector extends Component {
    static template = "calendar_extended.DepartmentGroupSelector";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            departmentGroups: [],
            selectedGroups: [],
            selectedEmployees: [],
            loading: false
        });

        this.loadDepartmentGroups();
    }

    async loadDepartmentGroups() {
        this.state.loading = true;
        try {
            const groups = await this.orm.searchRead(
                "calendar.department.group",
                [],
                ["id", "name", "department_id", "employee_ids"]
            );
            this.state.departmentGroups = groups;
        } catch (error) {
            console.error("Error loading department groups:", error);
        } finally {
            this.state.loading = false;
        }
    }

    onGroupToggle(groupId) {
        const index = this.state.selectedGroups.indexOf(groupId);
        if (index > -1) {
            this.state.selectedGroups.splice(index, 1);
        } else {
            this.state.selectedGroups.push(groupId);
        }
        this.updateSelectedEmployees();
    }

    async updateSelectedEmployees() {
        if (this.state.selectedGroups.length === 0) {
            this.state.selectedEmployees = [];
            return;
        }

        try {
            const groups = await this.orm.searchRead(
                "calendar.department.group",
                [["id", "in", this.state.selectedGroups]],
                ["employee_ids"]
            );
            
            const employeeIds = new Set();
            groups.forEach(group => {
                group.employee_ids.forEach(id => employeeIds.add(id));
            });
            
            this.state.selectedEmployees = Array.from(employeeIds);
            
            // Trigger parent component update
            if (this.props.onSelectionChange) {
                this.props.onSelectionChange(this.state.selectedEmployees);
            }
        } catch (error) {
            console.error("Error updating selected employees:", error);
        }
    }

    isGroupSelected(groupId) {
        return this.state.selectedGroups.includes(groupId);
    }
}

export class MeetingApprovalWidget extends Component {
    static template = "calendar_extended.MeetingApprovalWidget";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            approvalNotes: "",
            processing: false
        });
    }

    async approveMeeting() {
        if (this.state.processing) return;
        
        this.state.processing = true;
        try {
            await this.orm.call(
                "calendar.internal.meeting",
                "action_approve",
                [this.props.meetingId],
                { approval_notes: this.state.approvalNotes }
            );
            
            this.notification.add("Meeting approved successfully", { type: "success" });
            
            if (this.props.onApproval) {
                this.props.onApproval();
            }
        } catch (error) {
            console.error("Error approving meeting:", error);
            this.notification.add("Error approving meeting", { type: "danger" });
        } finally {
            this.state.processing = false;
        }
    }

    async rejectMeeting() {
        if (this.state.processing) return;
        
        this.state.processing = true;
        try {
            await this.orm.call(
                "calendar.internal.meeting",
                "action_reject",
                [this.props.meetingId],
                { rejection_reason: this.state.approvalNotes }
            );
            
            this.notification.add("Meeting rejected", { type: "info" });
            
            if (this.props.onRejection) {
                this.props.onRejection();
            }
        } catch (error) {
            console.error("Error rejecting meeting:", error);
            this.notification.add("Error rejecting meeting", { type: "danger" });
        } finally {
            this.state.processing = false;
        }
    }

    onNotesChange(event) {
        this.state.approvalNotes = event.target.value;
    }
}
