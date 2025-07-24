/* Calendar Extended JavaScript */

odoo.define('calendar_extended.CalendarAnnouncement', function (require) {
'use strict';

var FormController = require('web.FormController');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var CalendarAnnouncementFormController = FormController.extend({
    events: _.extend({}, FormController.prototype.events, {
        'click .o_quick_select_all': '_onQuickSelectAll',
        'click .o_quick_select_department': '_onQuickSelectDepartment',
    }),

    _onQuickSelectAll: function (event) {
        event.preventDefault();
        this._openDepartmentWizard('all');
    },

    _onQuickSelectDepartment: function (event) {
        event.preventDefault();
        var departmentId = $(event.currentTarget).data('department-id');
        this._openDepartmentWizard('departments', departmentId);
    },

    _openDepartmentWizard: function (mode, departmentId) {
        var self = this;
        var context = {
            default_announcement_id: this.model.get(this.handle).res_id,
            default_selection_mode: mode
        };

        if (departmentId) {
            context.default_department_ids = [[6, 0, [departmentId]]];
        }

        this.do_action({
            type: 'ir.actions.act_window',
            name: 'Select Attendees',
            res_model: 'calendar.department.select.wizard',
            view_mode: 'form',
            target: 'new',
            context: context
        }, {
            on_close: function () {
                self.reload();
            }
        });
    },
});

var CalendarAnnouncementFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: CalendarAnnouncementFormController,
    }),
});

viewRegistry.add('calendar_announcement_form', CalendarAnnouncementFormView);

return {
    CalendarAnnouncementFormController: CalendarAnnouncementFormController,
    CalendarAnnouncementFormView: CalendarAnnouncementFormView,
};

});
