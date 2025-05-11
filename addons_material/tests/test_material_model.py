from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger
from psycopg2 import IntegrityError
from psycopg2.errors import NotNullViolation

class TestMaterialModel(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Supplier'})

    def test_material_create_valid(self):
        """Ensure a material can be created with valid data."""
        material = self.env['material.material'].create({
            'name': 'Test',
            'code': 'VALID123',
            'material_type': 'cotton',
            'buy_price': 150,
            'supplier_id': self.partner.id
        })
        self.assertTrue(material.id)

    def test_material_buy_price_too_low(self):
        """Ensure material creation fails if buy_price is less than 100."""
        with self.assertRaises(ValidationError):
            self.env['material.material'].create({
                'name': 'Too Cheap',
                'code': 'CHEAP001',
                'material_type': 'cotton',
                'buy_price': 50,
                'supplier_id': self.partner.id
            })

    def test_update_material_buy_price_too_low(self):
        """Ensure updating buy_price to less than 100 raises ValidationError."""
        material = self.env['material.material'].create({
            'name': 'Valid Material',
            'code': 'LOW001',
            'material_type': 'fabric',
            'buy_price': 150,
            'supplier_id': self.partner.id
        })
        with self.assertRaises(ValidationError):
            material.write({'buy_price': 50})

    def test_material_code_unique_constraint(self):
        """Ensure creating materials with duplicate code raises IntegrityError."""
        self.env['material.material'].create({
            'name': 'First',
            'code': 'DUPL01',
            'material_type': 'jeans',
            'buy_price': 150,
            'supplier_id': self.partner.id
        })
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self.env['material.material'].create({
                    'name': 'Second',
                    'code': 'DUPL01',
                    'material_type': 'jeans',
                    'buy_price': 160,
                    'supplier_id': self.partner.id
                })

    def test_update_duplicate_code_not_allowed(self):
        """Ensure updating a material to a duplicate code raises IntegrityError."""
        material1 = self.env['material.material'].create({
            'name': 'Material One',
            'code': 'CODE1',
            'material_type': 'cotton',
            'buy_price': 120,
            'supplier_id': self.partner.id
        })

        material2 = self.env['material.material'].create({
            'name': 'Material Two',
            'code': 'CODE2',
            'material_type': 'cotton',
            'buy_price': 130,
            'supplier_id': self.partner.id
        })

        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                material2.write({'code': 'CODE1'})
                material2.flush()

    def test_material_missing_required_field(self):
        """Ensure missing required field (name) raises NotNullViolation."""
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(NotNullViolation):
                self.env['material.material'].create({
                    'code': 'REQ001',
                    'material_type': 'cotton',
                    'buy_price': '150',
                })

    def test_update_material_missing_name(self):
        """Ensure updating name to False (null) raises NotNullViolation."""
        material = self.env['material.material'].create({
            'name': 'Complete',
            'code': 'FULL001',
            'material_type': 'jeans',
            'buy_price': 150,
            'supplier_id': self.partner.id
        })

        with mute_logger('odoo.sql_db'):
            with self.assertRaises(NotNullViolation):
                material.write({'name': False})
                material.flush()

    def test_material_type_invalid_choice(self):
        """Ensure invalid value for selection field material_type raises ValueError."""
        with self.assertRaises(ValueError):
            self.env['material.material'].create({
                'name': 'Invalid Type',
                'code': 'BADTYPE',
                'material_type': 'plastic',
                'buy_price': 150,
                'supplier_id': self.partner.id
            })