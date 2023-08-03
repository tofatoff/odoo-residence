# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class Property(models.Model):
    _name = 'hr.property'
    _description = 'Property DB'

    name = fields.Char(string='Name', required=True)
    location = fields.Text(string='Location', required=True)
    code = fields.Char(string='Code', required=True)

    property_line = fields.One2many('hr.property.line','property_id', string='Property Line', readonly=True)

    property_line_reserved_count = fields.Integer(string='Total Property Line Reserved', compute='_compute_property_line_reserved_count', store=True)
    property_line_ready_count = fields.Integer(string='Total Property Line Ready', compute='_compute_property_line_ready_count', store=True)
    property_line_count = fields.Integer(string='Total Property Line', compute='_compute_property_line_count', store=True)
   

    @api.depends('property_line.state')
    def _compute_property_line_reserved_count(self):
        for record in self:
            record.property_line_reserved_count = record.property_line.search_count([('state','=','reserved'),('property_id','=',record.id)])

    @api.depends('property_line.state')
    def _compute_property_line_ready_count(self):
        for record in self:
            record.property_line_ready_count = record.property_line.search_count([('state','=','ready'),('property_id','=',record.id)])

    @api.depends('property_line')
    def _compute_property_line_count(self):
        for record in self:
            record.property_line_count = len(record.property_line)

    property_request = fields.One2many('hr.property.request','property_id', string='Property Request')

class PropertyLine(models.Model):
    _name = 'hr.property.line'
    _description = 'Property Line'

    name = fields.Char(string='Name')
    property_id = fields.Many2one('hr.property', string='Property', required=True, ondelete='cascade')
    block = fields.Char(string='Block')
    number = fields.Integer(string='Number')
    state = fields.Selection([('ready','Ready'),('reserved','Reserved')], string='State')

    property_request = fields.One2many('hr.property.request','property_line_id', string='Line Property')

class Request(models.Model):
    _name = 'hr.property.request'
    _description = 'Property Request'

    @api.model
    def _default_employee_id(self):
        employee = self.env.user.employee_id
        return employee
    
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res

    name = fields.Char(string='Number', readonly=True, default='New', unique=True)
    employee_id = fields.Many2one('hr.employee', string="Employee",
        store=True, required=True, readonly=False, 
        tracking=True,
        states={'approved': [('readonly', True)], 'done': [('readonly', True)]},
        default=_default_employee_id, 
        domain=lambda self: self._get_employee_id_domain(), 
        # check_company=True
        )
    
    @api.constrains('employee_id')
    def validate_user_double_request(self):
        for record in self:
            duplicates = self.search([('state', '!=', 'done'),('employee_id.id', '=', record.employee_id.id)])
            if len(duplicates) > 1:
                raise ValidationError("You already have a request that is currently being processed.")
                
    @api.constrains('employee_id')
    def validate_user_request_before_checkout(self):
        for record in self:
            duplicates = self.search([('checked_out', '=', False),('employee_id.id', '=', record.employee_id.id)])
            if len(duplicates) > 1:
                raise ValidationError("You have not checked out from the last residence")

    property_id = fields.Many2one('hr.property', string='Property', required=True, ondelete='cascade')
    state = fields.Selection([('draft','Draft'),('process','Process'),('waiting','Waiting'),('done','Done')], string='State', default='draft')


    @api.depends('property_line_id')
    def action_done(self):
        for rec in self:
            rec.write({'state': 'done'})
            rec.property_line_id.write({'state': 'reserved'})

    def action_confirm(self):
        for rec in self:
            rec.update_number()
            rec.write({'state': 'process'})

    def action_approve(self):
        for rec in self:
            rec.write({'state': 'waiting'})

    property_line_id = fields.Many2one('hr.property.line', 
                                       string='Property Line', 
                                       ondelete='cascade', 
                                       attrs={'invisible': [('state', '!=', 'waiting'),('state', '!=', 'done')]})

    def update_number(self):

        for row in self:
            if row.state == 'draft' and row.name == 'New':
                sequence_template = self.env['ir.sequence'].next_by_code('residence.request')
                now = datetime.datetime.now()
                month = now.strftime("%m")
                year = now.strftime("%Y")
                row.name = sequence_template+'/'+str(row.property_id.code)+'/'+month+'/'+year

    request_out = fields.One2many('hr.property.request.out','request_in',string='Request Out')
    checked_out = fields.Boolean(string='Checkout',default=False)


class RequestOut(models.Model):
    _name = "hr.property.request.out"
    _description = "Request Out"
    _inherits = {'hr.property.request': 'request_in'}

    name = fields.Char(string='Number', readonly=True, default='New')
    request_in = fields.Many2one('hr.property.request',string='Residence Reservation No.', required=True, ondelete='restrict',domain=[('state', '=', 'done'),('checked_out','=',False)], unique=True)

    state = fields.Selection([('draft','Draft'),('process','Process'),('done','Done')], string='State', default='draft')

    checkout_date = fields.Date(string="Checkout Date",default=fields.Date.today(), states={'draft': [('readonly', False)]})

    def action_done(self):
        for rec in self:
            rec.write({'state': 'done'})
            rec.request_in.property_line_id.write({'state': 'ready'})
            rec.request_in.checked_out = True

    def action_confirm(self):
        for rec in self:
            rec.update_number()
            rec.write({'state': 'process'})

    def update_number(self):

        for row in self:
            if row.state == 'draft' and row.name == 'New':
                sequence_template = self.env['ir.sequence'].next_by_code('residence.request.out')
                now = datetime.datetime.now()
                month = now.strftime("%m")
                year = now.strftime("%Y")
                row.name = sequence_template+'/'+str(row.property_id.code)+'/'+month+'/'+year

    