odoo.define('commission_lines.dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');

var CommissionDashboard = AbstractAction.extend({
    template: 'CommissionDashboard',
    
    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['CommissionDashboard'];
    },
    
    willStart: function() {
        var self = this;
        return this._super().then(function() {
            return self.fetch_data();
        });
    },
    
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.$('.commission_refresh').click(function() {
                self.fetch_data().then(function() {
                    self.render_dashboard();
                });
            });
        });
    },
    
    fetch_data: function() {
        var self = this;
        return rpc.query({
            model: 'commission.line',
            method: 'get_dashboard_data',
        }).then(function(result) {
            self.commission_data = result;
        });
    },
    
    render_dashboard: function() {
        var self = this;
        this.$('.commission_dashboard_content').html(core.qweb.render('CommissionDashboardContent', {
            widget: self,
            data: self.commission_data
        }));
    },
    
});

core.action_registry.add('commission_dashboard', CommissionDashboard);

return CommissionDashboard;

});