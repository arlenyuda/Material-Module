from odoo import http
from odoo.http import request, Response
from odoo.addons.addons_material.controllers.jwt_helper import jwt_required, generate_jwt
from odoo.exceptions import AccessDenied
from psycopg2 import IntegrityError
import json
import logging

_logger = logging.getLogger(__name__)

class MaterialController(http.Controller):

    @http.route('/api/login', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def login(self, username=None, password=None):
        if not username or not password:
            return {
                'error': 'error_login',
                'error_message': 'Username and password are required',
                'status': 400
            }

        user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)
        if not user:
            return {
                'error': 'error_login',
                'error_message': 'Invalid username or password',
                'status': 400
            }

        db = request.env.cr.dbname or request.session.get('db')
        if not db:
            return {
                'error': 'error_login',
                'error_message': 'Invalid database',
                'status': 400
            }

        try:
            request.session.authenticate(db, username, password)
        
        except AccessDenied as e:
            request.env.cr.rollback()
            return {
                'error': 'error_login',
                'error_message': 'Invalid username or password',
                'status': 400
            }

        token = generate_jwt(user.id)
        return {
            'user': user.partner_id.id if user.partner_id else user.id,
            'token': token,
            'status': 200
        }

    @http.route('/api/materials', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    @jwt_required
    def get_all_materials(self, **kwargs):
        materials = request.env['material.material'].sudo().search_read([], ['name', 'code', 'material_type', 'buy_price', 'supplier_id'])
        return Response(
            json.dumps({'status': 200, 'data': materials}),
            status=200,
            content_type='application/json'
        )

    @http.route('/api/materials/type/<string:material_type>', type='http', auth='none', cors='*', methods=['GET'], csrf=False)
    @jwt_required
    def get_all_materials_filter_type(self, material_type=None, **kwargs):
        if material_type.lower() not in ['fabric', 'jeans', 'cotton']:
            return Response(
                json.dumps({'status': 400, 'error': 'Invalid material type'}),
                status=400,
                content_type='application/json'
            )
        materials = request.env['material.material'].sudo().search_read(
            [('material_type', '=', material_type)], ['name', 'code', 'material_type', 'buy_price', 'supplier_id'])
        return Response(
            json.dumps({'status': 200, 'data': materials}),
            status=200,
            content_type='application/json'
        )

    @http.route('/api/materials/create', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    @jwt_required
    def create_material(self, **kwargs):
        required_fields = ['name', 'code', 'material_type', 'buy_price', 'supplier_id']
        missing = [f for f in required_fields if not kwargs.get(f)]

        if missing:
            return {'status': 400, 'error': f'Missing fields: {", ".join(missing)}'}

        code = kwargs.get('code', False)
        if code:
            existing = request.env['material.material'].sudo().search([('code', '=', code)], limit=1)
            if existing:
                return {'status': 409, 'error': 'Duplicate code. This material code already exists.'}

        buy_price = kwargs.get('buy_price', False)
        if not buy_price or float(buy_price) < 100:
            return {'status': 400, 'error': 'Buy price must be at least 100'}

        try:
            material = request.env['material.material'].sudo().create(kwargs)
            return {'status': 201, 'message': 'Material created successfully', 'id': material.id}

        except Exception as e:
            request.env.cr.rollback()
            return {'status': 500, 'error': str(e)}

    @http.route('/api/materials/update/<int:material_id>', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    @jwt_required
    def update_material(self, material_id, **kwargs):
        material = request.env['material.material'].sudo().browse(material_id)
        if not material.exists():
            return {'status': 404, 'error': 'Material not found'}

        code = kwargs.get('code', False)
        if code:
            existing = request.env['material.material'].sudo().search([('code', '=', code), ('id', '!=', material_id)], limit=1)
            if existing:
                return {'status': 409, 'error': 'Duplicate code. This material code already exists.'}

        buy_price = kwargs.get('buy_price', False)
        if buy_price and float(buy_price) < 100:
            return {'status': 400, 'error': 'Buy price must be at least 100'}

        try:
            material.write(kwargs)
            return {'status': 200, 'message': 'Material updated successfully'}
        
        except Exception as e:
            request.env.cr.rollback()
            return {'status': 500, 'error': str(e)}

    @http.route('/api/materials/delete/<int:material_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    @jwt_required
    def delete_material(self, material_id, **kwargs):
        material = request.env['material.material'].sudo().browse(material_id)
        if not material.exists():
            return Response(
                json.dumps({'status': 404, 'error': "Material not found"}),
                status=404,
                content_type='application/json'
            )
        try:
            material.unlink()
            return Response(
                json.dumps({'status': 200, 'data': "Material deleted successfully"}),
                status=200,
                content_type='application/json'
            )
        
        except Exception as e:
            request.env.cr.rollback()
            return Response(
                json.dumps({'status': 500, 'error': str(e)}),
                status=500,
                content_type='application/json'
            )