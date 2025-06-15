# -*- coding: utf-8 -*-
# from odoo import http


# class Healthic-odoo(http.Controller):
#     @http.route('/healthic-odoo/healthic-odoo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/healthic-odoo/healthic-odoo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('healthic-odoo.listing', {
#             'root': '/healthic-odoo/healthic-odoo',
#             'objects': http.request.env['healthic-odoo.healthic-odoo'].search([]),
#         })

#     @http.route('/healthic-odoo/healthic-odoo/objects/<model("healthic-odoo.healthic-odoo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('healthic-odoo.object', {
#             'object': obj
#         })

