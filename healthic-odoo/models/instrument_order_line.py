# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


# ============================================================================
# LÍNEA DE DETALLE DE ORDEN DE INSTRUMENTAL
# ============================================================================
# Este modelo representa cada instrumento individual dentro de una orden.
# Es el "puente" que conecta una orden con un instrumento específico del catálogo.
#
# ESTRUCTURA DE LA RELACIÓN:
# - InstrumentOrder (1) ←→ (N) InstrumentOrderLine (N) ←→ (1) InstrumentCatalog
# - Cada línea representa un instrumento específico que será procesado
# - Una orden puede tener múltiples líneas (múltiples instrumentos)
# - Un instrumento puede aparecer en múltiples órdenes (múltiples líneas)
#
# FUNCIONES PRINCIPALES:
# - Almacenar información específica del procesamiento de cada instrumento
# - Mantener el estado individual de cada instrumento en la orden
# - Permitir diferentes métodos de lavado/esterilización por instrumento
# - Calcular STU individual para facturación
# ============================================================================
class InstrumentOrderLine(models.Model):
    _name = 'instrument.order.line'
    _description = 'Línea de Detalle de Orden de Instrumental'
    _order = 'orden_id, id'  # Ordenar por orden y luego por ID
    _active_name = 'active'  # Campo para archivar en lugar de eliminar

    active = fields.Boolean(string='Activo', default=True, help='Indica si el registro está activo')

    # ============================================================================
    # RELACIONES PRINCIPALES
    # ============================================================================
    # Estas son las dos relaciones más importantes que definen la estructura
    # de datos del módulo.
    # ============================================================================
    
    # Relación con la orden principal (Many2one)
    # Cada línea pertenece a una orden específica
    orden_id = fields.Many2one(
        'instrument.order',  # Modelo de la orden
        string='Orden',
        required=True,       # Campo obligatorio
        ondelete='cascade',  # Si se elimina la orden, se eliminan todas sus líneas
        help='Orden a la que pertenece esta línea'
    )
    
    # Relación con el instrumento del catálogo (Many2one)
    # Cada línea representa un instrumento específico del catálogo
    instrumento_id = fields.Many2one(
        'instrument.catalog',  # Modelo del catálogo de instrumentos
        string='Instrumento/Material',
        required=True,         # Campo obligatorio
        help='Instrumento o material procesado. Viene del catálogo de instrumentos.'
    )
    
    # Estado de entrega
    estado_entrega = fields.Selection([
        ('completo', 'Completo'),
        ('faltante', 'Faltante'),
        ('deteriorado', 'Deteriorado')
    ], string='Estado de Entrega', default='completo', help='Estado de entrega del instrumento')
    
    estado_entrega_area_negra = fields.Selection([
        ('completo', 'Completo'),
        ('faltante', 'Faltante'),
        ('deteriorado', 'Deteriorado')
    ], string='Estado en Área Negra', help='Estado del instrumental en área negra')
    
    estado_entrega_area_blanca = fields.Selection([
        ('completo', 'Completo'),
        ('faltante', 'Faltante'),
        ('deteriorado', 'Deteriorado')
    ], string='Estado en Área Blanca', help='Estado del instrumental en área blanca')
    
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
    
    # Cambiar de Many2many a Selection
    lavado_metodo = fields.Selection([
        ('manual', 'Manual'),
        ('ultrasonico', 'Ultrasónico'),
        ('termodinamico', 'Termodinámico')
    ], string='Método de Lavado')
    
    esterilizacion_metodo = fields.Selection([
        ('alta_vapor', 'Alta Vapor'),
        ('baja_peroxido', 'Baja Peróxido'),
        ('baja_peroxido_eto', 'Baja Peróxido ETO')
    ], string='Método de Esterilización')
    
    # Eliminar referencias y lógica de métodos antiguos y relaciones Many2many
    
    # Información del turno
    responsable_empaquetado = fields.Many2one(
        'res.users',
        string='Responsable de Empaquetado',
        help='Usuario responsable del empaquetado'
    )
    
    turno_empaquetado = fields.Selection([
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('nocturno', 'Nocturno')
    ], string='Turno de Empaquetado', help='Turno en que se realizó el empaquetado')
    
    tipo_empaquetado = fields.Selection([
        ('grado_medico', 'Grado Médico (Tyvek/GMM)'),
        ('sms', 'SMS (Polipropileno)'),
        ('textil', 'Textil')
    ], string='Tipo de Empaquetado', help='Tipo de material de empaquetado utilizado')
    
    responsable_revision = fields.Many2one(
        'res.users',
        string='Responsable de Revisión de Paquetes Estériles',
        help='Usuario responsable de revisar los paquetes estériles'
    )
    
    numero_autoclave = fields.Char(
        string='# de Autoclave',
        help='Número del autoclave utilizado'
    )
    
    numero_carga = fields.Char(
        string='# de Carga',
        help='Número de carga del autoclave'
    )
    

    
    # Cantidad procesada
    cantidad = fields.Integer(
        string='Cantidad',
        default=1,
        help='Cantidad de unidades procesadas'
    )
    
    entregado_en = fields.Selection([
        ('area_negra', 'Área Negra'),
        ('area_blanca', 'Área Blanca')
    ], string='Entregado en', help='Área donde se entrega el instrumental')
    
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
    
    # ============================================================================
    # CAMPOS RELACIONADOS - INFORMACIÓN DE CONTEXTO
    # ============================================================================
    # Estos campos muestran información relacionada que viene de otros modelos.
    # Son útiles para búsquedas, filtros y mostrar contexto sin necesidad de
    # hacer consultas adicionales.
    #
    # IMPORTANTE: Los campos con store=True se guardan en la base de datos
    # para mejorar el rendimiento en búsquedas y reportes.
    # ============================================================================
    
    # Información de la orden padre
    cliente_id = fields.Many2one(
        related='orden_id.cliente_id',  # Viene de la orden
        string='Cliente',
        store=True,                     # Se guarda en BD para mejor rendimiento
        readonly=True                   # No se puede editar directamente
    )
    
    estado_orden = fields.Selection(
        related='orden_id.estado',      # Viene de la orden
        string='Estado de la Orden',
        store=True,                     # Se guarda en BD para mejor rendimiento
        readonly=True                   # No se puede editar directamente
    )
    
    # Información del instrumento del catálogo
    tipo_material = fields.Selection(
        related='instrumento_id.tipo_material',  # Viene del catálogo
        string='Tipo de Material',
        store=True,                              # Se guarda en BD para mejor rendimiento
        readonly=True                            # No se puede editar directamente
    )
    
    cantidad_estandar = fields.Integer(
        related='instrumento_id.cantidad_estandar',  # Viene del catálogo
        string='Cantidad Estándar',
        readonly=True,                               # No se puede editar directamente
        help='Cantidad estándar del instrumento según el catálogo'
    )
    
    # Todos los campos related a lavado_permitido_ids y esterilizacion_permitida_ids han sido eliminados.
    # También se eliminan las validaciones y métodos asociados a esos campos.
    
    # ============================================================================
    # CÁLCULO DE STU INDIVIDUAL
    # ============================================================================
    # Este método calcula las unidades de esterilización (STU) para esta
    # línea específica. El STU se usa para facturación y control de costos.
    #
    # FÓRMULA: STU = Equivalencia del instrumento × Cantidad procesada
    #
    # IMPORTANTE: La equivalencia viene del catálogo de instrumentos
    # y representa el valor en unidades de esterilización estándar.
    # ============================================================================
    @api.depends('instrumento_id', 'cantidad')
    def _compute_stu_calculado(self):
        """Calcular STU basado en la cantidad y equivalencia del instrumento"""
        for line in self:
            # Verificar que el instrumento tenga una equivalencia STU definida
            if line.instrumento_id and line.instrumento_id.equivalente_stu:
                # Calcular STU: equivalencia × cantidad procesada
                line.stu_calculado = line.cantidad * line.instrumento_id.equivalente_stu
            else:
                # Si no hay equivalencia definida, el STU es 0
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
    
    def unlink(self):
        """Sobrescribir el método unlink para manejar eliminación de manera segura"""
        # TODO: REACTIVAR VALIDACIONES DESPUÉS DE FASE DE PRUEBAS
        # for line in self:
        #     # Verificar si la línea tiene datos importantes que no deberían eliminarse
        #     if line.estado_orden in ['en_lavado', 'empaque', 'esterilizado', 'entregado']:
        #         raise exceptions.ValidationError(
        #             f"No se puede eliminar la línea '{line.name_get()[0][1]}' porque la orden está en estado '{line.estado_orden}'. "
        #             "Considere archivar el registro en lugar de eliminarlo."
        #         )
        #     
        #     # Verificar si hay datos de procesamiento que indican que ya se trabajó en esta línea
        #     if line.fecha_entrada or line.fecha_salida or line.lavado_aplicado or line.esterilizacion_aplicada:
        #         raise exceptions.ValidationError(
        #             f"No se puede eliminar la línea '{line.name_get()[0][1]}' porque ya tiene datos de procesamiento. "
        #             "Considere archivar el registro en lugar de eliminarlo."
        #         )
        
        return super().unlink()
    
    def action_archive(self):
        """Archivar la línea en lugar de eliminarla"""
        for line in self:
            line.active = False
        return True

    @api.onchange('instrumento_id')
    def _onchange_instrumento_id(self):
        """Actualizar valores por defecto cuando se selecciona un instrumento"""
        if self.instrumento_id:
            # Actualizar método de lavado por defecto
            if not self.lavado_metodo and self.instrumento_id.lavado_metodo_default:
                self.lavado_metodo = self.instrumento_id.lavado_metodo_default
            
            # Actualizar método de esterilización por defecto
            if not self.esterilizacion_metodo and self.instrumento_id.esterilizacion_metodo_default:
                self.esterilizacion_metodo = self.instrumento_id.esterilizacion_metodo_default
            
            # Actualizar cantidad por defecto
            if not self.cantidad and self.instrumento_id.cantidad_estandar:
                self.cantidad = self.instrumento_id.cantidad_estandar 

    @api.model
    def create(self, vals):
        """Crear línea de orden con valores por defecto del catálogo"""
        if 'instrumento_id' in vals:
            instrumento = self.env['instrument.catalog'].browse(vals['instrumento_id'])
            # Asignar método de lavado por defecto si no se especifica
            if 'lavado_metodo' not in vals and instrumento.lavado_metodo_default:
                vals['lavado_metodo'] = instrumento.lavado_metodo_default
            # Asignar método de esterilización por defecto si no se especifica
            if 'esterilizacion_metodo' not in vals and instrumento.esterilizacion_metodo_default:
                vals['esterilizacion_metodo'] = instrumento.esterilizacion_metodo_default
            # Asignar cantidad estándar si no se especifica
            if 'cantidad' not in vals and instrumento.cantidad_estandar:
                vals['cantidad'] = instrumento.cantidad_estandar
        return super().create(vals) 