# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MedicalDoctor(models.Model):
    _name = 'medical.doctor'
    _description = 'Médico'
    _order = 'name'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Nombre Completo',
        required=True,
        help='Nombre completo del médico'
    )
    
    cedula_profesional = fields.Char(
        string='Cédula Profesional',
        help='Número de cédula profesional del médico'
    )
    
    especialidad = fields.Char(
        string='Especialidad',
        help='Especialidad médica'
    )
    
    telefono = fields.Char(
        string='Teléfono',
        help='Número de teléfono de contacto'
    )
    
    email = fields.Char(
        string='Email',
        help='Correo electrónico'
    )
    
    hospital_ids = fields.Many2many(
        'hospital.client',
        'medical_doctor_hospital_rel',
        'doctor_id',
        'hospital_id',
        string='Hospitales',
        help='Hospitales donde trabaja el médico'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, el médico no aparecerá en las listas de selección'
    )
    
    display_name = fields.Char(
        string='Nombre a Mostrar',
        compute='_compute_display_name',
        store=True
    )
    
    # Estadísticas
    orden_count = fields.Integer(
        string='Número de Órdenes',
        compute='_compute_orden_count',
        store=True
    )
    
    @api.depends('name', 'cedula_profesional', 'especialidad')
    def _compute_display_name(self):
        """Calcular el nombre a mostrar del médico"""
        for doctor in self:
            parts = []
            # Ensure name is a string and not empty
            if doctor.name and str(doctor.name).strip():
                parts.append(str(doctor.name))
            else:
                parts.append("Sin Nombre")
            
            # Add especialidad if it exists and is not empty
            if doctor.especialidad and str(doctor.especialidad).strip():
                parts.append(f"({str(doctor.especialidad)})")
            
            # Add cedula if it exists and is not empty
            if doctor.cedula_profesional and str(doctor.cedula_profesional).strip():
                parts.append(f"- Céd: {str(doctor.cedula_profesional)}")
            
            doctor.display_name = ' '.join(parts)
    
    @api.depends('name')
    def _compute_orden_count(self):
        """Calcular el número de órdenes asociadas al médico"""
        for doctor in self:
            doctor.orden_count = self.env['instrument.order'].search_count([
                ('medico_id', '=', doctor.id)
            ])
    
    def name_get(self):
        """Personalizar el nombre mostrado en los campos de selección"""
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Buscar médicos por nombre, cédula o especialidad"""
        if args is None:
            args = []
        if name:
            args = ['|', '|', 
                    ('name', operator, name),
                    ('cedula_profesional', operator, name),
                    ('especialidad', operator, name)] + args
        return super(MedicalDoctor, self).search(args, limit=limit).name_get() 