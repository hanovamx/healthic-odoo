# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


# ============================================================================
# CATÁLOGO DE INSTRUMENTAL MÉDICO
# ============================================================================
# Este modelo es el "maestro" de todos los instrumentos y materiales médicos
# que pueden ser procesados en el sistema. Cada instrumento en este catálogo
# puede aparecer en múltiples órdenes de procesamiento.
#
# FUNCIONES PRINCIPALES:
# - Definir instrumentos y materiales disponibles para procesamiento
# - Configurar métodos de lavado y esterilización permitidos por instrumento
# - Establecer equivalencias STU para facturación
# - Mantener información técnica y de manejo de cada instrumento
#
# RELACIONES:
# - InstrumentCatalog (1) ←→ (N) InstrumentOrderLine (N) ←→ (1) InstrumentOrder
# - Un instrumento del catálogo puede aparecer en múltiples líneas de orden
# - Cada línea de orden referencia un instrumento específico del catálogo
# ============================================================================
class InstrumentCatalog(models.Model):
    _name = 'instrument.catalog'
    _description = 'Catálogo de Instrumental Médico'
    _order = 'tipo_material, name'  # Ordenar por tipo y luego por nombre

    # ============================================================================
    # INFORMACIÓN BÁSICA DEL INSTRUMENTO
    # ============================================================================
    # Estos campos definen la identidad básica del instrumento en el sistema.
    # ============================================================================
    
    name = fields.Char(
        string='Nombre del Instrumento/Material',
        required=True,  # Campo obligatorio
        help='Nombre específico del instrumento o material médico'
    )
    
    tipo_material = fields.Selection([
        ('desechable', 'Desechable'),
        ('instrumental', 'Instrumental'),
        ('textil', 'Textil'),
        ('consumible', 'Consumible')
    ], string='Tipo de Material', required=True)
    
    # ============================================================================
    # MÉTODOS PERMITIDOS - CONFIGURACIÓN DE SEGURIDAD
    # ============================================================================
    # Estos campos definen qué métodos de lavado y esterilización se pueden
    # aplicar a cada instrumento. Son fundamentales para la seguridad y
    # el correcto procesamiento del instrumental médico.
    #
    # IMPORTANTE: Estos campos se usan para validar que no se apliquen
    # métodos incompatibles o dañinos al instrumento durante el procesamiento.
    # ============================================================================
    
    # Métodos de lavado permitidos para este instrumento
    lavado_permitido_ids = fields.Many2many(
        'instrument.method',           # Modelo de métodos
        'catalog_lavado_method_rel',   # Tabla intermedia para la relación
        'catalog_id',                  # Campo en la tabla intermedia que apunta al catálogo
        'method_id',                   # Campo en la tabla intermedia que apunta al método
        string='Métodos de Lavado Permitidos',
        domain=[('tipo', '=', 'lavado')],  # Solo mostrar métodos de tipo 'lavado'
        help='Métodos de lavado que se pueden aplicar a este instrumento de forma segura'
    )
    
    # Métodos de esterilización permitidos para este instrumento
    esterilizacion_permitida_ids = fields.Many2many(
        'instrument.method',                    # Modelo de métodos
        'catalog_esterilizacion_method_rel',    # Tabla intermedia para la relación
        'catalog_id',                           # Campo en la tabla intermedia que apunta al catálogo
        'method_id',                            # Campo en la tabla intermedia que apunta al método
        string='Métodos de Esterilización Permitidos',
        domain=[('tipo', '=', 'esterilizacion')],  # Solo mostrar métodos de tipo 'esterilización'
        help='Métodos de esterilización que se pueden aplicar a este instrumento de forma segura'
    )
    
    # ============================================================================
    # CAMPOS PARA FACTURACIÓN Y CONTROL DE COSTOS
    # ============================================================================
    # Estos campos son fundamentales para el cálculo de costos y la facturación
    # del procesamiento de instrumental médico.
    # ============================================================================
    
    # Equivalencia en unidades de esterilización (STU)
    # Este valor se usa para calcular el costo de procesamiento
    equivalente_stu = fields.Float(
        string='Equivalencia en STU',
        digits=(10, 4),  # Precisión decimal para cálculos de facturación
        help='Unidades de esterilización equivalentes para facturación. '
             'Este valor se multiplica por la cantidad procesada para calcular el STU total.'
    )
    
    # Cantidad estándar del instrumento
    # Se usa como valor por defecto cuando se agrega el instrumento a una orden
    cantidad_estandar = fields.Integer(
        string='Cantidad Estándar',
        default=1,  # Valor por defecto
        help='Cantidad por paquete o juego estándar. '
             'Se usa como valor por defecto cuando se agrega este instrumento a una orden.'
    )
    
    # Campos adicionales útiles
    active = fields.Boolean(string='Activo', default=True)
    
    codigo = fields.Char(
        string='Código',
        help='Código interno del instrumento'
    )
    
    numero_dispositivo = fields.Char(
        string='No. de Dispositivo',
        help='Número único de dispositivo asignado por Healthic'
    )
    
    id_healthic = fields.Char(
        string='ID Healthic',
        help='Identificador único de Healthic para trazabilidad individual',
        copy=False
    )
    
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada del instrumento'
    )
    
    peso_aprox = fields.Float(
        string='Peso Aproximado (gr)',
        help='Peso aproximado en gramos'
    )
    
    requiere_empaque_especial = fields.Boolean(
        string='Requiere Empaque Especial',
        default=False,
        help='Indica si requiere un empaque específico'
    )
    
    observaciones = fields.Text(
        string='Observaciones',
        help='Observaciones especiales para el manejo del instrumento'
    )
    
    # ============================================================================
    # CAMPOS COMPUTADOS - ESTADÍSTICAS DE USO
    # ============================================================================
    # Estos campos calculan automáticamente estadísticas útiles sobre el uso
    # de cada instrumento en el sistema.
    # ============================================================================
    
    # Contador de veces que se ha utilizado este instrumento
    uso_count = fields.Integer(
        string='Veces Utilizado',
        compute='_compute_uso_count',  # Método que calcula el valor
        store=True,                    # Se guarda en BD para mejor rendimiento
        help='Número de veces que este instrumento ha sido procesado en órdenes'
    )
    
    # ============================================================================
    # MÉTODOS COMPUTADOS
    # ============================================================================
    
    @api.depends('name')
    def _compute_uso_count(self):
        """Calcular cuántas veces se ha utilizado este instrumento"""
        for instrument in self:
            # Contar cuántas líneas de orden usan este instrumento
            # Esto nos da el número total de veces que se ha procesado
            instrument.uso_count = self.env['instrument.order.line'].search_count([
                ('instrumento_id', '=', instrument.id)
            ])
    
    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            name = record.name
            if record.numero_dispositivo:
                name = f"[{record.numero_dispositivo}] {name}"
            elif record.codigo:
                name = f"[{record.codigo}] {name}"
            if record.tipo_material:
                tipo_dict = dict(record._fields['tipo_material'].selection)
                name += f" ({tipo_dict[record.tipo_material]})"
            result.append((record.id, name))
        return result
    
    @api.constrains('equivalente_stu')
    def _check_equivalente_stu(self):
        """Validar que la equivalencia STU sea positiva"""
        for record in self:
            if record.equivalente_stu and record.equivalente_stu <= 0:
                raise exceptions.ValidationError(
                    "La equivalencia STU debe ser un valor positivo"
                )
    
    @api.constrains('cantidad_estandar')
    def _check_cantidad_estandar(self):
        """Validar que la cantidad estándar sea positiva"""
        for record in self:
            if record.cantidad_estandar <= 0:
                raise exceptions.ValidationError(
                    "La cantidad estándar debe ser un valor positivo"
                ) 