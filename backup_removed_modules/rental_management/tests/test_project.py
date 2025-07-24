import psycopg2
from odoo.exceptions import ValidationError, AccessError
from .common import CreateRentalData
from odoo.tests.common import tagged

import datetime


@tagged("property_project")
class TestProject(CreateRentalData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_property_one = cls._create_project(
            name="Project One", project_sequence="10",
            project_for="rent", property_type="residential",
            property_subtype_id=1, date_of_project=datetime.datetime.today(), )
        
        cls.test_property_two = cls._create_project(
            name="Project Two", project_sequence="20",
            project_for="sale", property_type="commercial",
            property_subtype_id=11, date_of_project=datetime.datetime.today(),)
        
        cls.test_property_three = cls._create_project(
            name="Project Three", project_sequence="30",
            project_for="rent", property_type="industrial",
            property_subtype_id=8, date_of_project=datetime.datetime.today(),)
        
        cls.test_property_four = cls._create_project(
            name="Project Four", project_sequence="40",
            project_for="sale", property_type="land",
            property_subtype_id=7, date_of_project=datetime.datetime.today(), )
        
        cls.test_setupclass_property = cls._create_project(
            name="SetUp Class", project_sequence="50",
            project_for="rent", property_type="residential",
            property_subtype_id=1, date_of_project=datetime.datetime.today(), )
        

    def setUp(self):
        """Set up for Property"""
        super().setUp()
        self.test_setup_property = self._create_project(
            name="SetUp Method", project_sequence="60", project_for="sale", 
            property_type="commercial", property_subtype_id=12,
            date_of_project=datetime.datetime.today(),
        )

    def test_project_creation(self):
        """Test project creation"""

        self.assertTrue(self.test_property_one)
        self.assertTrue(self.test_property_two)
        self.assertTrue(self.test_property_three)
        self.assertTrue(self.test_property_four)
        self.assertEqual(self.test_property_one.project_for, "rent")
        data = self.env["property.sub.type"].search(
            [("type", "!=", "residential")])

        self.assertNotIn(self.test_property_one.property_subtype_id, data)

        data = self.env["property.sub.type"].search(
            [("type", "!=", "commercial")])

        self.assertNotIn(self.test_property_two.property_subtype_id, data)

        data = self.env["property.sub.type"].search(
            [("type", "!=", "industrial")])

        self.assertNotIn(self.test_property_three.property_subtype_id, data)

        data = self.env["property.sub.type"].search([("type", "!=", "land")])

        self.assertNotIn(self.test_property_four.property_subtype_id, data)

    def test_required_fields(self):
        """
        While chack if the it raise the error check that both
        """
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.project = self.env["property.project"]
                self.project.create({})

    def test_compute_count(self):
        document_one = self.env["project.document.line"].create({
            "name": "Document One", "document_name": "Common",
            "document_file": self.document, "user_id": self.env.user.id,
            "project_id": self.test_property_one.id, })
        document_two = self.env["project.document.line"].create({
            "name": "Document One", "document_name": "Common",
            "document_file": self.document, "user_id": self.env.user.id,
            "project_id": self.test_property_one.id, })
        document_three = self.env["project.document.line"].create({
            "name": "Document One", "document_name": "Common",
            "document_file": self.document, "user_id": self.env.user.id,
            "project_id": self.test_property_one.id, })

        self.test_property_one.compute_count()
        self.test_property_two.compute_count()

        self.assertEqual(self.test_property_one.document_count, 3)
        self.assertEqual(self.test_property_two.document_count, 0)

        create_unit_wizard = self._create_units_wizard(
            5, 5, 1, active_id=self.test_property_one.id, unit_from="project"
        )
        create_unit_wizard.action_create_property_unit()

        self.test_property_one.compute_count()
        self.test_property_two.compute_count()

        self.assertEqual(self.test_property_one.unit_count, 25)
        self.assertEqual(self.test_property_two.unit_count, 0)

        self.assertTrue(self.test_property_one.is_sub_project)

        create_sub_project_wizard = self._create_sub_project_wizard(
            "Sub Project One", "S1", 5, 5, active_id=self.test_property_one.id)

        create_sub_project_wizard.create_sub_project()

        self.test_property_one._compute_sub_project_count()
        self.test_property_two._compute_sub_project_count()

        self.assertEqual(self.test_property_one.total_subproject, 1)
        self.assertEqual(self.test_property_two.total_subproject, 0)

        project_one_units = self.env["property.details"].search(
            [("property_project_id", "=", self.test_property_one.id)], limit=10
        )

        for rec in project_one_units:
            if rec.id % 2 == 0:
                rec.action_in_available()
                self.assertEqual(rec.stage, "available")
                self.assertEqual(rec.sale_lease, "for_tenancy")
            else:
                rec.sale_lease = "for_sale"
                self.assertEqual(rec.stage, "draft")
                self.assertEqual(rec.sale_lease, "for_sale")

        self.test_property_one.compute_count()
        self.test_property_two.compute_count()

        self.assertEqual(self.test_property_one.available_unit_count, 5)
        self.assertEqual(self.test_property_two.available_unit_count, 0)

        project_one_units = self.env["property.details"].search(
            [("property_project_id", "=", self.test_property_one.id)],
            limit=10,
            offset=10,
        )

        for rec in project_one_units:
            if rec.id % 2 == 0:
                rec.stage = "sale"
                self.assertEqual(rec.stage, "sale")
            else:
                rec.stage = "sold"
                self.assertEqual(rec.stage, "sold")

        self.test_property_one.compute_count()
        self.test_property_two.compute_count()

        self.assertEqual(self.test_property_one.sold_count, 10)
        self.assertEqual(self.test_property_two.sold_count, 0)

        project_one_units = self.env["property.details"].search(
            [("property_project_id", "=", self.test_property_one.id)],
            limit=5,
            offset=20,
        )

        for rec in project_one_units:
            rec.stage = "on_lease"
            self.assertEqual(rec.stage, "on_lease")

        self.test_property_one.compute_count()
        self.test_property_two.compute_count()

        self.assertEqual(self.test_property_one.rent_count, 5)
        self.assertEqual(self.test_property_two.rent_count, 0)

    def test_all_action_methods(self):

        action = self.test_property_one.action_document_count()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Documents")
        self.assertIn(("project_id", "=", self.test_property_one.id),
            action.get("domain", []))
        self.assertEqual(action.get("context", {}).get("default_project_id"),
            self.test_property_one.id,)

        action = self.test_property_two.action_document_count()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Documents")
        self.assertIn(("project_id", "=", self.test_property_two.id),
            action.get("domain", []))
        
        self.assertEqual(action.get("context", {}).get("default_project_id"),
            self.test_property_two.id,)

        action = self.test_property_three.action_document_count()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Documents")
        self.assertIn(("project_id", "=", self.test_property_three.id),
            action.get("domain", []))
        self.assertEqual(action.get("context", {}).get("default_project_id"),
            self.test_property_three.id,)

        action = self.test_property_four.action_document_count()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Documents")
        self.assertIn(("project_id", "=", self.test_property_four.id),
            action.get("domain", []))
        self.assertEqual(action.get("context", {}).get("default_project_id"),
                         self.test_property_four.id, )

        action = self.test_property_one.action_sub_project_count()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Sub Projects")
        self.assertIn(("property_project_id", "=", self.test_property_one.id),
                      action.get("domain", []),)
        self.assertEqual(action["res_model"], "property.sub.project")

        action = self.test_property_one.action_view_unit()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Units")
        self.assertIn(("property_project_id", "=", self.test_property_one.id),
            action.get("domain", []),)
        self.assertEqual(action["res_model"], "property.details")

        action = self.test_property_one.action_view_available_unit()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Available Units")
        self.assertIn(("property_project_id", "=", self.test_property_one.id),
                      action.get("domain", []),
                      )
        self.assertIn(("stage", "=", "available"), action.get("domain", []))
        self.assertEqual(action["res_model"], "property.details")

        action = self.test_property_one.action_view_sold_unit()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Sold / Sale Units")
        self.assertIn(("property_project_id", "=", self.test_property_one.id),
                      action.get("domain", []),)

        self.assertIn(("stage", "in", ["sold", "sale"]),
                      action.get("domain", []))
        self.assertEqual(action["res_model"], "property.details")

        action = self.test_property_one.action_view_rent_unit()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["name"], "Rent Units")
        self.assertIn(("property_project_id", "=", self.test_property_one.id),
            action.get("domain", []),)
        self.assertIn(("stage", "=", "on_lease"), action.get("domain", []))
        self.assertEqual(action["res_model"], "property.details")

        self.test_property_one.longitude = 45
        self.test_property_one.latitude = 30

        action = self.test_property_one.action_gmap_location()

        self.assertIsInstance(action, dict)
        self.assertEqual(action["url"],
            "https://maps.google.com/maps?q=loc:30,45",)

        with self.assertRaises(ValidationError):
            self.test_property_two.action_gmap_location()

        self.test_property_one.action_status_available()
        self.assertEqual(self.test_property_one.status, "available")

        self.test_property_one.action_status_draft()
        self.assertEqual(self.test_property_one.status, "draft")

    def test_unlink(self):
        create_sub_project_wizard = self._create_sub_project_wizard(
            "Sub Project One", "S1", 5, 5, active_id=self.test_property_one.id)

        create_sub_project_wizard.create_sub_project()

        with self.assertRaises(ValidationError):
            self.test_property_one.unlink()
