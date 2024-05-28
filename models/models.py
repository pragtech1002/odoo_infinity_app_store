import ast
import requests
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
import paramiko
import re


class ResUsers(models.Model):
    _inherit = 'res.users'

    public_ssh_key = fields.Char(string='Public SSH Key')
    github_account_name = fields.Char(string='GitHub Account Name')

    @staticmethod
    def generate_ssh_keypair():
        key_filename = 'my_ssh_key'  # Default key filename
        passphrase = 'my_passphrase'  # Default passphrase, optional

        key = paramiko.RSAKey.generate(2048)
        # Save the private key to a file
        key.write_private_key_file(key_filename, password=passphrase)
        # Get the public key string
        public_key_string = f"ssh-rsa {key.get_base64()}"
        print('public_key_string----------------------', public_key_string)
        # Append the public key to the private key file
        with open(key_filename + '.pub', 'w') as pubkey_file:
            pubkey_file.write(public_key_string)

        print(
            f"SSH key pair generated successfully. Private key: {key_filename}, Public key appended to the same file.")
        return public_key_string  # Usage

    @api.model
    def create(self, values):
        store_sshkey = self.generate_ssh_keypair()
        print('store_sshkey--------------------', store_sshkey)
        user = super(ResUsers, self).create(values)
        user.write({'public_ssh_key': store_sshkey})
        return user


