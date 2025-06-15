# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HospitalClient(models.Model):
    _name = 'hospital.client'
    _description = 'Cliente Hospitalario'
    _order = 'name'

    name = fields.Char(
        string='Razón Social', 
        required=True,
        help='Nombre o razón social del hospital/cliente'
    )
    
    facturacion_concepto = fields.Char(
        string='Concepto de Facturación',
        help='Descripción específica para la facturación'
    )
    
    tipo_facturacion = fields.Selection([
        ('stu', 'STU (Sterilization Unit)'),
        ('metro3', 'Metro Cúbico'),  
        ('carga', 'Por Carga')
    ], string='Tipo de Facturación', required=True, default='stu')
    
    # Campos adicionales útiles
    active = fields.Boolean(string='Activo', default=True)
    
    # Información de contacto
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    address = fields.Text(string='Dirección')
    
    # Estadísticas
    orden_count = fields.Integer(
        string='Número de Órdenes',
        compute='_compute_orden_count'
    )
    
    @api.depends('name')
    def _compute_orden_count(self):
        """Calcular el número de órdenes del cliente"""
        for client in self:
            client.orden_count = self.env['instrument.order'].search_count([
                ('cliente_id', '=', client.id)
            ])
    
    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            name = record.name
            if record.tipo_facturacion:
                tipo_dict = dict(record._fields['tipo_facturacion'].selection)
                name += f' ({tipo_dict[record.tipo_facturacion]})'
            result.append((record.id, name))
        return result 