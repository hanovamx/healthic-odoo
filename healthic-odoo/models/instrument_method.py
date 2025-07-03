# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class InstrumentMethod(models.Model):
    _name = 'instrument.method'
    _description = 'Método de Lavado y Esterilización'
    _order = 'tipo, name'

    name = fields.Char(
        string='Nombre del Método',
        required=True,
        help='Nombre del método (ej. Lavadora, Peróxido, Autoclave)'
    )
    
    tipo = fields.Selection([
        ('lavado', 'Lavado'),
        ('esterilizacion', 'Esterilización')
    ], string='Tipo', required=True)
    
    # Campos adicionales para configuración
    active = fields.Boolean(string='Activo', default=True)
    
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada del método y sus características'
    )
    
    temperatura_min = fields.Float(
        string='Temperatura Mínima (°C)',
        help='Temperatura mínima requerida para este método'
    )
    
    temperatura_max = fields.Float(
        string='Temperatura Máxima (°C)', 
        help='Temperatura máxima permitida para este método'
    )
    
    tiempo_proceso = fields.Integer(
        string='Tiempo de Proceso (min)',
        help='Tiempo estándar del proceso en minutos'
    )
    
    requiere_secado = fields.Boolean(
        string='Requiere Secado',
        default=False,
        help='Indica si este método requiere un proceso de secado adicional'
    )
    
    # Tipos de ciclo para esterilización
    tipo_ciclo = fields.Selection([
        ('rapido', 'Ciclo Rápido'),
        ('estandar', 'Ciclo Estándar'),
        ('textil', 'Ciclo Textil'),
        ('instrumental', 'Ciclo Instrumental'),
        ('contenedores', 'Ciclo Contenedores'),
        ('implantes', 'Ciclo Implantes')
    ], string='Tipo de Ciclo', help='Tipo de ciclo de esterilización')
    
    tipo_carga = fields.Selection([
        ('solida', 'Carga Sólida'),
        ('porosa', 'Carga Porosa'),
        ('liquida', 'Carga Líquida'),
        ('mixta', 'Carga Mixta')
    ], string='Tipo de Carga', help='Tipo de carga para la que está diseñado este ciclo')
    
    # Estadísticas
    uso_count = fields.Integer(
        string='Veces Utilizado',
        compute='_compute_uso_count'
    )
    
    @api.depends('name')
    def _compute_uso_count(self):
        """Calcular cuántas veces se ha utilizado este método"""
        for method in self:
            lavado_count = self.env['instrument.order.line'].search_count([
                ('lavado_aplicado', '=', method.id)
            ])
            esterilizacion_count = self.env['instrument.order.line'].search_count([
                ('esterilizacion_aplicada', '=', method.id)
            ])
            method.uso_count = lavado_count + esterilizacion_count
    
    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            tipo_dict = dict(record._fields['tipo'].selection)
            name = f"{record.name} ({tipo_dict[record.tipo]})"
            result.append((record.id, name))
        return result
    
    @api.constrains('temperatura_min', 'temperatura_max')
    def _check_temperaturas(self):
        """Validar que la temperatura mínima sea menor que la máxima"""
        for record in self:
            if record.temperatura_min and record.temperatura_max:
                if record.temperatura_min >= record.temperatura_max:
                    raise exceptions.ValidationError(
                        "La temperatura mínima debe ser menor que la temperatura máxima"
                    ) 