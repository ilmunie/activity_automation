from odoo import api,models,fields,_,SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError




class ActivityAutomationConfig(models.Model):
    _name = 'activity.automation.config'

    @api.model
    def name_get(self):
        res = []
        for rec in self:
            name = rec.model_id.name + ' ('+ rec.model_id.model+')'
            
            res.append((rec.id, name))
        return res

    active = fields.Boolean()
    model_id = fields.Many2one('ir.model',domain=[('model','in',('crm.lead','sale.order','account.move'))])
    line_ids = fields.One2many('activity.automation.config.lines','config_id')

    def update_module(self):
        module = self.env['ir.module.module'].search([('name', '=', 'activity_automation')], limit=1)
        if module:
            module.button_immediate_upgrade()
   
    def susbscribe_model(self):
        for record in self:
            if record.model_id:
                record.active=True
                if 'activity.automation.config.lines' in record.model_id.inherited_model_ids.mapped('model'):
                    continue
                else:
                    abstract_class_model_id = self.env['ir.model'].search(([('name','=','activity.automation.config.lines')]))[0].id
                    txt_to_exec = "class " + "SaleOrder" + """(models.Model,ActivityAutomationMixin):
                    _inherit='sale.order'"""
                    exec(txt_to_exec)
                    self.update_module()
            else:
                 raise UserError(_("Please define the model you want to subscribe to the activities automation"))

    def unsusbscribe_model(self):
        for record in self:
            if record.model_id:
                record.active=False
                if 'activity.automation.config.lines' in record.model_id.inherited_model_ids.mapped('model'):
                    abstract_class_model_id = self.env['ir.model'].search(([('name','=','activity.automation.config.lines')]))[0].id
                    record.model_id.inherited_model_ids = [(3,abstract_class_model_id)]
    


class ActivityAutomationConfigLines(models.Model):
    _name = 'activity.automation.config.lines'

    model_id = fields.Many2one(related='config_id.model_id',store=True)
    model_name = fields.Char(related='model_id.model',store=True)
    config_id = fields.Many2one('activity.automation.config')
    activity_type_ids = fields.Many2many('mail.activity.type','act_autom_config_line_act_type_rel','act_auto_conf_line_id','act_type_id')
    action_type = fields.Selection(selection=[('create','Create'),('delete','Delete')])
    activity_description = fields.Char()
    user_assigment_type = fields.Selection(selection=[('specific_users','Specific Users'),('specifics_groups','Specific Groups'),('model_user_fields','Model user fields')])
    users_ids = fields.Many2many('res.users','act_autom_config_line_user_rel','act_auto_conf_line_id','user_id')
    groups_ids = fields.Many2many('res.groups','act_autom_config_line_group_rel','act_auto_conf_line_id','group_id')
    #@api.onchange('user_assigment_type')
    #def get_domain(self):
    #    for record in self:
    #        model_id = record.model_id.id
    #        res = [('model_id','=',model_id),('relation','=','res.users')]
    #        return res
    model_user_fields_ids = fields.Many2many('ir.model.fields','act_autom_config_line_field_rel','act_auto_conf_line_id','field_id')
    domain_to_check = fields.Char()
    active = fields.Boolean()

class ActivityAutomationMixin(models.AbstractModel):
    _name = 'activity.automation.mixin'

    def write(self, vals):
        # Add your custom logic here
        res = super().write(vals)
        # Add your custom logic here
        activity_configs_to_check = self.env['activity.automation.config'].search([('model_id','=',self._name)])
        if activity_configs_to_check:
            for activity_config_to_check in activity_configs_to_check:
                for activity_rule in activity_config_to_check.line_ids.filtered(lambda x:x.active):
                    conditions = eval(activity_rule.domain_to_check)
                    conditions.append(('id','=',self.id))
                    result = self.env[self._name].search_count(conditions)
                    if result and result >0:
                        self.exec_activity_automation_line(activity_rule)
        #import pdb;pdb.set_trace()
        return res

    def exec_activity_automation_line(self,activity_rule):
        for act_type in activity_rule.activity_type_ids:
            if activity_rule.action_type == 'create':
                users = []
                if activity_rule.user_assigment_type == 'specific_users':
                    users.extend(activity_rule.users_ids.mapped('id'))
                elif activity_rule.user_assigment_type == 'specific_groups':
                    for group in activity_rule.groups_ids:
                        users.extend(group.user_ids.mapped('id'))
                else:
                    for field in activity_rule.model_user_fields_ids:
                        user_field = eval("self."+field.name)
                        if user_field:
                            users.append(user_field.id)
                if users:
                    for user in users:
                        act_id = self.activity_type_get_xml_id(act_type)
                        self.with_context(mail_activity_quick_update = True).activity_schedule(act_id, user_id=user,note=activity_rule.activity_description, date_deadline=fields.Date.today())

            else:
                for activity in self.activity_ids.filtered(lambda x: x.activity_type_id.id in activity_rule.activity_type_ids.mapped('id')):
                    activity.sudo().unlink()
        return False

    def activity_type_get_xml_id(self,activity_type_id):
        external_xml_id = self.env['ir.model.data'].search([
            ('model', '=', 'mail.activity.type'),
            ('res_id', '=', activity_type_id.id)
        ])
        if external_xml_id:
            external_xml_id = external_xml_id.module + '.' + external_xml_id.name
        else:
            external_xml_id = False
        return external_xml_id







class CrmLead(models.Model,ActivityAutomationMixin):
    _inherit ='crm.lead'
class SaleOrder(models.Model,ActivityAutomationMixin):
    _inherit ='sale.order'
class AccountMove(models.Model,ActivityAutomationMixin):
    _inherit ='account.move'

