# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class TestAppointmentModels(TransactionCase):
    """Test suite for Online Appointment Models"""

    def setUp(self):
        super().setUp()
        
        # Create test user
        self.test_user = self.env['res.users'].create({
            'name': 'Test Service Provider',
            'login': 'test_provider',
            'email': 'provider@test.com',
            'tz': 'UTC'
        })
        
        # Create test customer
        self.test_customer = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'customer@test.com',
            'phone': '+1234567890'
        })

    def test_appointment_option_creation(self):
        """Test appointment option model creation and validation"""
        option = self.env['online_appointment.option'].create({
            'name': 'Test Consultation',
            'description': 'Test consultation service',
            'duration': 1.0,
            'active': True,
            'website_published': True
        })
        
        self.assertEqual(option.name, 'Test Consultation')
        self.assertEqual(option.duration, 1.0)
        self.assertTrue(option.active)
        self.assertTrue(option.website_published)

    def test_appointment_option_validation(self):
        """Test appointment option validation constraints"""
        with self.assertRaises(ValidationError):
            # Duration must be positive
            self.env['online_appointment.option'].create({
                'name': 'Invalid Option',
                'duration': 0.0
            })

    def test_appointment_slot_creation(self):
        """Test appointment slot model creation and validation"""
        slot = self.env['online_appointment.slot'].create({
            'user_id': self.test_user.id,
            'day': '0',  # Monday
            'slot': 9.0,  # 9:00 AM
            'active': True
        })
        
        self.assertEqual(slot.user_id, self.test_user)
        self.assertEqual(slot.day, '0')
        self.assertEqual(slot.slot, 9.0)
        self.assertTrue(slot.active)

    def test_appointment_slot_validation(self):
        """Test appointment slot validation constraints"""
        with self.assertRaises(ValidationError):
            # Slot time must be within working hours
            self.env['online_appointment.slot'].create({
                'user_id': self.test_user.id,
                'day': '0',
                'slot': 25.0  # Invalid time
            })

    def test_appointment_registration_creation(self):
        """Test appointment registration model creation"""
        # Create calendar event first
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': datetime.now() + timedelta(days=1),
            'stop': datetime.now() + timedelta(days=1, hours=1),
        })
        
        registration = self.env['online_appointment.registration'].create({
            'event_id': event.id,
            'partner_id': self.test_customer.id,
            'appointee_id': self.test_user.partner_id.id,
            'customer_name': 'Test Customer',
            'customer_email': 'customer@test.com',
            'state': 'confirmed'
        })
        
        self.assertEqual(registration.event_id, event)
        self.assertEqual(registration.partner_id, self.test_customer)
        self.assertEqual(registration.customer_name, 'Test Customer')
        self.assertEqual(registration.state, 'confirmed')

    def test_appointment_registration_validation(self):
        """Test appointment registration validation"""
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': datetime.now() - timedelta(days=1),  # Past date
            'stop': datetime.now() - timedelta(days=1) + timedelta(hours=1),
        })
        
        with self.assertRaises(ValidationError):
            # Should not allow past appointments
            self.env['online_appointment.registration'].create({
                'event_id': event.id,
                'customer_name': 'Test Customer',
                'customer_email': 'invalid-email',  # Invalid email
            })

    def test_appointment_registration_actions(self):
        """Test appointment registration state actions"""
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': datetime.now() + timedelta(days=1),
            'stop': datetime.now() + timedelta(days=1, hours=1),
        })
        
        registration = self.env['online_appointment.registration'].create({
            'event_id': event.id,
            'customer_name': 'Test Customer',
            'customer_email': 'customer@test.com',
            'state': 'pending'
        })
        
        # Test confirmation
        registration.action_confirm_appointment()
        self.assertEqual(registration.state, 'confirmed')
        
        # Test cancellation
        registration.action_cancel_appointment()
        self.assertEqual(registration.state, 'cancelled')
        
        # Test that cancelled events can't be confirmed
        with self.assertRaises(UserError):
            registration.action_confirm_appointment()

    def test_appointment_duration_computation(self):
        """Test duration computation in registration"""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': start_time,
            'stop': end_time,
        })
        
        registration = self.env['online_appointment.registration'].create({
            'event_id': event.id,
            'customer_name': 'Test Customer',
            'customer_email': 'customer@test.com',
        })
        
        self.assertEqual(registration.duration_hours, 2.0)

    def test_display_name_computation(self):
        """Test display name computation"""
        option = self.env['online_appointment.option'].create({
            'name': 'Test Consultation',
            'duration': 1.0
        })
        
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': datetime.now() + timedelta(days=1),
            'stop': datetime.now() + timedelta(days=1, hours=1),
        })
        
        registration = self.env['online_appointment.registration'].create({
            'event_id': event.id,
            'customer_name': 'John Doe',
            'customer_email': 'john@test.com',
            'appointment_option_id': option.id,
        })
        
        self.assertIn('John Doe', registration.display_name)
        self.assertIn('Test Consultation', registration.display_name)