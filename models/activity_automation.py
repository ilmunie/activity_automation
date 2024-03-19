from odoo import api,models,fields,_,SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval

class ActivityAutomationConfig(models.Model):
    _name = 'activity.automation.config'

    @api.model
    def name_get(self):
        res = []
        for rec in self:
            name = rec.model_id.name + ' (' + rec.model_id.model + ')'
            res.append((rec.id, name))
        return res

    active = fields.active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', domain=[('model', 'in', ('mrp.production', 'res.partner','crm.lead','sale.order','account.move','purchase.order','stock.picking','product.product','product.template'))])
    domain_filter = fields.Char()
    model_name = fields.Char(related='model_id.model')
    line_ids = fields.One2many('activity.automation.config.lines','config_id')
    def cron_activity_schedule(self):
        activity_automations = self.env['activity.automation.config'].search([])
        models_checked = []
        for activity_automation in activity_automations:
            if activity_automation.model_id.id not in models_checked:
                models_checked.append(activity_automation.model_id.id)
                domain = eval(activity_automation.domain_filter) if activity_automation.domain_filter else []
                recs_to_check = self.env[activity_automation.model_name].search(domain)
                for rec in recs_to_check:
                    rec.write({'trigger_activity_schedule': not rec.trigger_activity_schedule})
class ActivityAutomationConfigLines(models.Model):
    _name = 'activity.automation.config.lines'
    _order = 'sequence'

    sequence = fields.Integer()
    model_id = fields.Many2one(related='config_id.model_id', store=True)
    model_name = fields.Char(related='model_id.model', store=True)
    config_id = fields.Many2one('activity.automation.config')
    activity_type_ids = fields.Many2many('mail.activity.type', 'act_autom_config_line_act_type_rel', 'act_auto_conf_line_id', 'act_type_id')
    action_type = fields.Selection(selection=[('create', 'Create'), ('delete', 'Delete'), ('delete', 'Delete'), ('done', 'Mark as done')])
    activity_description = fields.Char()
    user_assigment_type = fields.Selection(selection=[('specific_users','Specific Users'), ('specifics_groups', 'Specific Groups'),('model_user_fields', 'Model user fields')])
    users_ids = fields.Many2many('res.users','act_autom_config_line_user_rel','act_auto_conf_line_id', 'user_id')
    groups_ids = fields.Many2many('res.groups', 'act_autom_config_line_group_rel', 'act_auto_conf_line_id', 'group_id')
    model_user_fields_ids = fields.Many2many('ir.model.fields', 'act_autom_config_line_field_rel', 'act_auto_conf_line_id', 'field_id')
    domain_to_check = fields.Char()
    active = fields.Boolean(default=True)

class ActivityAutomationMixin(models.AbstractModel):
    _name = 'activity.automation.mixing'

    trigger_activity_schedule = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.write({'trigger_activity_schedule': False})
        return res
    def write(self, vals):
        res = super().write(vals)
        activity_configs_to_check = self.env['activity.automation.config'].search([('model_id','=',self._name)])
        if activity_configs_to_check:
            for activity_config_to_check in activity_configs_to_check:
                for activity_rule in activity_config_to_check.line_ids.filtered(lambda x:x.active):
                    conditions = safe_eval(activity_rule.domain_to_check)
                    conditions.append(('id','=',self.id))
                    result = self.env[self._name].search_count(conditions)
                    if result and result > 0:
                        self.exec_activity_automation_line(activity_rule)
        return res

    def exec_activity_automation_line(self,activity_rule):
        for act_type in activity_rule.activity_type_ids:
            if activity_rule.action_type == 'create':
                users = []
                if activity_rule.user_assigment_type == 'specific_users':
                    users.extend(activity_rule.users_ids.mapped('id'))
                elif activity_rule.user_assigment_type == 'specifics_groups':
                    for group in activity_rule.groups_ids:
                        users.extend(group.users.mapped('id'))
                else:
                    for field in activity_rule.model_user_fields_ids:
                        user_field = safe_eval("self."+field.name)
                        if user_field:
                            users.append(user_field.id)
                if users:
                    scheduled_users = []
                    for user in users:
                        if user not in scheduled_users:
                            act_id = self.activity_type_get_xml_id(act_type)
                            self.activity_schedule(act_id, user_id=user,note=activity_rule.activity_description or '', date_deadline=fields.Date.today())
            else:
                for activity in self.activity_ids.filtered(lambda x: x.activity_type_id.id in activity_rule.activity_type_ids.mapped('id')):
                    if activity_rule.action_type == 'done' and self.env.user.id == activity.user_id.id:
                        activity.action_done()
                    else:
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
    _inherit = 'crm.lead'


class SaleOrder(models.Model,ActivityAutomationMixin):
    _inherit = 'sale.order'


class AccountMove(models.Model,ActivityAutomationMixin):
    _inherit = 'account.move'


class PurchaseOrder(models.Model,ActivityAutomationMixin):
    _inherit = 'purchase.order'


class StockPicking(models.Model,ActivityAutomationMixin):
    _inherit = 'stock.picking'

class ResPartner(models.Model,ActivityAutomationMixin):
    _inherit = 'res.partner'

class ProductProduct(models.Model,ActivityAutomationMixin):
    _inherit = 'product.product'

class ProductTemplate(models.Model,ActivityAutomationMixin):
    _inherit = 'product.template'

class MrpProduction(models.Model,ActivityAutomationMixin):
    _inherit = 'mrp.production'