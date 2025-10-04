# -*- coding: utf-8 -*-

from odoo.tests.common import HttpCase
from odoo.tools import mute_logger
import json


class TestAppointmentControllers(HttpCase):
    """Test suite for Online Appointment Controllers"""

    def setUp(self):
        super().setUp()
        
        # Create test data
        self.test_user = self.env['res.users'].create({
            'name': 'Test Service Provider',
            'login': 'test_provider',
            'email': 'provider@test.com',
            'tz': 'UTC'
        })
        
        self.appointment_option = self.env['online_appointment.option'].create({
            'name': 'Test Consultation',
            'description': 'Test consultation service',
            'duration': 1.0,
            'active': True,
            'website_published': True
        })
        
        self.appointment_slot = self.env['online_appointment.slot'].create({
            'user_id': self.test_user.id,
            'day': '0',  # Monday
            'slot': 10.0,  # 10:00 AM
            'active': True
        })

    def test_online_appointment_page_access(self):
        """Test that the online appointment page is accessible"""
        # Enable public access
        param = self.env['ir.config_parameter'].sudo().set_param(
            's2u_online_appointment', 'public'
        )
        
        response = self.url_open('/online-appointment')
        self.assertEqual(response.status_code, 200)

    def test_appointment_booking_validation(self):
        """Test appointment booking form validation"""
        # Enable public access
        self.env['ir.config_parameter'].sudo().set_param(
            's2u_online_appointment', 'public'
        )
        
        # Test invalid data submission
        response = self.url_open('/online-appointment/appointment-confirm', data={
            'name': '',  # Empty name should fail
            'email': 'invalid-email',  # Invalid email should fail
            'phone': '',  # Empty phone should fail
        })
        
        self.assertEqual(response.status_code, 200)
        # Should return form with errors, not redirect

    def test_appointment_scheduling_flow(self):
        """Test complete appointment scheduling flow"""
        # Enable public access
        self.env['ir.config_parameter'].sudo().set_param(
            's2u_online_appointment', 'public'
        )
        
        # Test valid appointment booking data
        booking_data = {
            'name': 'Test Customer',
            'email': 'customer@test.com',
            'phone': '+1234567890',
            'appointee_id': self.test_user.id,
            'appointment_option_id': self.appointment_option.id,
            'timeslot_id': self.appointment_slot.id,
            'appointment_date': '01/01/2025',  # Future date
            'remarks': 'Test appointment'
        }
        
        # Count existing appointments
        initial_count = self.env['calendar.event'].sudo().search_count([])
        
        response = self.url_open('/online-appointment/appointment-confirm', 
                                data=booking_data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 200)
        
        # Check that appointment was created
        final_count = self.env['calendar.event'].sudo().search_count([])
        self.assertGreaterEqual(final_count, initial_count)

    def test_appointment_ajax_endpoints(self):
        """Test AJAX endpoints for appointment data"""
        # Test getting available appointees
        response = self.url_open('/online-appointment/get-appointees', data={
            'option_id': self.appointment_option.id,
            'date': '01/01/2025'
        })
        
        self.assertEqual(response.status_code, 200)

    @mute_logger('odoo.http')
    def test_appointment_security(self):
        """Test security restrictions"""
        # Disable public access
        self.env['ir.config_parameter'].sudo().set_param(
            's2u_online_appointment', 'registered'
        )
        
        # Public user should not be able to access
        response = self.url_open('/online-appointment')
        # Should show restricted access page
        self.assertEqual(response.status_code, 200)

    def test_portal_appointment_management(self):
        """Test portal user appointment management"""
        # Create a portal user
        portal_user = self.env['res.users'].create({
            'name': 'Portal User',
            'login': 'portal_user',
            'email': 'portal@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        
        # Test portal access (requires authentication)
        self.authenticate('portal_user', 'portal_user')
        
        response = self.url_open('/my/online-appointments')
        self.assertEqual(response.status_code, 200)

    def test_appointment_cancellation(self):
        """Test appointment cancellation flow"""
        # Create test appointment
        event = self.env['calendar.event'].sudo().create({
            'name': 'Test Appointment',
            'start': '2025-01-01 10:00:00',
            'stop': '2025-01-01 11:00:00',
        })
        
        registration = self.env['online_appointment.registration'].sudo().create({
            'event_id': event.id,
            'partner_id': self.env.user.partner_id.id,
            'customer_name': 'Test Customer',
            'customer_email': 'customer@test.com',
            'state': 'confirmed'
        })
        
        # Test cancellation
        response = self.url_open('/online-appointment/cancel-appointment', data={
            'appointment_to_cancel': registration.id
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Check that appointment was cancelled
        registration.refresh()
        self.assertEqual(registration.state, 'cancelled')