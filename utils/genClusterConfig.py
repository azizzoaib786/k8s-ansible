#!/usr/bin/env python3


import os
import sys
import yaml
import glob
import subprocess
import argparse

def combineDicts(dictionary1, dictionary2):
    output = {}
    for item, value in dictionary1.items():
        if item in dictionary2:
            if isinstance(dictionary2[item], dict):
                output[item] = combineDicts(value, dictionary2.pop(item))
        else:
            output[item] = value
    for item, value in dictionary2.items():
         output[item] = value
    return output

def exportConfig(component, cluster_name, cluster_state):

    if component == 'cluster':
        data = yaml.load(subprocess.getoutput(
            "kops get cluster --name={0} --state={1} -oyaml".format(
                cluster_name, cluster_state)))

    elif component == 'ig':
        data = yaml.load(subprocess.getoutput(
            "kops get ig nodes --name={0} --state={1} -oyaml".format(
                cluster_name, cluster_state)))

    elif component == 'nodes':
        data = yaml.load(subprocess.getoutput(
            "kops get nodes --name={0} --state={1} -oyaml".format(
                cluster_name, cluster_state)))

    elif 'master' in component:
        data = yaml.load(subprocess.getoutput(
            "kops get ig {0} --name={1} --state={2} -oyaml".format(
                component, cluster_name, cluster_state)))
    else:
        return None

    if 'instancegroup not found' in data: sys.exit(0)
    if 'metadata' in data:
      del data['metadata']['creationTimestamp']
    return data

def load_cluster_config(cluster_name, cluster_config, cluster_state, component='cluster'):
    if cluster_config is None and cluster_name is None:
        print("I don't know how to get the cluster config")
        sys.exit(1)

    conf = None
    if cluster_name:
        conf = exportConfig(component, cluster_name, cluster_state)
    elif cluster_config:
        if not os.path.exists(cluster_config):
            print("%s does not exist" % (cluster_config))
            return None
        with open(cluster_config, 'r') as f:
            conf = yaml.load(f)
    return conf

def mergeSnippets(cluster_config, snippets_path):
    new_conf = cluster_config
    for sn in glob.glob(os.path.join(snippets_path, '*.yaml')):
        print("Loading %s" % (sn))
        with open(sn, 'r') as f:
            snData = yaml.load(f)
        new_conf = combineDicts(new_conf, snData)
    return new_conf

def saveConfigToFile(conf, dest):
    try:
        with open(dest, 'w+') as f:
            f.write(yaml.dump(conf, default_flow_style = False))
    except:
        print("Cannot save config to %s" % (dest))
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kops config snippets merger')
    parser.add_argument('--conf-path',
        help='Path to the conf.d dir with all the snippets', required=True)
    parser.add_argument('--cluster-name', required=False)
    parser.add_argument('--cluster-state',
        help='S3 bucket used by KOPS to store state', required=False),
    parser.add_argument('--cluster-config', required=False)
    parser.add_argument('--output', default=None, required=False)
    parser.add_argument('--component',
        help='cluster, ig or nodes', default='cluster')

    args = parser.parse_args()

    conf = load_cluster_config(
        cluster_config=args.cluster_config,
        cluster_name=args.cluster_name,
        cluster_state=args.cluster_state,
        component=args.component)

    new_conf = mergeSnippets(conf, args.conf_path)

    if not args.output is None:
        saveConfigToFile(new_conf, args.output)
        print("New config saved to %s" % (args.output))
