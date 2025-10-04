# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError


class TestAppointmentSecurity(TransactionCase):
    """Test suite for Online Appointment Security"""

    def setUp(self):
        super().setUp()
        
        # Create test users
        self.admin_user = self.env.ref('base.user_admin')
        
        self.internal_user = self.env['res.users'].create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'internal@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        
        self.portal_user = self.env['res.users'].create({
            'name': 'Portal User',
            'login': 'portal_user',
            'email': 'portal@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        
        # Create test data
        self.appointment_option = self.env['online_appointment.option'].create({
            'name': 'Test Consultation',
            'duration': 1.0,
            'active': True,
            'website_published': True
        })
        
        self.appointment_slot = self.env['online_appointment.slot'].create({
            'user_id': self.internal_user.id,
            'day': '0',
            'slot': 10.0,
            'active': True
        })

    def test_appointment_option_access_rights(self):
        """Test appointment option access rights"""
        # Admin should have full access
        option_as_admin = self.appointment_option.sudo(self.admin_user)
        self.assertTrue(option_as_admin.name)
        
        # Portal user should only read
        option_as_portal = self.appointment_option.sudo(self.portal_user)
        self.assertTrue(option_as_portal.name)
        
        with self.assertRaises(AccessError):
            option_as_portal.write({'name': 'Modified'})

    def test_appointment_slot_access_rights(self):
        """Test appointment slot access rights"""
        # Owner should have full access
        slot_as_owner = self.appointment_slot.sudo(self.internal_user)
        self.assertTrue(slot_as_owner.user_id)
        
        # Portal user should only read
        slot_as_portal = self.appointment_slot.sudo(self.portal_user)
        self.assertTrue(slot_as_portal.user_id)
        
        with self.assertRaises(AccessError):
            slot_as_portal.write({'slot': 11.0})

    def test_appointment_registration_security(self):
        """Test appointment registration security rules"""
        # Create registrations for different users
        event1 = self.env['calendar.event'].create({
            'name': 'Test Appointment 1',
            'start': '2025-01-01 10:00:00',
            'stop': '2025-01-01 11:00:00',
        })
        
        registration1 = self.env['online_appointment.registration'].create({
            'event_id': event1.id,
            'partner_id': self.portal_user.partner_id.id,
            'customer_name': 'Portal User',
            'customer_email': 'portal@test.com',
        })
        
        event2 = self.env['calendar.event'].create({
            'name': 'Test Appointment 2',
            'start': '2025-01-01 11:00:00',
            'stop': '2025-01-01 12:00:00',
        })
        
        registration2 = self.env['online_appointment.registration'].create({
            'event_id': event2.id,
            'partner_id': self.internal_user.partner_id.id,
            'customer_name': 'Internal User',
            'customer_email': 'internal@test.com',
        })
        
        # Portal user should only see their own registrations
        registrations_as_portal = self.env['online_appointment.registration'].sudo(self.portal_user).search([])
        self.assertEqual(len(registrations_as_portal), 1)
        self.assertEqual(registrations_as_portal.id, registration1.id)
        
        # Internal user should see all registrations
        registrations_as_internal = self.env['online_appointment.registration'].sudo(self.internal_user).search([])
        self.assertGreaterEqual(len(registrations_as_internal), 2)

    def test_portal_user_registration_creation(self):
        """Test that portal users can create their own registrations"""
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': '2025-01-01 10:00:00',
            'stop': '2025-01-01 11:00:00',
        })
        
        # Portal user should be able to create registration for themselves
        registration = self.env['online_appointment.registration'].sudo(self.portal_user).create({
            'event_id': event.id,
            'partner_id': self.portal_user.partner_id.id,
            'customer_name': 'Portal User',
            'customer_email': 'portal@test.com',
        })
        
        self.assertEqual(registration.partner_id, self.portal_user.partner_id)

    def test_portal_user_cannot_delete_registrations(self):
        """Test that portal users cannot delete registrations"""
        event = self.env['calendar.event'].create({
            'name': 'Test Appointment',
            'start': '2025-01-01 10:00:00',
            'stop': '2025-01-01 11:00:00',
        })
        
        registration = self.env['online_appointment.registration'].create({
            'event_id': event.id,
            'partner_id': self.portal_user.partner_id.id,
            'customer_name': 'Portal User',
            'customer_email': 'portal@test.com',
        })
        
        # Portal user should not be able to delete
        registration_as_portal = registration.sudo(self.portal_user)
        with self.assertRaises(AccessError):
            registration_as_portal.unlink()

    def test_public_user_read_access(self):
        """Test public user read access to published options"""
        # Public user should be able to read published options
        public_user = self.env.ref('base.public_user')
        
        # Should be able to read published options
        options_as_public = self.env['online_appointment.option'].sudo(public_user).search([
            ('website_published', '=', True)
        ])
        self.assertGreater(len(options_as_public), 0)
        
        # Should be able to read active slots
        slots_as_public = self.env['online_appointment.slot'].sudo(public_user).search([
            ('active', '=', True)
        ])
        self.assertGreater(len(slots_as_public), 0)

    def test_user_slot_ownership(self):
        """Test that users can only manage their own slots"""
        # Create another user
        other_user = self.env['res.users'].create({
            'name': 'Other User',
            'login': 'other_user',
            'email': 'other@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        
        # Other user should not see first user's slots in their domain
        slots_as_other = self.env['online_appointment.slot'].sudo(other_user).search([])
        user_slots = slots_as_other.filtered(lambda s: s.user_id == self.internal_user)
        
        # Due to record rules, other user shouldn't see other user's slots
        self.assertEqual(len(user_slots), 0)