# -*- coding: utf-8 -*-
{
    'name': "Healthic - Gestión de Instrumental Médico",

    'summary': "Sistema de gestión y trazabilidad de instrumental médico esterilizado",

    'description': """
        Módulo para digitalizar el proceso de recepción, seguimiento, control y entrega 
        de instrumental médico esterilizado, garantizando trazabilidad, cumplimiento 
        normativo y eficiencia operativa.
        
        Funcionalidades principales:
        - Registro de clientes hospitalarios
        - Catálogo de instrumental médico
        - Gestión de órdenes de procesamiento
        - Trazabilidad completa del proceso
        - Soporte para múltiples métodos de lavado y esterilización
    """,

    'author': "Healthic",
    'website': "https://www.healthic.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Healthcare',
    'version': '1.0.0',

    # Dependencias necesarias para el funcionamiento
    'depends': ['base'],

    # Archivos de datos a cargar
    'data': [
        'security/ir.model.access.csv',
        'data/instrument_method_data.xml',
        'views/hospital_client_views.xml',
        'views/instrument_catalog_views.xml',
        'views/instrument_method_views.xml',
        'views/instrument_order_views.xml',
        'views/instrument_order_line_views.xml',
        'views/menus.xml',
    ],
    
    # Datos de demostración
    'demo': [
        'demo/demo_data.xml',
    ],
    
    # Configuración del módulo
    'installable': True,
    'auto_install': False,
    'application': True,
}

