import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from werkzeug.exceptions import NotFound
from odoo.addons.website_sale.controllers.main import WebsiteSale

class DashboardController(http.Controller):

    @http.route('/my/dashboard', auth='user', website=True,csrf=False)
    def dashboard(self, **kwargs):
        return request.render('odoo_infinity_app_store.dashboard_template', {})

    @http.route('/my/dashboard/repositories', auth='user', website=True,csrf=False)
    def repositories(self, **kwargs):
        return request.render('odoo_infinity_app_store.dashboard_template', {'active_section': 'repositories'})

    @http.route('/my/apps/dashboard', auth='user', website=True,csrf=False)
    def apps(self, **kwargs):
        return request.render('odoo_infinity_app_store.my_apps_section')

    @http.route('/my/dashboard/register', type='http', auth='user', website=True, csrf=False)
    def my_repo(self, **kwargs):
        return request.render('odoo_infinity_app_store.register_repo')

    @http.route('/fetch_repository_endpoint', type='json', auth='user', csrf=False)
    def fetch_repository(self, **post):
        ssh_url = post.get('ssh_url')
        return json.dumps({'ssh_url': ssh_url})

    @http.route('/submit_ssh_url', type='json', auth='user', csrf=False)
    def submit_ssh_url(self, ssh_url):
        user = request.env.user
        ssh_repo_obj = request.env['ssh.repository']
        ssh_repo_obj.create({'user_id': user.id, 'ssh_url': ssh_url})
        return {'result': 'success'}

    @http.route('/fetch_ssh_urls', type='json', auth='user', csrf=False)
    def fetch_ssh_urls(self):
        ssh_repo_records = request.env['ssh.repository'].search([])
        ssh_urls = [{'id': record.id, 'ssh_url': record.ssh_url} for record in ssh_repo_records]
        return ssh_urls

    @http.route('/update_ssh_url', type='json', auth='user')
    def update_ssh_url(self, repo_id, new_ssh_url, **kwargs):
        print("===========repo_id==============", repo_id)
        print("===========new_ssh_url==============", new_ssh_url)
        ssh_repo = request.env['ssh.repository'].sudo().browse(int(repo_id))
        print("===========ssh_repo==============", ssh_repo)
        ssh_repo.write({'ssh_url': new_ssh_url})
        return {'success': True}

    @http.route('/fetch_repository_content', type='json', auth='user', csrf=False)
    def fetch_repository_content(self, repo_id):
        repository = request.env['ssh.repository'].sudo().browse(repo_id)
        if repository:
            # repository.fetch_repository_content()
            repository_contents = request.env['product.template'].sudo().search([('ssh_repository_id', '=', repo_id)])
            data = []
            for content in repository_contents:
                content.write({'scanned': True})
                data.append({
                    'id': content.id,
                    'name': content.name,
                    'description': content.description,
                    'price': content.price,
                    'list_price':content.price,
                    'company_name': content.company_name,
                    'technical_name': content.technical_name,
                    'default_code': content.technical_name,
                    'odoo_versions': content.odoo_versions,
                    'repository_name': content.repository_name,
                    'icon_image': content.icon_image,
                    'ssh_repository_id': content.ssh_repository_id.id if content.ssh_repository_id else None,
                    'scanned': content.scanned
                })
        return json.dumps({'data': data})


    # @http.route('/scanned_apps', type='json', auth='user', csrf=False)
    # def scanned_apps_content(self):
    #     repository_contents = request.env['product.product'].sudo().search([('scanned', '=', True)])
    #     vals = []
    #     for content in repository_contents:
    #         vals.append({
    #             'id': content.id,
    #             'name': content.name,
    #             'description': content.description,
    #             'price': content.price,
    #             'company_name': content.company_name,
    #             'technical_name': content.technical_name,
    #             'odoo_versions': content.odoo_versions,
    #             'repository_name': content.repository_name,
    #             'icon_image': content.icon_image,
    #             'ssh_repository_id': content.ssh_repository_id.id if content.ssh_repository_id else None,
    #             'scanned':content.scanned
    #         })
    #     return vals

    @http.route('/scanned_apps', type='json', auth='user', csrf=False)
    def scanned_apps_content(self):
        repository_contents = request.env['product.template'].sudo().search(
            [('scanned', '=', True)])

        print("product id from template--------------------", repository_contents)
        vals = []
        for content in repository_contents:
            product = request.env['product.product'].sudo().search(
                [('product_tmpl_id', '=', content.id)], limit=1)
            print('product------------------scann------', product)
            vals.append({
                'id': content.id,
                'name': content.name,
                'description': content.description,
                'price': content.price,
                'company_name': content.company_name,
                'technical_name': content.technical_name,
                'odoo_versions': content.odoo_versions,
                'repository_name': content.repository_name,
                'icon_image': content.icon_image,
                'ssh_repository_id': content.ssh_repository_id.id if content.ssh_repository_id else None,
                'scanned': content.scanned,
                'product': product.id if product else None  # Include the product ID
            })
        return vals


    # @http.route(['/app-details/<int:app_id>'], type='http', auth='public', website=True, csrf=False)
    @http.route(['/app-details/<int:app_id>/<int:product_id>'], type='http', auth='public', website=True, csrf=False)
    def app_details(self, app_id,product_id, **kwargs):
        app = request.env['product.template'].sudo().browse(app_id)
        product = request.env['product.product'].sudo().browse(product_id)
        print("product details-------------------------------------------------",product.id)
        return request.render('odoo_infinity_app_store.view_app_template', {
            'app': app,
            'product': product,
            'product_id': product.id,
            'ssh_repository_id': product.ssh_repository_id.id,
            'index_url': '/odoo_infinity_app_store/static/src/js/index.html'

        })

    @http.route('/get_product_details', type='json', auth='public', website=True)
    def get_product_details(self, version=None, **kwargs):
        product_details = request.env['product.product'].sudo().search([('odoo_versions', 'like', version)])

        print("product details",product_details)



class AuthSignupHome(http.Controller):

    @http.route('/web/signup', type='http', auth='public', website=True ,csrf=False)
    def web_auth_signup(self, **post):

        return request.render('odoo_infinity_app_store.auth_signup_register_form',{})

    @http.route('/web/signup/submit', type='json', auth='public', website=True, csrf=False)
    def web_auth_signup_submit(self, **post):
        # Retrieve user input from the form
        name = post.get('name')
        email = post.get('login')
        password = post.get('password')
        github_account_name = post.get('github_account_name')
        print('github_account_name------------',github_account_name)

        user_exists = request.env['res.users'].sudo().search([('login', '=', email)])

        if user_exists:
            return {'error': 'An employee with this email already exists.'}
        else:
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password,
                'github_account_name': github_account_name,

            })
            print('new_user-----------------',new_user)

            return {'success': True}

class MyWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth='public', website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """ Add product to cart and update the cart quantity """
        order = request.website.sale_get_order(force_create=1)
        # product_id = 57
        product_id = int(product_id)
        print("============================================",product_id)
        add_qty = float(add_qty)

        if set_qty:
            set_qty = float(set_qty)
            order._cart_update(product_id=product_id, set_qty=set_qty)
        else:
            order._cart_update(product_id=product_id, add_qty=add_qty)

        return request.redirect('/shop/cart')



