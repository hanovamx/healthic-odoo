# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime


class InstrumentOrder(models.Model):
    _name = 'instrument.order'
    _description = 'Orden de Procesamiento de Instrumental'
    _order = 'create_date desc, name desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Número de Orden',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._get_next_sequence()
    )
    
    # Información del cliente y procedimiento
    cliente_id = fields.Many2one(
        'hospital.client',
        string='Cliente Hospitalario',
        required=True,
        help='Hospital o cliente que genera la orden'
    )
    
    numero_cuenta = fields.Char(
        string='Número de Cuenta',
        help='Número de cuenta del paciente'
    )
    
    sala = fields.Char(
        string='Sala Quirúrgica',
        help='Sala donde se realizará el procedimiento'
    )
    
    tipo_cirugia = fields.Char(
        string='Tipo de Cirugía',
        help='Nombre o tipo de cirugía a realizar'
    )
    
    # Fechas del proceso
    fecha_recepcion = fields.Datetime(
        string='Fecha de Recepción',
        required=True,
        default=fields.Datetime.now,
        help='Fecha y hora de entrada del instrumental'
    )
    
    fecha_entrega = fields.Datetime(
        string='Fecha de Entrega',
        help='Fecha y hora de salida del instrumental'
    )
    
    # Estado del instrumental al recibir
    instrumental_humedo = fields.Boolean(
        string='¿Instrumental Húmedo?',
        default=False,
        help='Indica si el instrumental llegó húmedo'
    )
    
    cincho_integro = fields.Selection([
        ('si', 'Sí'),
        ('no', 'No'),
        ('na', 'No Aplica')
    ], string='Cincho Íntegro', default='na')
    
    # Estado de la orden
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_lavado', 'En Lavado'),
        ('empaque', 'En Empaque'),
        ('esterilizado', 'Esterilizado'),
        ('entregado', 'Entregado')
    ], string='Estado', required=True, default='pendiente', tracking=True)
    
    # Responsables del proceso
    responsable_lavado = fields.Many2one(
        'res.users',
        string='Responsable de Lavado',
        help='Usuario responsable del proceso de lavado'
    )
    
    responsable_esterilizacion = fields.Many2one(
        'res.users', 
        string='Responsable de Esterilización',
        help='Usuario responsable del proceso de esterilización'
    )
    
    responsable_descarga = fields.Many2one(
        'res.users',
        string='Responsable de Descarga',
        help='Usuario responsable de la descarga/entrega'
    )
    
    # Relaciones con líneas de detalle
    linea_ids = fields.One2many(
        'instrument.order.line',
        'orden_id',
        string='Líneas de Instrumental',
        help='Detalle de instrumentos en esta orden'
    )
    
    # Evidencias y archivos adjuntos
    evidencia_ids = fields.Many2many(
        'ir.attachment',
        'order_attachment_rel',
        'order_id',
        'attachment_id',
        string='Evidencias',
        help='Archivos adjuntos (imágenes, PDFs) del proceso'
    )
    
    # Observaciones
    observaciones = fields.Text(
        string='Observaciones',
        help='Observaciones generales de la orden'
    )
    
    observaciones_lavado = fields.Text(
        string='Observaciones de Lavado',
        help='Observaciones específicas del proceso de lavado'
    )
    
    observaciones_esterilizacion = fields.Text(
        string='Observaciones de Esterilización',
        help='Observaciones específicas del proceso de esterilización'
    )
    
    fallos_proceso = fields.Text(
        string='Fallos de Proceso',
        help='Registro de fallos o incidencias durante el proceso'
    )
    
    # Campos computados
    total_instrumentos = fields.Integer(
        string='Total de Instrumentos',
        compute='_compute_totales',
        store=True
    )
    
    total_stu = fields.Float(
        string='Total STU',
        compute='_compute_totales',
        store=True,
        digits=(10, 4)
    )
    
    duracion_proceso = fields.Float(
        string='Duración del Proceso (horas)',
        compute='_compute_duracion_proceso',
        store=True
    )
    
    # Estados computados
    puede_iniciar_lavado = fields.Boolean(
        string='Puede Iniciar Lavado',
        compute='_compute_estados_disponibles'
    )
    
    puede_iniciar_empaque = fields.Boolean(
        string='Puede Iniciar Empaque',
        compute='_compute_estados_disponibles'
    )
    
    puede_esterilizar = fields.Boolean(
        string='Puede Esterilizar',
        compute='_compute_estados_disponibles'
    )
    
    puede_entregar = fields.Boolean(
        string='Puede Entregar',
        compute='_compute_estados_disponibles'
    )
    
    # Método para generar secuencia automática
    def _get_next_sequence(self):
        """Generar el siguiente número de secuencia para la orden"""
        last_order = self.search([], order='id desc', limit=1)
        if last_order:
            try:
                last_num = int(last_order.name.split('-')[-1])
                return f"MS2-{last_num + 1:03d}"
            except (ValueError, IndexError):
                pass
        return "MS2-001"
    
    @api.depends('linea_ids', 'linea_ids.instrumento_id')
    def _compute_totales(self):
        """Calcular totales de instrumentos y STU"""
        for order in self:
            order.total_instrumentos = len(order.linea_ids)
            order.total_stu = sum(
                line.instrumento_id.equivalente_stu or 0 
                for line in order.linea_ids
            )
    
    @api.depends('fecha_recepcion', 'fecha_entrega')
    def _compute_duracion_proceso(self):
        """Calcular la duración del proceso en horas"""
        for order in self:
            if order.fecha_recepcion and order.fecha_entrega:
                delta = order.fecha_entrega - order.fecha_recepcion
                order.duracion_proceso = delta.total_seconds() / 3600
            else:
                order.duracion_proceso = 0
    
    @api.depends('estado', 'linea_ids')
    def _compute_estados_disponibles(self):
        """Calcular qué estados están disponibles según las reglas de negocio"""
        for order in self:
            order.puede_iniciar_lavado = order.estado == 'pendiente'
            order.puede_iniciar_empaque = order.estado == 'en_lavado'
            order.puede_esterilizar = order.estado == 'empaque'
            order.puede_entregar = order.estado == 'esterilizado'
    
    # Métodos de transición de estado
    def action_iniciar_lavado(self):
        """Iniciar proceso de lavado"""
        self.ensure_one()
        if not self.puede_iniciar_lavado:
            raise exceptions.UserError("No se puede iniciar el lavado en el estado actual")
        
        self.write({
            'estado': 'en_lavado',
            'responsable_lavado': self.env.user.id
        })
        return True
    
    def action_iniciar_empaque(self):
        """Iniciar proceso de empaque"""
        self.ensure_one()
        if not self.puede_iniciar_empaque:
            raise exceptions.UserError("No se puede iniciar el empaque en el estado actual")
        
        self.write({
            'estado': 'empaque'
        })
        return True
    
    def action_esterilizar(self):
        """Marcar como esterilizado"""
        self.ensure_one()
        if not self.puede_esterilizar:
            raise exceptions.UserError("No se puede esterilizar en el estado actual")
        
        self.write({
            'estado': 'esterilizado',
            'responsable_esterilizacion': self.env.user.id
        })
        return True
    
    def action_entregar(self):
        """Entregar la orden"""
        self.ensure_one()
        if not self.puede_entregar:
            raise exceptions.UserError("No se puede entregar en el estado actual")
        
        self.write({
            'estado': 'entregado',
            'fecha_entrega': fields.Datetime.now(),
            'responsable_descarga': self.env.user.id
        })
        return True
    
    @api.constrains('fecha_recepcion', 'fecha_entrega')
    def _check_fechas(self):
        """Validar que las fechas tengan sentido cronológico"""
        for order in self:
            if order.fecha_entrega and order.fecha_recepcion:
                if order.fecha_entrega <= order.fecha_recepcion:
                    raise exceptions.ValidationError(
                        "La fecha de entrega debe ser posterior a la fecha de recepción"
                    )
    
    @api.constrains('linea_ids')
    def _check_lineas(self):
        """Validar que la orden tenga al menos una línea"""
        for order in self:
            if order.estado != 'pendiente' and not order.linea_ids:
                raise exceptions.ValidationError(
                    "La orden debe tener al menos un instrumento"
                ) 