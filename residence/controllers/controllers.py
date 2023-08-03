# -*- coding: utf-8 -*-
# from odoo import http


# class Residence(http.Controller):
#     @http.route('/residence/residence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/residence/residence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('residence.listing', {
#             'root': '/residence/residence',
#             'objects': http.request.env['residence.residence'].search([]),
#         })

#     @http.route('/residence/residence/objects/<model("residence.residence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('residence.object', {
#             'object': obj
#         })
