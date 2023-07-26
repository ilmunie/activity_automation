# -*- coding: utf-8 -*-
{
    'name': 'activity_automation',
    'version': '2.0',
    'category': 'Base',
    'sequence': 15,
    'summary': 'Odoo v15 module that allows to automate activity types in any model. The module patchs the write method, evaluating ui configurable conditions in order to create or delete differents activity types',
    'description': "",
    'website': '',
    'depends': [
        'crm',
        'sale',
        'purchase',
        'stock',
        'account',
    ],
    'data': [
        'views/activity_automation_form_views.xml',
        'views/activity_type_view.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
