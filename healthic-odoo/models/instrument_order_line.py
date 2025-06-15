# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class InstrumentOrderLine(models.Model):
    _name = 'instrument.order.line'
    _description = 'Línea de Detalle de Orden de Instrumental'
    _order = 'orden_id, id'

    # Relación con la orden principal
    orden_id = fields.Many2one(
        'instrument.order',
        string='Orden',
        required=True,
        ondelete='cascade',
        help='Orden a la que pertenece esta línea'
    )
    
    # Instrumento utilizado
    instrumento_id = fields.Many2one(
        'instrument.catalog',
        string='Instrumento/Material',
        required=True,
        help='Instrumento o material procesado'
    )
    
    # Estado de entrega
    estado_entrega = fields.Selection([
        ('completo', 'Completo'),
        ('faltante', 'Faltante'),
        ('deteriorado', 'Deteriorado')
    ], string='Estado de Entrega', default='completo', required=True)
    
    # Fechas específicas del elemento
    fecha_entrada = fields.Datetime(
        string='Fecha de Entrada',
        help='Fecha de ingreso individual del instrumento'
    )
    
    fecha_salida = fields.Datetime(
        string='Fecha de Salida',
        help='Fecha de salida individual del instrumento'
    )
    
    # Información específica del procedimiento
    procedimiento_realizado = fields.Char(
        string='Procedimiento Realizado',
        help='Detalle específico del procedimiento o cirugía'
    )
    
    medico_responsable = fields.Char(
        string='Médico Responsable',
        help='Nombre del médico responsable del procedimiento'
    )
    
    # Métodos aplicados
    lavado_aplicado = fields.Many2one(
        'instrument.method',
        string='Método de Lavado Aplicado',
        domain=[('tipo', '=', 'lavado')],
        help='Método de lavado utilizado para este instrumento'
    )
    
    esterilizacion_aplicada = fields.Many2one(
        'instrument.method',
        string='Método de Esterilización Aplicado',
        domain=[('tipo', '=', 'esterilizacion')],
        help='Método de esterilización utilizado para este instrumento'
    )
    
    # Información del turno
    turno = fields.Selection([
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('nocturno', 'Nocturno')
    ], string='Turno', help='Turno en el que se procesó el instrumento')
    
    # Estado del cincho verde (indicador de esterilización)
    cincho_verde = fields.Selection([
        ('si', 'Sí'),
        ('no', 'No'),
        ('na', 'No Aplica')
    ], string='Cincho Verde', default='na', help='Indicador de esterilización válida')
    
    # Cantidad procesada
    cantidad = fields.Integer(
        string='Cantidad',
        default=1,
        help='Cantidad de unidades procesadas'
    )
    
    # Observaciones específicas
    observaciones = fields.Text(
        string='Observaciones',
        help='Observaciones específicas para este instrumento'
    )
    
    # Campos computados
    stu_calculado = fields.Float(
        string='STU Calculado',
        compute='_compute_stu_calculado',
        store=True,
        digits=(10, 4),
        help='STU calculado basado en la cantidad y equivalencia'
    )
    
    duracion_individual = fields.Float(
        string='Duración Individual (horas)',
        compute='_compute_duracion_individual',
        store=True,
        help='Duración del procesamiento individual'
    )
    
    # Campos relacionados para facilitar búsquedas
    cliente_id = fields.Many2one(
        related='orden_id.cliente_id',
        string='Cliente',
        store=True,
        readonly=True
    )
    
    estado_orden = fields.Selection(
        related='orden_id.estado',
        string='Estado de la Orden',
        store=True,
        readonly=True
    )
    
    tipo_material = fields.Selection(
        related='instrumento_id.tipo_material',
        string='Tipo de Material',
        store=True,
        readonly=True
    )
    
    # Validaciones de métodos permitidos
    lavado_permitido_ids = fields.Many2many(
        related='instrumento_id.lavado_permitido_ids',
        string='Métodos de Lavado Permitidos',
        readonly=True
    )
    
    esterilizacion_permitida_ids = fields.Many2many(
        related='instrumento_id.esterilizacion_permitida_ids',
        string='Métodos de Esterilización Permitidos',
        readonly=True
    )
    
    @api.depends('instrumento_id', 'cantidad')
    def _compute_stu_calculado(self):
        """Calcular STU basado en la cantidad y equivalencia del instrumento"""
        for line in self:
            if line.instrumento_id and line.instrumento_id.equivalente_stu:
                line.stu_calculado = line.cantidad * line.instrumento_id.equivalente_stu
            else:
                line.stu_calculado = 0
    
    @api.depends('fecha_entrada', 'fecha_salida')
    def _compute_duracion_individual(self):
        """Calcular la duración individual del procesamiento"""
        for line in self:
            if line.fecha_entrada and line.fecha_salida:
                delta = line.fecha_salida - line.fecha_entrada
                line.duracion_individual = delta.total_seconds() / 3600
            else:
                line.duracion_individual = 0
    
    @api.onchange('instrumento_id')
    def _onchange_instrumento_id(self):
        """Limpiar métodos si no son compatibles con el nuevo instrumento"""
        if self.instrumento_id:
            # Limpiar método de lavado si no es compatible
            if (self.lavado_aplicado and 
                self.instrumento_id.lavado_permitido_ids and 
                self.lavado_aplicado not in self.instrumento_id.lavado_permitido_ids):
                self.lavado_aplicado = False
            
            # Limpiar método de esterilización si no es compatible  
            if (self.esterilizacion_aplicada and
                self.instrumento_id.esterilizacion_permitida_ids and
                self.esterilizacion_aplicada not in self.instrumento_id.esterilizacion_permitida_ids):
                self.esterilizacion_aplicada = False
    
    @api.constrains('lavado_aplicado', 'instrumento_id')
    def _check_lavado_permitido(self):
        """Validar que el método de lavado sea compatible con el instrumento"""
        for line in self:
            if (line.lavado_aplicado and 
                line.instrumento_id and 
                line.instrumento_id.lavado_permitido_ids and
                line.lavado_aplicado not in line.instrumento_id.lavado_permitido_ids):
                raise exceptions.ValidationError(
                    f"El método de lavado '{line.lavado_aplicado.name}' no es compatible "
                    f"con el instrumento '{line.instrumento_id.name}'"
                )
    
    @api.constrains('esterilizacion_aplicada', 'instrumento_id')
    def _check_esterilizacion_permitida(self):
        """Validar que el método de esterilización sea compatible con el instrumento"""
        for line in self:
            if (line.esterilizacion_aplicada and
                line.instrumento_id and
                line.instrumento_id.esterilizacion_permitida_ids and
                line.esterilizacion_aplicada not in line.instrumento_id.esterilizacion_permitida_ids):
                raise exceptions.ValidationError(
                    f"El método de esterilización '{line.esterilizacion_aplicada.name}' no es compatible "
                    f"con el instrumento '{line.instrumento_id.name}'"
                )
    
    @api.constrains('fecha_entrada', 'fecha_salida')
    def _check_fechas_individuales(self):
        """Validar que las fechas individuales tengan sentido cronológico"""
        for line in self:
            if line.fecha_entrada and line.fecha_salida:
                if line.fecha_salida <= line.fecha_entrada:
                    raise exceptions.ValidationError(
                        "La fecha de salida debe ser posterior a la fecha de entrada"
                    )
    
    @api.constrains('cantidad')
    def _check_cantidad(self):
        """Validar que la cantidad sea positiva"""
        for line in self:
            if line.cantidad <= 0:
                raise exceptions.ValidationError(
                    "La cantidad debe ser un valor positivo"
                )
    
    def name_get(self):
        """Personalizar el nombre mostrado en la línea"""
        result = []
        for line in self:
            name = f"{line.orden_id.name} - {line.instrumento_id.name}"
            if line.cantidad > 1:
                name += f" (x{line.cantidad})"
            result.append((line.id, name))
        return result 