class SSHRepository(models.Model):
    _name = 'ssh.repository'
    _description = 'SSH Repository'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    ssh_url = fields.Char(string='SSH URL')
    repository_content = fields.One2many('product.template', 'ssh_repository_id', string="Repository Contents")

    def fetch_repository_content(self):
        try:
            # Parse the SSH URL
            parts = self.ssh_url.split(':')[-1].split('/')
            username = parts[-2]
            repo_name = parts[-1].split('#')[0].replace('.git', '')
            branch = parts[-1].split('#')[1] if '#' in parts[-1] else 'master'

            # Construct the GitHub API URL
            url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
            response = requests.get(url, params={'ref': branch})

            # Log the response status and URL
            print(f"Fetching URL: {url}")
            print(f"Response Status Code: {response.status_code}")

            if response.status_code == 200:
                contents = response.json()
                for content in contents:
                    if content['type'] == 'dir' and content['name'] != '__pycache__':
                        module_name = content['name']

                        # Fetch Index HTML
                        index_html_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/static/description/index.html"
                        index_html_response = requests.get(index_html_url)
                        index_html_content = index_html_response.text if index_html_response.status_code == 200 else None

                        # Update image paths in index.html content
                        if index_html_content:
                            updated_html_content = self._update_image_paths(index_html_content, username, repo_name,
                                                                            branch, module_name)
                            index_html_content = updated_html_content

                        # Fetch other resources and metadata
                        gif_path, icon_path, license_text_content = self._fetch_additional_resources(username,
                                                                                                     repo_name, branch,
                                                                                                     module_name)

                        # Fetch Manifest
                        manifest_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/__manifest__.py"
                        manifest_response = requests.get(manifest_url)

                        if manifest_response.status_code == 200:
                            manifest_data = manifest_response.text
                            app_data = self._parse_manifest(manifest_data)

                            # Search or create 'Odoo Version' attribute and value
                            odoo_version_attribute = self.env['product.attribute'].search(
                                [('name', '=', 'Odoo Version')], limit=1)
                            if not odoo_version_attribute:
                                odoo_version_attribute = self.env['product.attribute'].create({'name': 'Odoo Version'})

                            odoo_version_value = self.env['product.attribute.value'].search(
                                [('name', '=', app_data['odoo_versions']),
                                 ('attribute_id', '=', odoo_version_attribute.id)], limit=1)

                            if not odoo_version_value:
                                odoo_version_value = self.env['product.attribute.value'].create({
                                    'name': app_data['odoo_versions'],
                                    'attribute_id': odoo_version_attribute.id
                                })

                            # Prepare the values to be updated/created
                            vals = {
                                'name': app_data['name'],
                                'description': app_data['description'],
                                'price': app_data['price'],
                                'company_name': app_data['company_name'],
                                'technical_name': module_name,
                                'odoo_versions': app_data['odoo_versions'],
                                'website': app_data['website'],
                                'depends': app_data['depends'],
                                'category': app_data['category'],
                                'currency': app_data['currency'],
                                'license': app_data['license'],
                                'repository_name': repo_name,
                                'ssh_repository_id': self.id,
                                'icon_image': icon_path,
                                'gif_image': gif_path,
                                'index_html_content': index_html_content,
                                'license_text_content': license_text_content,
                            }

                            # Check if the product template already exists
                            existing_product = self.env['product.template'].search(
                                [('technical_name', '=', module_name)], limit=1)
                            if existing_product:
                                print("===========existing_product====template=============",existing_product)
                                # Check if the attribute line exists
                                attribute_line = self.env['product.template.attribute.line'].search(
                                    [('product_tmpl_id', '=', existing_product.id),
                                     ('attribute_id', '=', odoo_version_attribute.id)], limit=1)

                                if attribute_line:
                                    # Add the value if it doesn't already exist
                                    if odoo_version_value.id not in attribute_line.value_ids.ids:
                                        attribute_line.write({'value_ids': [(4, odoo_version_value.id)]})
                                else:
                                    # Create the attribute line if it doesn't exist
                                    existing_product.write({
                                        'attribute_line_ids': [(0, 0, {
                                            'attribute_id': odoo_version_attribute.id,
                                            'value_ids': [(6, 0, [odoo_version_value.id])]
                                        })]
                                    })
                            else:
                                # Create the product template and attribute line
                                vals['attribute_line_ids'] = [(0, 0, {
                                    'attribute_id': odoo_version_attribute.id,
                                    'value_ids': [(6, 0, [odoo_version_value.id])]
                                })]
                                existing_product = self.env['product.template'].create(vals)

                            # Update or create product.product entries
                            product_product_data = self.env['product.product'].search([
                                ('product_tmpl_id', '=', existing_product.id),
                                ('product_template_attribute_value_ids.attribute_id', '=', odoo_version_attribute.id),
                                ('product_template_attribute_value_ids.product_attribute_value_id', '=',
                                 odoo_version_value.id)
                            ])

                            if product_product_data:
                                product_product_data.write(vals)
                                print("========product_product_data============",product_product_data)
                            else:
                                self.env['product.product'].create({
                                    'product_tmpl_id': existing_product.id,
                                    **vals
                                })
                        else:
                            raise UserError(
                                f"Failed to fetch manifest file for module {module_name} in repository {repo_name} (branch: {branch}).")
            else:
                raise UserError(
                    f"Failed to fetch contents for repository {repo_name} (branch: {branch}). Status Code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print("Unexpected error:", str(e))

    def _update_image_paths(self, html_content, username, repo_name, branch, module_name):
        # Use regex to replace image src paths
        img_src_pattern = re.compile(r'src="([^"]+)"')
        updated_html_content = img_src_pattern.sub(
            lambda
                match: f'src="https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/static/description/{match.group(1)}"',
            html_content)
        return updated_html_content

    def _fetch_additional_resources(self, username, repo_name, branch, module_name):
        # Fetch GIF
        gif_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/static/description/{module_name}.gif"
        gif_response = requests.get(gif_url)
        gif_path = None
        if gif_response.status_code == 200:
            gif_data = gif_response.content
            gif_filename = f"{module_name}.gif"
            gif_attachment = self.env['ir.attachment'].create({
                'name': gif_filename,
                'type': 'binary',
                'datas': base64.b64encode(gif_data),
                'res_model': 'product.template',
                'res_id': self.id,
            })
            gif_path = f"/web/image/{gif_attachment.id}/gif_image"

        # Fetch Icon
        icon_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/static/description/icon.png"
        icon_response = requests.get(icon_url)
        icon_path = None
        if icon_response.status_code == 200:
            icon_data = icon_response.content
            icon_filename = f"{module_name}_icon.png"
            icon_attachment = self.env['ir.attachment'].create({
                'name': icon_filename,
                'type': 'binary',
                'datas': base64.b64encode(icon_data),
                'res_model': 'product.template',
                'res_id': self.id,
            })
            icon_path = f"/web/image/{icon_attachment.id}/icon_image"

        # Fetch License
        license_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/LICENSE"
        license_response = requests.get(license_url)
        license_text_content = license_response.text if license_response.status_code == 200 else None

        return gif_path, icon_path, license_text_content

    def _parse_manifest(self, manifest_data):
        manifest_dict = ast.literal_eval(manifest_data)
        app_name = manifest_dict.get('name', '')
        app_description = manifest_dict.get('description', '')
        app_price = manifest_dict.get('price', 0.0)
        app_company_name = manifest_dict.get('author', '')
        app_technical_name = manifest_dict.get('technical_name', '')
        app_version = manifest_dict.get('version', '0.0')
        major_minor_version = '.'.join(app_version.split('.')[:2])  # Extract major and minor version
        app_odoo_versions = major_minor_version if major_minor_version else '0.0'
        app_website = manifest_dict.get('website', '')
        app_depends = manifest_dict.get('depends', '')
        app_category = manifest_dict.get('category', '')
        app_currency = manifest_dict.get('currency', '')
        app_license = manifest_dict.get('license', '')

        return {
            'name': app_name,
            'description': app_description,
            'price': app_price,
            'company_name': app_company_name,
            'technical_name': app_technical_name,
            'odoo_versions': app_odoo_versions,
            'website': app_website,
            'depends': app_depends,
            'category': app_category,
            'currency': app_currency,
            'license': app_license,
        }


    @api.model
    def create(self, vals):
        try:
            if not vals.get('ssh_url'):
                raise UserError("SSH URL is required.")

            if not vals.get('ssh_url').startswith('ssh://'):
                raise UserError("SSH URL must start with 'ssh://'.")

            parts = vals['ssh_url'].split(':')[-1].split('/')
            if len(parts) < 2:
                raise UserError("Invalid SSH URL format.")

            username = parts[-2]
            repo_name = parts[-1].split('#')[0].replace('.git', '')
            if not repo_name:
                raise UserError("Repository name is required.")

            branch = parts[-1].split('#')[1] if '#' in parts[-1] else None
            if not branch:
                raise UserError("Branch name is required after the '#' symbol.")

            url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
            response = requests.get(url, params={'ref': branch})
            if response.status_code != 200:
                raise UserError(f"Failed to fetch contents for repository {repo_name} (branch: {branch}).")

            account = super(SSHRepository, self).create(vals)
            account.fetch_repository_content()

            return account
        except UserError as e:
            raise e

    @api.onchange('ssh_url')
    def onchange_ssh_url(self):
        try:
            if not self.ssh_url:
                return

            if not self.ssh_url.startswith('ssh://'):
                raise UserError("SSH URL must start with 'ssh://'.")

            parts = self.ssh_url.split(':')[-1].split('/')
            if len(parts) < 2:
                raise UserError("Invalid SSH URL format.")

            username = parts[-2]
            repo_name = parts[-1].split('#')[0].replace('.git', '')
            if not repo_name:
                raise UserError("Repository name is required.")

            branch = parts[-1].split('#')[1] if '#' in parts[-1] else None
            if not branch:
                raise UserError("Branch name is required after the '#' symbol.")

            url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
            response = requests.get(url, params={'ref': branch})
            if response.status_code != 200:
                raise UserError(f"Failed to fetch contents for repository {repo_name} (branch: {branch}).")

            self.fetch_repository_content()
        except UserError as e:
            raise e


class ProductProduct(models.Model):
    _inherit = 'product.template'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    company_name = fields.Char(string='Company Name')
    technical_name = fields.Char(string='Technical Name')
    odoo_versions = fields.Char(string='Odoo Versions')
    repository_name = fields.Char(string='Repository Name')
    ssh_repository_id = fields.Many2one('ssh.repository', string="SSH Repository")
    icon_image = fields.Char(string="Icon Path")
    #
    gif_image = fields.Char(string="GIF Image Path")
    #
    scanned = fields.Boolean(string="Scanned", default=False)
    website = fields.Char(string="website")
    depends = fields.Char(string="Depended Modules")
    category = fields.Char(string="Category")
    currency = fields.Char(string="Currency")
    license = fields.Char(string="License")
    index_html_content = fields.Text(string="Index HTML Content")
    license_text_content = fields.Text(string="License Text Content")
    ispublished = fields.Boolean(string="ispublished", default=False)
    isunpublished = fields.Boolean(string="isunpublished", default=False)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    template_id = fields.Many2one('product.template', string='Product Template')
    # Inherit the necessary fields from product.template
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    company_name = fields.Char(string='Company Name')
    technical_name = fields.Char(string='Technical Name')
    odoo_versions = fields.Char(string='Odoo Versions')
    repository_name = fields.Char(string='Repository Name')
    ssh_repository_id = fields.Many2one('ssh.repository', string="SSH Repository")
    icon_image = fields.Char(string="Icon Path")
    #
    gif_image = fields.Char(string="GIF Image Path")
    #
    scanned = fields.Boolean(string="Scanned", default=False)
    website = fields.Char(string="website")
    depends = fields.Char(string="Depended Modules")
    category = fields.Char(string="Category")
    currency = fields.Char(string="Currency")
    license = fields.Char(string="License")
    index_html_content = fields.Text(string="Index HTML Content")
    license_text_content = fields.Text(string="License Text Content")
    ispublished = fields.Boolean(string="ispublished", default=False)
    isunpublished = fields.Boolean(string="isunpublished", default=False)
