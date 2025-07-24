/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CalendarExtendedWidget extends Component {
    static template = "calendar_extended.CalendarExtendedWidget";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            meetings: [],
            selectedDepartment: null,
            departments: [],
            loading: false
        });

        onMounted(() => {
            this.loadDepartments();
            this.loadMeetings();
        });
    }

    async loadDepartments() {
        try {
            const departments = await this.orm.searchRead(
                "hr.department",
                [],
                ["id", "name", "employee_ids"]
            );
            this.state.departments = departments;
        } catch (error) {
            console.error("Error loading departments:", error);
        }
    }

    async loadMeetings() {
        this.state.loading = true;
        try {
            const domain = this.state.selectedDepartment 
                ? [["attendee_ids.employee_id.department_id", "=", this.state.selectedDepartment]]
                : [];
            
            const meetings = await this.orm.searchRead(
                "calendar.internal.meeting",
                domain,
                ["id", "name", "start_datetime", "state", "organizer_id", "attendee_ids"]
            );
            this.state.meetings = meetings;
        } catch (error) {
            console.error("Error loading meetings:", error);
            this.notification.add("Error loading meetings", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    onDepartmentChange(event) {
        this.state.selectedDepartment = event.target.value ? parseInt(event.target.value) : null;
        this.loadMeetings();
    }

    async createQuickMeeting() {
        try {
            const action = await this.orm.call(
                "calendar.quick.meeting.wizard",
                "open_wizard",
                []
            );
            this.action.doAction(action);
        } catch (error) {
            console.error("Error opening quick meeting wizard:", error);
            this.notification.add("Error opening meeting wizard", { type: "danger" });
        }
    }

    async approveMeeting(meetingId) {
        try {
            await this.orm.call(
                "calendar.internal.meeting",
                "action_approve",
                [meetingId]
            );
            this.notification.add("Meeting approved successfully", { type: "success" });
            this.loadMeetings();
        } catch (error) {
            console.error("Error approving meeting:", error);
            this.notification.add("Error approving meeting", { type: "danger" });
        }
    }

    async rejectMeeting(meetingId) {
        try {
            await this.orm.call(
                "calendar.internal.meeting",
                "action_reject",
                [meetingId]
            );
            this.notification.add("Meeting rejected", { type: "info" });
            this.loadMeetings();
        } catch (error) {
            console.error("Error rejecting meeting:", error);
            this.notification.add("Error rejecting meeting", { type: "danger" });
        }
    }

    getStateClass(state) {
        const stateClasses = {
            'draft': 'badge-secondary',
            'pending_approval': 'badge-warning',
            'approved': 'badge-success',
            'confirmed': 'badge-primary',
            'completed': 'badge-info',
            'cancelled': 'badge-danger'
        };
        return stateClasses[state] || 'badge-secondary';
    }

    getStateLabel(state) {
        const stateLabels = {
            'draft': 'Draft',
            'pending_approval': 'Pending Approval',
            'approved': 'Approved',
            'confirmed': 'Confirmed',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        };
        return stateLabels[state] || state;
    }

    formatDateTime(datetime) {
        if (!datetime) return 'Not set';
        const date = new Date(datetime);
        return date.toLocaleString();
    }
}

// Register the widget
registry.category("view_widgets").add("calendar_extended_widget", CalendarExtendedWidget);
