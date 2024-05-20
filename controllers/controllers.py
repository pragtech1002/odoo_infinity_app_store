import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from werkzeug.exceptions import NotFound

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

    # @http.route('/fetch_scanned_value', type='json', auth='user')
    # def fetch_scanned_value(self,repo_id):
    #     scanned_value = request.env['github.repository.content'].sudo().search([('ssh_repository_id', '=', repo_id)])
    #     scanned = [{'id': record.id, 'scanned': record.scanned} for record in scanned_value]
    #     print("-----------------------------scanned-----------------------------------", scanned)
    #     return scanned

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
            repository_contents = request.env['product.template'].sudo().search(
                [('ssh_repository_id', '=', repo_id)])
            data = []
            for content in repository_contents:
                content.write({'scanned': True})
                data.append({
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
                    'scanned': content.scanned
                })
        return json.dumps({'data': data})


    @http.route('/scanned_apps', type='json', auth='user', csrf=False)
    def scanned_apps_content(self):
        repository_contents = request.env['product.template'].sudo().search(
            [('scanned', '=', True)])
        vals = []
        for content in repository_contents:
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
                'scanned':content.scanned
            })
        return vals

    @http.route('/get_scanning_status', type='json', auth='user', csrf=False)
    def get_scanning_status(self, repo_id):
        # Fetch the repository content based on the provided repo_id
        repository_content = request.env['product.template'].sudo().search(
            [('ssh_repository_id', '=', repo_id), ('scanned', '=', True)], limit=1)

        if repository_content:
            # Check if the repository content has been scanned
            scanned = repository_content.scanned
        else:
            scanned = False

        return json.dumps({'scanned': scanned})

    @http.route('/app-details/<int:app_id>', type='http', auth="public", website=True, csrf=False)
    def app_details(self, app_id, **kwargs):
        app = request.env['product.template'].sudo().browse(app_id)
        return request.render('odoo_infinity_app_store.view_app_template', {'app': app})

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
            # ssh_key = request.env['res.users']
            # print('ssh_key------------',ssh_key)
            # public_ssh_key = self.generate_ssh_keypair()
            # print('public_ssh_key-------------controller------',public_ssh_key)
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'password': password,
                'github_account_name': github_account_name,

            })
            print('new_user-----------------',new_user)

            return {'success': True}

    @http.route(['/shop/cart/update'], type='http', auth="public", website=True,csrf=False)
    def cart_update_custom(self, product_id, add_qty=None, set_qty=None, **kw):
        # Call the original cart_update method to add the product to the cart
        res = super(AuthSignupHome, self).cart_update(product_id, add_qty, set_qty, **kw)
        print("Upadated Cart Details",res)

        # Redirect to the cart view after adding the product to the cart
        return request.redirect('/shop/app_cart')

    @http.route('/shop/app_cart', type='http', auth='public', website=True,csrf=False)
    def cart_view(self, **kwargs):
        # Render the template
        return http.request.render('your_module_name.inherit_cart_lines', {})














