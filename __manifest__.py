# -*- coding: utf-8 -*-
{
    'name': 'activity_automation',
    'version': '1.0',
    'category': 'Base',
    'sequence': 15,
    'summary': 'Odoo v15 module that allows to automate activity types in any model. The module patchs the write method, evaluating ui configurable conditions in order to create or delete differents activity types',
    'description': "",
    'website': '',
    'depends': [
        'custom_leads',
    ],

    'data': [
        'views/activity_automation_form_views.xml',
        'security/ir.model.access.csv',
    ],
   
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
