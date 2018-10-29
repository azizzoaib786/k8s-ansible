# Provisioning Kubernetes on AWS

These Ansible playbooks aim to facilitate the creation of K8s cluster using Kops on AWS.

> *Disclaimer: this is a Working in Progress. Several configurations will be changed in the near future.*

## Requirements

### Kubectl

```bash
# From https://kubernetes.io/docs/tasks/tools/install-kubectl/

# macOS
brew install kubernetes-cli

# Linux
# Check on documentation. There are repositories available to Ubuntu/Debian or CentOS/RHEL
```

### Kops

```bash
# From https://kubernetes.io/docs/setup/custom-cloud/kops/#creating-a-cluster

curl -OL https://github.com/kubernetes/kops/releases/download/1.10.0/kops-darwin-amd64
chmod +x kops-darwin-amd64
mv kops-darwin-amd64 /usr/local/bin/kops

# you can also install using Homebrew
brew update && brew install kops
```

### Ansible

```bash
# From https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

# I suggest use virtualenv
sudo pip install ansible
```

### AWS CLI

```bash
# From https://docs.aws.amazon.com/cli/latest/userguide/installing.html

# I suggest use virtualenv
pip install awscli --upgrade --user
```

## Basic Usage

### Create cluster

```
ansible-playbook create-cluster.yaml --extra-vars "env_name=<cluster-file-name>"
```

### Delete cluster

```
ansible-playbook delete-cluster.yaml --extra-vars "env_name=<cluster-file-name>"
```

## How to create a new cluster

In order to create a new cluster, it is necessary to create a new cluster profile.

```bash
$ touch kops-cluster/my_profile.yaml
```

On this profile, it is necessary to set the following parameters:

| Parameter | Description | Default |
|-|-|-|
| cluster_name  | Name of cluster | Not set |
| aws_region | AWS region  | 'eu-west-1' |
| aws_zones | AWS zones | 'eu-west-1a,eu-west-1b,eu-west-1c' |
| kops_state_bucket | Bucket name where cluster state is stored | kops-state-bkt |
| master_size | Set instance size for masters | t2.medium |
| master_volume_size | Set instance volume size (in GB) for master | 50 |
| master_count | Set the number of masters | 1 |
| node_size | Set instance size for nodes | t2.medium |
| nodes_count | Set the number of nodes | 3 |
| node_volume_size | Set instance volume size (in GB) for nodes | 50 |
| dns_zone | DNS hosted zone to use | example.com |
| kube_version | Version of kubernetes to run | 1.10.7 |

> *Only cluster_name is mandatory. If nothing else is set, a cluster with 1 master + 3 nodes will be deployed.*

After setting profile file, it is necessary to run create-cluster playbook.

```bash
$ ansible-playbook create-cluster.yaml --extra-vars "env_name=my_profile"
```

## Advanced configs

There are configurations that can be set on K(ops)ubernetes cluster, but are not available through kops cli. It is possible to set such configurations creating yaml files on the following directories: *cluster.conf.d*, *master.conf.d* and *node.conf.d*. The directory name specifies where those configurations will be included.

Cluster configurations can be found in https://github.com/kubernetes/kops/blob/master/docs/cluster_spec.md
