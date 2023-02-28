from odoo import api, fields, models, SUPERUSER_ID, _
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from dateutil.relativedelta import relativedelta



class MailActivity(models.Model):
    _inherit = "mail.activity"

    schedule_mode = fields.Selection(selection=[
        ('mass_schedule', 'Email Mass Mailing'),
        ('native', 'Post on Multiple Documents')], string='Composition mode', default='native')
 
    AVAILABLE_PRIORITIES = [
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Urgent'),
        ]
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=AVAILABLE_PRIORITIES[0][0])
    subtype = fields.Char()
    special_treatment = fields.Boolean(related = 'activity_type_id.special_treatment')

    activity_configuration_id = fields.Many2one('activity.configuration')


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        import pdb;pdb.set_trace()

        #if self.schedule_mode == 'mass_schedule':
        #    rec_ids = self._context.get('active_ids',[])
        #    for rec_id in rec_ids:
        #        lead = self.env['crm.lead'].browse(lead_to_update_id)
#
        #else:
        #    
        return super(MailActivity, self).activity_schedule(act_type_xmlid = act_type_xmlid,date_deadline = date_deadline,summary = summary,note = note,act_values=act_values)


