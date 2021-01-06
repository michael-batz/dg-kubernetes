#!/usr/bin/python3

import argparse
import json
import os
import subprocess
import sys
import jinja2

def main():
    # get input from DATAGERRY via stdin
    input_data = json.loads(sys.stdin.read())

    # get arguments
    #parser = argparse.ArgumentParser()
    #parser.add_argument('appname', type=str, help='appname label')
    #args.parser.parse_args()

    # prepare jinja2 environment
    jinja_tpl_dir = os.path.join(os.path.dirname(__file__),"templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(jinja_tpl_dir))

    # init variables
    #app_name = args.appname
    app_name = 'datagerry-demo'
    app_ids = []

    # iterate over all DATAGERRY objects
    for dg_object in input_data:
        app_id = dg_object['variables']['app_id']
        # prepare jinja template
        template_data = {}
        template_data['app_id'] = app_id
        template_data['app_name'] = app_name
        template_data['app_version'] = dg_object['variables']['app_version']
        template_data['adminpw'] = dg_object['variables']['init_admin_pw']
        template_data['hostname'] = dg_object['variables']['hostname']
        jinja_tpl = jinja_env.get_template('datagerry-kubernetes.yml.tpl')
        kube_defs = jinja_tpl.render(template_data)

        # send kubernetes definitions via kubectl to a cluster (create/update apps)
        subprocess.run(['/usr/local/bin/kubectl', 'apply', '-f-'], input=kube_defs, check=True, encoding='utf8')

        # save app_id in defined apps
        app_ids.append(app_id)

    # get all provisioned app_ids with the defined appname
    result = subprocess.run(['/usr/local/bin/kubectl', 'get', 'services,statefulsets,deployments,ingress,pvc', 
                             '-l appname=' + app_name, '-o=jsonpath={.items[*][\'metadata.labels.appid\']}'],
                             check=True, encoding='utf8', stdout=subprocess.PIPE)
    provisioned_appids = set(result.stdout.split(' '))

    # check which appids are on kubernetes but not defined in DATAGERRY and remove them
    for app_id in app_ids:
        provisioned_appids.remove(app_id)
    # remove services, statefulsets, deployments and ingress objects
    for app_id in provisioned_appids:
        subprocess.run(['/usr/local/bin/kubectl', 'delete', 'services,statefulsets,deployments,ingress',
                        '-l appid=' + app_id + ',appname=' + app_name], check=True, encoding='utf8')
    # remove pvc objects in an own step, as there is some waiting time until deployments/statefulsets are removed
    for app_id in provisioned_appids:
        subprocess.run(['/usr/local/bin/kubectl', 'delete', 'pvc',
                        '-l appid=' + app_id + ',appname=' + app_name], check=True, encoding='utf8')



if __name__ == '__main__':
    main()
