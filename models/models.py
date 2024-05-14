import ast
import os
import requests
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
import random
import string


class SSHRepository(models.Model):
    _name = 'ssh.repository'
    _description = 'SSH Repository'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    ssh_url = fields.Char(string='SSH URL')
    repository_content = fields.One2many('github.repository.content', 'ssh_repository_id', string="Repository Contents")

    def fetch_repository_content(self):
        try:
            parts = self.ssh_url.split(':')[-1].split('/')
            print("=====parts=========",parts)
            username = parts[-2]
            repo_name = parts[-1].split('#')[0].replace('.git', '')
            print("=====username=========",username)
            print("=====repo_name=========",repo_name)
            branch = parts[-1].split('#')[1] if '#' in parts[-1] else 'master'
            print("=====branch=========",branch)

            url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
            response = requests.get(url, params={'ref': branch})
            if response.status_code == 200:
                contents = response.json()
                for content in contents:
                    if content['type'] == 'dir' and content['name'] != '__pycache__':
                        module_name = content['name']
                        print("==========module_name==========", module_name)
                        icon_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/static/description/icon.png"
                        print("==========icon_url=========",icon_url)
                        icon_response = requests.get(icon_url)
                        print("==========icon_response=========",icon_response)
                        icon_path = None
                        if icon_response.status_code == 200:
                            icon_data = icon_response.content
                            icon_filename = f"{module_name}_icon.png"
                            icon_attachment = self.env['ir.attachment'].create({
                                'name': icon_filename,
                                'type': 'binary',
                                'datas': base64.b64encode(icon_data),
                                'res_model': 'github.repository.content',
                                'res_id': self.id,
                            })
                            icon_path = f"/web/image/{icon_attachment.id}/icon_image"

                        manifest_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{module_name}/__manifest__.py"
                        manifest_response = requests.get(manifest_url)
                        if manifest_response.status_code == 200:
                            manifest_data = manifest_response.text
                            app_data = self._parse_manifest(manifest_data)
                            vals = {
                                'name': app_data['name'],
                                'description': app_data['description'],
                                'price': app_data['price'],
                                'company_name': app_data['company_name'],
                                'technical_name': module_name,
                                'odoo_versions': app_data['odoo_versions'],
                                'website': app_data['website'],
                                'depends': app_data['depends'],
                                'repository_name': repo_name,
                                'ssh_repository_id': self.id,
                                'icon_image': icon_path,
                            }
                            print("================Vals==================",vals)
                            existing_record = self.env['github.repository.content'].search(
                                [('technical_name', '=', module_name)])
                            if existing_record:
                                print("Record Is Already Exist")
                                existing_record.write(vals)
                            else:
                                self.env['github.repository.content'].create(vals)
                        else:
                            raise UserError(
                                f"Failed to fetch manifest file for module {module_name} in repository {repo_name} (branch: {branch}).")
            else:
                raise UserError(f"Failed to fetch contents for repository {repo_name} (branch: {branch}).")

        except Exception as e:
            print("Unexpected error:", str(e))

    def _parse_manifest(self, manifest_data):
        manifest_dict = ast.literal_eval(manifest_data)
        app_name = manifest_dict.get('name', '')
        app_description = manifest_dict.get('description', '')
        app_price = manifest_dict.get('price', 0.0)
        app_company_name = manifest_dict.get('author', '')
        app_technical_name = manifest_dict.get('technical_name', '')
        #
        app_version = manifest_dict.get('version', '0.0')
        major_minor_version = '.'.join(app_version.split('.')[:2])  # Extract major and minor version
        app_odoo_versions = major_minor_version if major_minor_version else '0.0'
        #
        # app_odoo_versions = manifest_dict.get('version', '')
        app_website = manifest_dict.get('website', '')
        app_depends = manifest_dict.get('depends', '')
        return {
            'name': app_name,
            'description': app_description,
            'price': app_price,
            'company_name': app_company_name,
            'technical_name': app_technical_name,
            'odoo_versions': app_odoo_versions,
            'website': app_website,
            'depends': app_depends,
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


class RepositoryContent(models.Model):
    _name = 'github.repository.content'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    company_name = fields.Char(string='Company Name')
    technical_name = fields.Char(string='Technical Name')
    odoo_versions = fields.Char(string='Odoo Versions')
    repository_name = fields.Char(string='Repository Name')
    ssh_repository_id = fields.Many2one('ssh.repository', string="SSH Repository")
    icon_image = fields.Char(string="Icon Path")
    scanned = fields.Boolean(string="Scanned", default=False)
    website = fields.Char(string="website")
    depends = fields.Char(string="Depended Modules")


