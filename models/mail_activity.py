from odoo import api, fields, models
from datetime import timedelta, datetime

class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    unique_in_document = fields.Boolean('Única en documento',
                                        help='Elimina las tareas iguales del documento que no esten en estado terminado')
    unique_per_user = fields.Boolean('Única por usuario en documento')


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model_create_multi
    def create(self, vals_list):
        vals_list_to_create = []
        for act_to_create in vals_list:
            activitys = False
            act_to_create_type_rec = self.env['mail.activity.type'].browse(act_to_create['activity_type_id'])
            if act_to_create_type_rec.unique_per_user == True:
                activitys = self.env['mail.activity'].search(
                    [('res_model_id', '=', act_to_create['res_model_id']), ('res_id', '=', act_to_create['res_id']),
                     ('user_id', '=', act_to_create['user_id']),
                     ('activity_type_id', '=', act_to_create['activity_type_id'])])
            elif act_to_create_type_rec.unique_in_document == True:
                activitys = self.env['mail.activity'].search(
                    [('res_model_id', '=', act_to_create['res_model_id']), ('res_id', '=', act_to_create['res_id']),
                     ('activity_type_id', '=', act_to_create['activity_type_id'])])
            if not activitys:
                vals_list_to_create.append(act_to_create)
        return super(MailActivity, self).create(vals_list_to_create)
