# -*- coding: utf-8 -*-
{
    'name': "odoo_infinity_app_store",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website','website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/ssh_repository_views.xml',
        'views/odoo_infinity_app_store.xml',
        'views/register_repo.xml',
        'views/dashboard_template.xml',
        'views/details_dashboard_template.xml',
        'views/repository_dashboard_template.xml',
        'views/my_apps_dashboard_template.xml',
        'views/view_app_template.xml',
        'views/website_login.xml',
        'views/inherite_res_user_form.xml',
        'views/my_account_details.xml',
        'views/product_template.xml',
        'views/cart_view_template.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            '/odoo_infinity_app_store/static/src/js/my_dashboard.js',
            '/odoo_infinity_app_store/static/src/js/fetch_repo.js',
            '/odoo_infinity_app_store/static/src/js/login_data.js',
            '/odoo_infinity_app_store/static/src/js/add_cart.js',
            '/odoo_infinity_app_store/static/src/css/app_view_details.css',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
