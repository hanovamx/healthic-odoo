# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class InstrumentCatalog(models.Model):
    _name = 'instrument.catalog'
    _description = 'Catálogo de Instrumental Médico'
    _order = 'tipo_material, name'

    name = fields.Char(
        string='Nombre del Instrumento/Material',
        required=True,
        help='Nombre específico del instrumento o material médico'
    )
    
    tipo_material = fields.Selection([
        ('desechable', 'Desechable'),
        ('instrumental', 'Instrumental'),
        ('textil', 'Textil'),
        ('consumible', 'Consumible')
    ], string='Tipo de Material', required=True)
    
    # Relaciones many2many con métodos permitidos
    lavado_permitido_ids = fields.Many2many(
        'instrument.method',
        'catalog_lavado_method_rel',
        'catalog_id',
        'method_id',
        string='Métodos de Lavado Permitidos',
        domain=[('tipo', '=', 'lavado')],
        help='Métodos de lavado aplicables a este instrumento'
    )
    
    esterilizacion_permitida_ids = fields.Many2many(
        'instrument.method',
        'catalog_esterilizacion_method_rel', 
        'catalog_id',
        'method_id',
        string='Métodos de Esterilización Permitidos',
        domain=[('tipo', '=', 'esterilizacion')],
        help='Métodos de esterilización aplicables a este instrumento'
    )
    
    # Campos específicos para facturación
    equivalente_stu = fields.Float(
        string='Equivalencia en STU',
        digits=(10, 4),
        help='Unidades de esterilización equivalentes para facturación'
    )
    
    cantidad_estandar = fields.Integer(
        string='Cantidad Estándar',
        default=1,
        help='Cantidad por paquete o juego estándar'
    )
    
    # Campos adicionales útiles
    active = fields.Boolean(string='Activo', default=True)
    
    codigo = fields.Char(
        string='Código',
        help='Código interno del instrumento'
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
    
    # Campos computados para estadísticas
    uso_count = fields.Integer(
        string='Veces Utilizado',
        compute='_compute_uso_count',
        store=True
    )
    
    @api.depends('name')
    def _compute_uso_count(self):
        """Calcular cuántas veces se ha utilizado este instrumento"""
        for instrument in self:
            instrument.uso_count = self.env['instrument.order.line'].search_count([
                ('instrumento_id', '=', instrument.id)
            ])
    
    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            name = record.name
            if record.codigo:
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