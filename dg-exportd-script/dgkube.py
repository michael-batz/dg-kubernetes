#!/usr/bin/python3

import json
import os
import subprocess
import sys
import jinja2

def main():
    # get input from DATAGERRY via stdin
    input_data = json.loads(sys.stdin.read())

    # prepare jinja2 environment
    jinja_tpl_dir = os.path.join(os.path.dirname(__file__),"templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(jinja_tpl_dir))

    # init variables
    defined_apps = []

    # iterate over all DATAGERRY objects
    for dg_object in input_data:
        app_id = dg_object['variables']['app_id']
        # prepare jinja template
        template_data = {}
        template_data['app_id'] = app_id
        template_data['app_version'] = dg_object['variables']['app_version']
        template_data['adminpw'] = dg_object['variables']['init_admin_pw']
        template_data['hostname'] = dg_object['variables']['hostname']
        jinja_tpl = jinja_env.get_template('datagerry-kubernetes.yml.tpl')
        kube_defs = jinja_tpl.render(template_data)

        # send kubernetes definitions via kubectl to a cluster (create/update apps)
        subprocess.run(['/usr/local/bin/kubectl', 'apply', '-f-'], input=kube_defs, check=True, encoding='utf8')

        # save app_id in defined apps
        defined_apps.append(app_id)

    # get all provisioned apps

if __name__ == '__main__':
    main()
