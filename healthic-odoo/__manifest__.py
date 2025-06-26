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
    'version': '1.1.1',

    # Dependencias necesarias para el funcionamiento
    'depends': ['base', 'web'],

    # Archivos de datos a cargar
    'data': [
        'security/ir.model.access.csv',
        'data/instrument_method_data.xml',
        'data/instrument_catalog.xml',
        'data/surgery_type_data.xml',
        #'data/surgery_instruments_parto.xml',
        #'data/surgery_instruments_apendisectomia.xml',
        #'data/surgery_instruments_orquidectomia.xml',
        #'data/surgery_instruments_cesarea.xml',
        #'data/surgery_instruments_quistectomia.xml',
        # 'data/surgery_instruments_hernia_inguinal.xml',
        # 'data/surgery_instruments_histerectomia_abdominal.xml',
        # 'data/surgery_instruments_rafi_de_tobillo.xml',
        # 'data/surgery_instruments_rafi.xml',
        # 'data/surgery_instruments_puncion_lumbar.xml',
        # 'data/surgery_instruments_fx_mandibula.xml',
        # 'data/surgery_instruments_cerclaje.xml',
        # 'data/surgery_instruments_manga_gastrica_1.xml',
        # 'data/surgery_instruments_manga_gastrica_2.xml',
        # 'data/surgery_instruments_reduccionn_abierta_de_ostesintesis.xml',
        # 'data/surgery_instruments_histerecromia_abdominal.xml',
        # 'data/surgery_instruments_rtup.xml',
        # 'data/surgery_instruments_lape.xml',
        # 'data/surgery_instruments_legrado.xml',
        # 'data/surgery_instruments_fluro_en_vena.xml',
        # 'data/surgery_instruments_fractura_nasal.xml',
        # 'data/surgery_instruments_manga_gastrica.xml',
        # 'data/surgery_instruments_artroscopia_de_rodilla.xml',
        # 'data/surgery_instruments_sinustomia.xml',
        # 'data/surgery_instruments_colocacion_de_cateter_jj.xml',
        # 'data/surgery_instruments_nefropieloscopia.xml',
        # 'data/surgery_instruments_histerectomia.xml',
        # 'data/surgery_instruments_colesistectonmia_por_laparoscopia.xml',
        # 'data/surgery_instruments_colocacion_cateter_jj.xml',
        # 'data/surgery_instruments_laparoscopia_diagnostica.xml',
        # 'data/surgery_instruments_colesietctomia_por_laparoscopia.xml',
        # 'data/surgery_instruments_by_pass_gastrico.xml',
        # 'data/surgery_instruments_drenaje_abceso.xml',
        # 'data/surgery_instruments_artroscopia.xml',
        # 'data/surgery_instruments_laparoscopia_exploratoria.xml',
        # 'data/surgery_instruments_ameu.xml',
        # 'data/surgery_instruments_apendisectomia_por_laaproscopia.xml',
        # 'data/surgery_instruments_safenoablacion.xml',
        # 'data/surgery_instruments_vambio_de_vac.xml',
        # 'data/surgery_instruments_cistoscopia.xml',
        # 'data/surgery_instruments_retiro_de_implante.xml',
        # 'data/surgery_instruments_hemitireidectomia.xml',
        # 'data/surgery_instruments_discoidectomia_por_endoscopia.xml',
        # 'data/surgery_instruments_manga_gastrica_3.xml',
        # 'data/surgery_instruments_manga_gastrica_4.xml',
        # 'data/surgery_instruments_extraccion.xml',
        # 'data/surgery_instruments_cateter.xml',
        # 'data/surgery_instruments_miomectomia_por_laparoscopia.xml',
        # 'data/surgery_instruments_colonoscopia.xml',
        # 'data/surgery_instruments_retiro_de_cateter_jj.xml',
        # 'data/surgery_instruments_laparatomia_exploratoria.xml',
        'views/hospital_client_views.xml',
        'views/instrument_catalog_views.xml',
        'views/instrument_method_views.xml',
        'views/surgery_type_views.xml',
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

