---
title:  "Building Kubernetes on Proxmox with Ansible & Teraform for the Homelabs"
layout: post
published: false
---

[ClusterCreator: Terraform & Ansible K8S Bootstrapping on Proxmox](https://github.com/mcgarrah/ClusterCreator) by Jairus Christensen looks like an amazing opportunity for me to get a Kuberetes Cluster running in the Homelab with my existing Proxmox Cluster.

From Jairus README.md

``` text
ClusterCreator automates the creation and maintenance of fully functional Kubernetes (K8S) clusters of any size on Proxmox. Leveraging Terraform/OpenTofu and Ansible, it facilitates complex setups, including decoupled etcd clusters, diverse worker node configurations, and optional integration with Unifi networks and VLANs.

Having a virtualized K8S cluster allows you to not only simulate a cloud environment but also scale and customize your cluster to your needs—adding or removing nodes and disks, managing backups and snapshots of the virtual machine disks, customizing node class types, and controlling state.
```

<!-- excerpt-end -->

This is were I write stuff down.

[Introducing ClusterCreator: K8s on Proxmox using Terraform and Ansible](https://cyber-engine.com/blog/2024/06/25/k8s-on-proxmox-using-clustercreator/)

[Fully Functional K8s on Proxmox using Terraform and Ansible](https://www.reddit.com/r/homelab/comments/1fcui9f/fully_functional_k8s_on_proxmox_using_terraform/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

## Terraform / OpenTofu

This terraform uses the [Terraform Provider for Proxmox VE](https://github.com/bpg/terraform-provider-proxmox) module.

You can see the [TF Statefile using S3 with Minio](https://github.com/christensenjairus/ClusterCreator/blob/main/terraform/providers.tf#L36C1-L50C4). This needs to be replaced.

TF Statefile storage in Minio S3 or something else...

To store a Terraform state file in CephFS, you need to configure a remote backend in your Terraform configuration, specifying CephFS as the storage location, allowing you to access the state file from your CephFS cluster instead of storing it locally on your machine; essentially, you're using CephFS as a remote storage for your Terraform state data. 

``` HCL
terraform {
  backend "remote-exec" {
    # Replace with your CephFS details
    #directory = "/shared/terraform-state"
    #key = "terraform.tfstate"
    path = "/mnt/pve/cephfs/tfcluster/terraform.tfstate"
  }
}
```

[Terraform Variables File](https://github.com/christensenjairus/ClusterCreator/blob/main/terraform/variables.tf) has settings.

``` HCL
locals {
    proxmox_host   = "10.0.0.100"
    proxmox_node   = "Citadel"
    template_vm_id = 9000
#     unifi_api_url  = "https://10.0.0.1/"
#     minio_endpoint = "https://s3.christensencloud.us"
#     minio_region   = "default"
#     minio_bucket   = "terraform-state"
}
```

The cluster types of `alpha`, `beta`, and `gamma` are found in [clusters.tf](https://github.com/christensenjairus/ClusterCreator/blob/main/terraform/clusters.tf#L80) as the default.

## Ansible

There is a bit of Ansible in here as well for configuration of the VMs.

[Ansible Configuration file](https://github.com/christensenjairus/ClusterCreator/blob/main/scripts/k8s.env) has some interesting settings.

`PROXMOX_DISK_DATASTORE` would have to change to the ceph datastore and same for `PROXMOX_ISO_PATH` to get it in the right place.

``` INI
### -------------------------------------------------------
### --------------General Template Config------------------
### -------------------------------------------------------

NON_PASSWORD_PROTECTED_SSH_KEY="id_rsa" # assumed that this is in ~/.ssh/ and the .pub file is named similarly
PROXMOX_USERNAME=root
PROXMOX_HOST="10.0.0.100"
PROXMOX_DISK_DATASTORE="local-btrfs"
PROXMOX_BACKUPS_DATASTORE="hdds"
PROXMOX_ISO_PATH="/var/lib/pve/local-btrfs/template/iso"
TIMEZONE="America/Denver"
TEMPLATE_VM_BRIDGE=vmbr0
TEMPLATE_VM_GATEWAY="10.0.0.1"
TEMPLATE_VM_IP="10.0.0.10/24"
TEMPLATE_VM_SEARCH_DOMAIN="lan"
TEMPLATE_VLAN_TAG="None" # None if no vlan, otherwise the vlan tag (e.g. 100)
TWO_DNS_SERVERS="1.1.1.1 1.0.0.1"
TEMPLATE_VM_CPU_TYPE="x86-64-v3"
TEMPLATE_VM_CPU=8
TEMPLATE_VM_MEM=8192

### -------------------------------------------------------
### --------------PKGS to Install with APT-----------------
### ---kubectl, kubeadm, and kubelet use the k8s version---
### -----`apt-cache madison <package>` to find versions----
### -------------------------------------------------------

KUBERNETES_SHORT_VERSION=1.32
KUBERNETES_MEDIUM_VERSION=1.32.1
KUBERNETES_LONG_VERSION=1.32.1-1.1

# ------------------- Addon Versions ----------------------

CILIUM_VERSION=1.16.6
KUBELET_SERVING_CERT_APPROVER_VERSION=0.9.0
LOCAL_PATH_PROVISIONER_VERSION=0.0.31
METRICS_SERVER_VERSION=3.12.2
METALLB_VERSION=0.14.9

# ----------------NVIDIA Drivers (optional)----------------
# To find versions on Ubuntu:
#   apt search nvidia-driver | grep -E '^nvidia-driver-[0-9]+-server' | cut -d '/' -f 1
# Versions on Debian:
#   Bookworm only has 535.
#   Bullseye has both 470 & 390. For 390 you'll need to tweak apt-packages.sh
#     to install `nvidia-legacy-390xx-driver` instead of `nvidia-drivers`.
#     For debian, the version specified below will be ignored, and it will
#     install whichever nvidia driver version matches the debian release.
# Adds substantial creation time & disk utilization for the template vm.
# To install, uncomment the line below and increase TEMPLATE_DISK_SIZE.

#NVIDIA_DRIVER_VERSION=535

### -------------------------------------------------------
### --------------PKGS to Download Directly----------------
### -----Find these directly on GitHub Release Pages-------
### -------------------------------------------------------

CNI_PLUGINS_VERSION=1.6.0
ETCD_VERSION=3.5.16

# The template vm's cpu/mem resources only matter for initial creation.
# More cpu greatly speeds up nvidia driver installation.

### -------------------------------------------------------
### -------------Template Image selection------------------
### This project only supports debian & ubuntu based images
### Some pkg versions may be different for different images
### -------------------------------------------------------

# As a speed optimization, the disk size is set to be just large enough to fit
#   the image and the k8s pkgs to help with vm cloning speed. The k8s installation
#   ansible will check to make sure there wasn't any disk space issues during the
#   template creation process.

### Debian 12 Image (Bookworm)
TEMPLATE_VM_ID=9000
TEMPLATE_VM_NAME="k8s-ready-template"
IMAGE_NAME="debian-12-generic-amd64.qcow2"
IMAGE_LINK="https://cloud.debian.org/images/cloud/bookworm/latest/${IMAGE_NAME}"
EXTRA_TEMPLATE_TAGS="bookworm template"
TEMPLATE_DISK_SIZE=4.6G # Add 1.6G more if installing nvidia drivers

### Ubuntu 24.04 LTS Image (Noble Numbat)
#TEMPLATE_VM_ID=9000
#TEMPLATE_VM_NAME="k8s-ready-template"
#IMAGE_NAME="ubuntu-24.04-server-cloudimg-amd64.img"
#IMAGE_LINK="https://cloud-images.ubuntu.com/releases/24.04/release/${IMAGE_NAME}"
#EXTRA_TEMPLATE_TAGS="24.04-lts template"
#TEMPLATE_DISK_SIZE=5.6G # Add 1.8G more if installing nvidia drivers

### -------------------------------------------------------
```
