# -*- coding: utf-8 -*-
{
    'name': "Material | addons_material",
    'summary': "Manage material data including types, codes, pricing, and suppliers.",
    'description': """
        This module provides basic material management functionality such as:
        - CRUD operations for material records
        - REST API access (secured with JWT)
    """,

    'author': "Arlen Yuda",
    'website': "https://yuuda.vercel.app",
    'license': 'LGPL-3',
    'category': 'Inventory',
    'version': '14.0.1',

    'depends': ["base"],
    "external_dependencies": {
        "python": ["PyJWT","python-dotenv"], # Requires: pip install PyJWT for authenticate REST API
    },

    'data': [
        'security/ir.model.access.csv',      
        'views/material_view.xml',
    ],
    'demo': [
        'demo/demo_data_material.xml',
    ],

    'application': True,
    'installable': True,
}
