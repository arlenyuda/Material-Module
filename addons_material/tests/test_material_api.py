from odoo.tests import HttpCase
from odoo.tests.common import tagged
import json

@tagged('post_install', '-at_install')
class TestMaterialAPI(HttpCase):
    def login(self, username, password):
        """Helper method to simulate login and return token or error response."""
        response = self.url_open(
            '/api/login',
            data=json.dumps({
                'params': {
                    'username': username,
                    'password': password
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        result = json.loads(data['result']) if isinstance(data['result'], str) else data['result']
        return result

    def test_login_success(self):
        """Should return token and status 200 for valid login credentials."""
        login = self.login('admin', 'admin')
        self.assertIn('token', login)
        self.assertEqual(login['status'], 200)

    def test_login_fail(self):
        """Should return error and status 400 for invalid credentials."""
        login = self.login('admin', 'wrongpassword')
        self.assertIn('error', login)
        self.assertEqual(login['status'], 400)

    def test_login_missing_username(self):
        """Should return error when username is missing."""
        response = self.url_open(
            '/api/login',
            data=json.dumps({'params': {'password': 'admin'}}),
            headers={'Content-Type': 'application/json'},
        )
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('error_message', data['result'])

    def test_login_missing_password(self):
        """Should return error when password is missing."""
        response = self.url_open(
            '/api/login',
            data=json.dumps({'params': {'username': 'admin'}}),
            headers={'Content-Type': 'application/json'},
        )
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('error_message', data['result'])

    def test_login_missing_both(self):
        """Should return error when both username and password are missing."""
        response = self.url_open(
            '/api/login',
            data=json.dumps({'params': {}}),
            headers={'Content-Type': 'application/json'},
        )
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('error_message', data['result'])

    def test_access_materials_with_token(self):
        """Should allow access to /materials when a valid token is provided."""
        login = self.login('admin', 'admin')
        token = login['token']
        response = self.url_open('/api/materials', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('data', data)
        self.assertEqual(data['status'], 200)

    def test_access_materials_without_token(self):
        """Should return 401 when accessing /materials without token."""
        response = self.url_open('/api/materials', headers={})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.text)
        self.assertIn('error', data)

    def test_access_materials_filter_type_with_token(self):
        """Should return filtered materials by type when token is valid."""
        login = self.login('admin', 'admin')
        token = login['token']
        response = self.url_open('/api/materials/type/fabric', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('data', data)
        self.assertEqual(data['status'], 200)

    def test_access_materials_filter_type_without_token(self):
        """Should return 401 when accessing material type filter without token."""
        response = self.url_open('/api/materials/type/fabric', headers={})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.text)
        self.assertIn('error', data)

    def test_create_material(self):
        """Should successfully create material with valid data and token."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        params = {
            "params": {
                "name": "Test Material",
                "code": "TEST123",
                "material_type": "cotton",
                "buy_price": 1000.0,
                "supplier_id": supplier
            }
        }
        response = self.url_open(
            '/api/materials/create',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertIn('id', data['result'])
        self.assertEqual(data['result']['status'], 201)

    def test_create_material_missing_fields(self):
        """Should return 400 if required fields are missing in material creation."""
        login = self.login('admin', 'admin')
        token = login['token']
        params = {
            "params": {
                "code": "TEST123",
                "material_type": "cotton",
                "buy_price": 1000.0,
            }
        }
        response = self.url_open(
            '/api/materials/create',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('Missing fields', data['result']['error'])

    def test_update_material(self):
        """Should update material data if ID exists and token is valid."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        material = self.env['material.material'].sudo().create({
            "name": "Before Update",
            "code": "UPD001",
            "material_type": "jeans",
            "buy_price": 1500,
            "supplier_id": supplier
        })
        updated_data = {"params": {"name": "After Update", "buy_price": 2000}}
        response = self.url_open(
            f'/api/materials/update/{material.id}',
            data=json.dumps(updated_data),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 200)

    def test_update_material_not_found(self):
        """Should return 404 if material ID not found during update."""
        login = self.login('admin', 'admin')
        token = login['token']
        updated_data = {"params": {"name": "Invalid Update"}}
        response = self.url_open(
            '/api/materials/update/999999',
            data=json.dumps(updated_data),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertEqual(data['result']['status'], 404)

    def test_delete_material(self):
        """Should delete material successfully with valid token."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        material = self.env['material.material'].sudo().create({
            "name": "To Be Deleted",
            "code": "DEL001",
            "material_type": "fabric",
            "buy_price": 500,
            "supplier_id": supplier
        })
        response = self.url_open(
            f'/api/materials/delete/{material.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('data', data)
        self.assertEqual(data['status'], 200)
        self.assertFalse(material.exists())

    def test_delete_material_not_found(self):
        """Should return 404 if material to delete is not found."""
        login = self.login('admin', 'admin')
        token = login['token']
        response = self.url_open(
            '/api/materials/delete/999999',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.text)
        self.assertIn('Material not found', data['error'])

    def test_create_material_duplicate_code_not_allowed(self):
        """Should return 409 if material code already exists on creation."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        self.env['material.material'].sudo().create({
            "name": "Original Material",
            "code": "DUPLICATE",
            "material_type": "cotton",
            "buy_price": 120,
            "supplier_id": supplier
        })
        params = {
            "params": {
                "name": "Another Material",
                "code": "DUPLICATE",
                "material_type": "cotton",
                "buy_price": 130,
                "supplier_id": supplier
            }
        }
        response = self.url_open(
            '/api/materials/create',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 409)
        self.assertIn('error', data['result'])

    def test_update_material_duplicate_code_not_allowed(self):
        """Should return 409 if code is duplicated on material update."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        material1 = self.env['material.material'].sudo().create({
            "name": "Material One",
            "code": "CODE1",
            "material_type": "cotton",
            "buy_price": 120,
            "supplier_id": supplier
        })
        material2 = self.env['material.material'].sudo().create({
            "name": "Material Two",
            "code": "CODE2",
            "material_type": "cotton",
            "buy_price": 130,
            "supplier_id": supplier
        })
        params = {"params": {"id": material2.id, "code": "CODE1"}}
        response = self.url_open(
            f'/api/materials/update/{material2.id}',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 409)
        self.assertIn('error', data['result'])

    def test_create_materials_buy_price_too_low_not_allowed(self):
        """Should return error if buy_price < 100 on material creation."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        params = {
            "params": {
                "name": "Too Cheap Material",
                "code": "TOOCHEAP",
                "material_type": "cotton",
                "buy_price": 50,
                "supplier_id": supplier
            }
        }
        response = self.url_open(
            '/api/materials/create',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('error', data['result'])

    def test_update_material_buy_price_too_low_not_allowed(self):
        """Should return error if buy_price < 100 during material update."""
        login = self.login('admin', 'admin')
        token = login['token']
        supplier = login['user']
        material = self.env['material.material'].sudo().create({
            "name": "Normal Material",
            "code": "NORMAL",
            "material_type": "cotton",
            "buy_price": 120,
            "supplier_id": supplier
        })
        params = {"params": {"id": material.id, "buy_price": 50}}
        response = self.url_open(
            f'/api/materials/update/{material.id}',
            data=json.dumps(params),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.text)
        self.assertIn('result', data)
        self.assertEqual(data['result']['status'], 400)
        self.assertIn('error', data['result'])