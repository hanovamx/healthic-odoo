# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime


# ============================================================================
# TIPOS DE CIRUGÍA
# ============================================================================
# Este modelo define los diferentes tipos de procedimientos quirúrgicos
# y los instrumentos que típicamente se necesitan para cada uno.
#
# FUNCIONES PRINCIPALES:
# - Definir tipos de cirugía disponibles en el sistema
# - Configurar instrumentos predeterminados por tipo de cirugía
# - Facilitar la carga automática de instrumentos en órdenes
# - Mantener estándares de instrumentación por procedimiento
#
# RELACIÓN CON INSTRUMENTOS:
# - SurgeryType (1) ←→ (N) SurgeryTypeInstrument (N) ←→ (1) InstrumentCatalog
# - Cada tipo de cirugía puede tener múltiples instrumentos predeterminados
# - Los instrumentos predeterminados se cargan automáticamente al crear órdenes
# ============================================================================
class SurgeryType(models.Model):
    _name = 'surgery.type'
    _description = 'Tipos de Cirugía'
    _order = 'name'  # Ordenar alfabéticamente por nombre

    # ============================================================================
    # INFORMACIÓN BÁSICA DEL TIPO DE CIRUGÍA
    # ============================================================================
    
    name = fields.Char(
        string='Nombre de la Cirugía',
        required=True,  # Campo obligatorio
        help='Nombre del tipo de cirugía'
    )
    
    codigo = fields.Char(
        string='Código',
        help='Código interno de la cirugía para identificación rápida'
    )
    
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada de la cirugía y sus características'
    )
    
    # ============================================================================
    # RELACIÓN CON INSTRUMENTOS PREDETERMINADOS
    # ============================================================================
    # Esta es la relación más importante: define qué instrumentos se cargan
    # automáticamente cuando se selecciona este tipo de cirugía en una orden.
    #
    # FLUJO DE TRABAJO:
    # 1. Se configura un tipo de cirugía con sus instrumentos predeterminados
    # 2. Al crear una orden, se selecciona el tipo de cirugía
    # 3. Se ejecuta automáticamente el método _onchange_tipo_cirugia
    # 4. Se cargan los instrumentos predeterminados como líneas de la orden
    # ============================================================================
    instrumentos_predeterminados_ids = fields.One2many(
        'surgery.type.instrument',  # Modelo intermedio que conecta cirugía con instrumentos
        'surgery_type_id',          # Campo Many2one en el modelo intermedio
        string='Instrumentos Predeterminados',
        help='Instrumentos que típicamente se necesitan para esta cirugía. '
             'Se cargan automáticamente al seleccionar este tipo de cirugía en una orden.'
    )
    
    active = fields.Boolean(string='Activo', default=True)
    
    # Campos computados
    total_instrumentos = fields.Integer(
        string='Total de Instrumentos',
        compute='_compute_total_instrumentos',
        store=True
    )
    
    @api.depends('instrumentos_predeterminados_ids')
    def _compute_total_instrumentos(self):
        """Calcular el total de instrumentos predeterminados"""
        for surgery in self:
            surgery.total_instrumentos = len(surgery.instrumentos_predeterminados_ids)
    
    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            name = record.name
            if record.codigo:
                name = f"[{record.codigo}] {name}"
            result.append((record.id, name))
        return result


class SurgeryTypeInstrument(models.Model):
    _name = 'surgery.type.instrument'
    _description = 'Instrumentos por Tipo de Cirugía'
    _order = 'surgery_type_id, sequence'
    _active_name = 'active'

    active = fields.Boolean(string='Activo', default=True, help='Indica si el registro está activo')

    surgery_type_id = fields.Many2one(
        'surgery.type',
        string='Tipo de Cirugía',
        required=True,
        ondelete='cascade'
    )
    
    instrumento_id = fields.Many2one(
        'instrument.catalog',
        string='Instrumento',
        required=True,
        help='Instrumento predeterminado para esta cirugía'
    )
    
    cantidad_predeterminada = fields.Char(
        string='Cantidad Predeterminada',
        default='1',
        help='Cantidad predeterminada de este instrumento'
    )
    
    entregado_en = fields.Selection([
        ('area_negra', 'Área Negra'),
        ('area_blanca', 'Área Blanca')
    ], string='Entregado en', help='Área donde se entrega este instrumento')
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de aparición en la lista'
    )
    
    observaciones = fields.Text(
        string='Observaciones',
        help='Observaciones específicas para este instrumento en esta cirugía'
    )
    
    # Campos relacionados para facilitar la gestión
    tipo_material = fields.Selection(
        related='instrumento_id.tipo_material',
        string='Tipo de Material',
        readonly=True
    )
    
    cantidad_estandar = fields.Integer(
        related='instrumento_id.cantidad_estandar',
        string='Cantidad Estándar',
        readonly=True
    )
    
    def unlink(self):
        """Sobrescribir el método unlink para manejar eliminación de manera segura"""
        for record in self:
            # Verificar si hay órdenes que usan este tipo de cirugía
            orders_using_surgery = self.env['instrument.order'].search([
                ('tipo_cirugia', '=', record.surgery_type_id.id)
            ], limit=1)
            
            if orders_using_surgery:
                raise exceptions.ValidationError(
                    f"No se puede eliminar el instrumento '{record.instrumento_id.name}' del tipo de cirugía "
                    f"'{record.surgery_type_id.name}' porque hay órdenes que lo utilizan. "
                    "Considere archivar el registro en lugar de eliminarlo."
                )
        
        return super().unlink()
    
    def action_archive(self):
        """Archivar el registro en lugar de eliminarlo"""
        for record in self:
            record.active = False
        return True


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
    
    tipo_cirugia = fields.Many2one(
        'surgery.type',
        string='Tipo de Cirugía',
        help='Tipo de cirugía a realizar'
    )
    
    medico_responsable = fields.Char(
        string='Médico Responsable (Texto)',
        help='Nombre del médico responsable del procedimiento (campo de texto libre)'
    )
    
    medico_id = fields.Many2one(
        'medical.doctor',
        string='Médico Responsable',
        help='Médico responsable del procedimiento'
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
    
    quien_realiza_lavado = fields.Char(
        string='Quien Realiza Lavado',
        help='Nombre de la persona que realizó el lavado'
    )
    
    metodo_lavado_id = fields.Many2one(
        'instrument.method',
        string='Método de Lavado',
        domain=[('tipo', '=', 'lavado')],
        help='Método de lavado utilizado'
    )
    
    # Métodos de esterilización planificados
    usar_autoclave = fields.Boolean(
        string='Autoclave',
        help='Se utilizará autoclave para esterilización'
    )
    
    usar_peroxido = fields.Boolean(
        string='Peróxido',
        help='Se utilizará peróxido para esterilización'
    )
    
    usar_oxido_etileno = fields.Boolean(
        string='Óxido de Etileno',
        help='Se utilizará óxido de etileno para esterilización'
    )
    
    usar_plasma = fields.Boolean(
        string='Plasma',
        help='Se utilizará plasma para esterilización'
    )
    
    responsable_esterilizacion = fields.Many2one(
        'res.users', 
        string='Responsable de Esterilización',
        help='Usuario responsable del proceso de esterilización'
    )
    
    # Información de equipo y carga para esterilización
    equipo_esterilizacion = fields.Char(
        string='Equipo de Esterilización',
        help='Identificación del equipo utilizado para esterilización'
    )
    
    numero_carga_esterilizacion = fields.Char(
        string='Número de Carga',
        help='Número de carga del proceso de esterilización'
    )
    
    # Indicador biológico
    tiene_indicador_biologico = fields.Boolean(
        string='Indicador Biológico en Carga',
        help='Indica si la carga incluye un indicador biológico'
    )
    
    resultado_indicador_biologico = fields.Selection([
        ('positivo', 'Positivo'),
        ('negativo', 'Negativo'),
        ('pendiente', 'Pendiente')
    ], string='Resultado del Indicador Biológico', 
       help='Resultado del indicador biológico')
    
    fecha_lectura_biologico = fields.Datetime(
        string='Fecha de Lectura',
        help='Fecha y hora de lectura del indicador biológico'
    )
    
    responsable_lectura_biologico = fields.Many2one(
        'res.users',
        string='Responsable de Lectura',
        help='Usuario que realizó la lectura del indicador biológico'
    )
    
    responsable_descarga = fields.Many2one(
        'res.users',
        string='Responsable de Descarga',
        help='Usuario responsable de la descarga/entrega'
    )
    
    # ============================================================================
    # RELACIÓN PRINCIPAL CON INSTRUMENTOS
    # ============================================================================
    # Esta es la relación más importante del módulo: conecta una orden con sus
    # instrumentos individuales. Cada línea representa un instrumento específico
    # que será procesado en esta orden.
    #
    # ESTRUCTURA DE LA RELACIÓN:
    # - InstrumentOrder (1) ←→ (N) InstrumentOrderLine (N) ←→ (1) InstrumentCatalog
    # - Una orden puede tener múltiples instrumentos
    # - Cada instrumento puede aparecer en múltiples órdenes
    # - La eliminación de una orden elimina automáticamente todas sus líneas (cascade)
    #
    # FLUJO DE TRABAJO:
    # 1. Se crea una orden vacía
    # 2. Se selecciona un tipo de cirugía → se cargan automáticamente los instrumentos predeterminados
    # 3. Se pueden agregar/quitar instrumentos manualmente
    # 4. Cada línea mantiene el estado individual del procesamiento
    # ============================================================================
    linea_ids = fields.One2many(
        'instrument.order.line',  # Modelo de las líneas de detalle
        'orden_id',              # Campo Many2one en la línea que apunta a esta orden
        string='Líneas de Instrumental',
        help='Detalle de instrumentos en esta orden. Cada línea representa un instrumento específico que será procesado.'
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
    
    # Campos para devolución a proveedor
    requiere_devolucion = fields.Boolean(
        string='Requiere Devolución a Proveedor',
        help='Indica si algún instrumento requiere devolución al proveedor'
    )
    
    motivo_devolucion = fields.Text(
        string='Motivo de Devolución',
        help='Razón por la cual se requiere la devolución'
    )
    
    proveedor_devolucion = fields.Char(
        string='Proveedor',
        help='Nombre del proveedor al que se devolverá el instrumental'
    )
    
    fecha_devolucion = fields.Date(
        string='Fecha de Devolución',
        help='Fecha en que se realizó o realizará la devolución'
    )
    
    numero_guia_devolucion = fields.Char(
        string='Número de Guía',
        help='Número de guía o referencia de la devolución'
    )
    
    # Campos de firma - Recepción
    firma_entrega_hospitalaria = fields.Binary(
        string='Firma Hospitalaria - Entrega',
        help='Firma del personal del hospital que entrega el instrumental'
    )
    
    firma_recibe_healthic = fields.Binary(
        string='Firma Healthic - Recibe',
        help='Firma del personal de Healthic que recibe el instrumental'
    )
    
    # Campos de firma - Devolución
    firma_entrega_healthic = fields.Binary(
        string='Firma Healthic - Entrega',
        help='Firma del personal de Healthic que entrega el instrumental procesado'
    )
    
    firma_recibe_hospitalaria = fields.Binary(
        string='Firma Hospitalaria - Recibe',
        help='Firma del personal del hospital que recibe el instrumental procesado'
    )
    
    # Campos antiguos para compatibilidad
    firma_entrega = fields.Binary(
        string='Firma de Quien Entrega (Deprecated)',
        help='Firma de la persona que entrega el instrumental'
    )
    
    firma_recibe = fields.Binary(
        string='Firma de Quien Recibe (Deprecated)',
        help='Firma de la persona que recibe el instrumental'
    )
    
    # ============================================================================
    # CAMPOS COMPUTADOS - TOTALES DE LA ORDEN
    # ============================================================================
    # Estos campos calculan automáticamente los totales basándose en las líneas
    # de instrumentos. Se actualizan cada vez que se modifica una línea.
    #
    # IMPORTANTE: Los campos computados con store=True se guardan en la base de datos
    # para mejorar el rendimiento en búsquedas y reportes.
    # ============================================================================
    total_instrumentos = fields.Integer(
        string='Total de Instrumentos',
        compute='_compute_totales',  # Método que calcula el valor
        store=True,                  # Se guarda en BD para mejor rendimiento
        help='Número total de instrumentos en esta orden (calculado automáticamente)'
    )
    
    total_stu = fields.Float(
        string='Total STU',
        compute='_compute_totales',  # Mismo método que calcula ambos totales
        store=True,                  # Se guarda en BD para mejor rendimiento
        digits=(10, 4),              # Precisión decimal para cálculos de facturación
        help='Total de unidades de esterilización (STU) para facturación'
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
    
    # ============================================================================
    # CARGA AUTOMÁTICA DE INSTRUMENTOS POR TIPO DE CIRUGÍA
    # ============================================================================
    # Este método se ejecuta automáticamente cuando el usuario selecciona un
    # tipo de cirugía en la orden. Carga los instrumentos predeterminados que
    # típicamente se necesitan para ese tipo de procedimiento.
    #
    # FLUJO:
    # 1. Usuario selecciona tipo de cirugía
    # 2. Se ejecuta este método automáticamente (@api.onchange)
    # 3. Se obtienen los instrumentos predeterminados del tipo de cirugía
    # 4. Se crean las líneas de detalle automáticamente
    # 5. El usuario puede modificar/agregar/quitar instrumentos después
    #
    # NOTA: Los instrumentos predeterminados se configuran en el modelo
    # SurgeryTypeInstrument y se pueden editar desde la vista del tipo de cirugía.
    # ============================================================================
    @api.onchange('tipo_cirugia')
    def _onchange_tipo_cirugia(self):
        """Precargar instrumentos predeterminados cuando se selecciona un tipo de cirugía"""
        if self.tipo_cirugia and self.tipo_cirugia.instrumentos_predeterminados_ids:
            # Solo cargar si no hay líneas existentes (evitar sobrescribir datos)
            if not self.linea_ids:
                new_lines = []
                for pred_instrument in self.tipo_cirugia.instrumentos_predeterminados_ids:
                    # Convertir cantidad_predeterminada de string a integer de forma segura
                    cantidad = 1
                    try:
                        cantidad = int(pred_instrument.cantidad_predeterminada or '1')
                    except (ValueError, TypeError):
                        cantidad = 1  # Valor por defecto si hay error en la conversión
                    
                    # Crear nueva línea usando la sintaxis de Odoo para One2many
                    # (0, 0, {...}) = crear nueva línea
                    new_lines.append((0, 0, {
                        'instrumento_id': pred_instrument.instrumento_id.id,  # Instrumento del catálogo
                        'cantidad': cantidad,  # Cantidad predeterminada convertida
                        'entregado_en': pred_instrument.entregado_en,  # Área de entrega (negra/blanca)
                        'observaciones': pred_instrument.observaciones or '',  # Observaciones específicas
                    }))
                # Asignar las líneas creadas al campo One2many
                self.linea_ids = new_lines
    
    # ============================================================================
    # CÁLCULO AUTOMÁTICO DE TOTALES
    # ============================================================================
    # Este método calcula automáticamente los totales de la orden basándose
    # en las líneas de instrumentos. Se ejecuta cada vez que se modifica
    # una línea o se cambia un instrumento.
    #
    # CAMPOS CALCULADOS:
    # - total_instrumentos: Número de líneas (instrumentos) en la orden
    # - total_stu: Suma de las unidades de esterilización (STU) de todos los instrumentos
    #
    # IMPORTANTE: El decorador @api.depends especifica qué campos activan
    # el recálculo automático.
    # ============================================================================
    @api.depends('linea_ids', 'linea_ids.instrumento_id')
    def _compute_totales(self):
        """Calcular totales de instrumentos y STU"""
        for order in self:
            # Contar el número total de instrumentos (líneas)
            order.total_instrumentos = len(order.linea_ids)
            
            # Calcular el total STU sumando la equivalencia de cada instrumento
            # equivalente_stu viene del catálogo de instrumentos (InstrumentCatalog)
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
        
        # TODO: REACTIVAR VALIDACIONES DESPUÉS DE FASE DE PRUEBAS
        # Validar campos obligatorios
        # campos_faltantes = []
        # 
        # if not self.cliente_id:
        #     campos_faltantes.append('Cliente Hospitalario')
        # if not self.fecha_recepcion:
        #     campos_faltantes.append('Fecha de Recepción')
        # if not self.linea_ids:
        #     campos_faltantes.append('Instrumentos a Procesar')
        # if not self.medico_id:
        #     campos_faltantes.append('Médico Responsable')
        # if not self.tipo_cirugia:
        #     campos_faltantes.append('Tipo de Cirugía')
        # if not self.sala:
        #     campos_faltantes.append('Sala Quirúrgica')
        # if not self.numero_cuenta:
        #     campos_faltantes.append('Número de Cuenta')
        # 
        # # Verificar que se haya seleccionado al menos un método de esterilización
        # if not any([self.usar_autoclave, self.usar_peroxido, self.usar_oxido_etileno, self.usar_plasma]):
        #     campos_faltantes.append('Al menos un Método de Esterilización')
        # 
        # # Verificar firmas de recepción
        # if not self.firma_entrega_hospitalaria:
        #     campos_faltantes.append('Firma Hospitalaria de Entrega')
        # if not self.firma_recibe_healthic:
        #     campos_faltantes.append('Firma Healthic de Recepción')
        # 
        # if campos_faltantes:
        #     raise exceptions.UserError(
        #         f"No se puede iniciar el lavado. Los siguientes campos son obligatorios:\n" +
        #         "\n".join(f"• {campo}" for campo in campos_faltantes)
        #     )
        
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