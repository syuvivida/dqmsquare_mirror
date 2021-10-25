** Create personal VM:**
https://clouddocs.web.cern.ch/tutorial/openstack_command_line.html
openstack server create --key-name lxplus --flavor m2.small --image "CC7 - x86_64 [2021-10-01]" vmpmandrik
openstack server show vmpmandrik
openstack volume create --size 20 vopmandrik
openstack volume list
openstack server add volume vmpmandrik vopmandrik
openstack console url show vmpmandrik
Login via : ssh root@vmpmandrik.cern.ch

**Run locally (assuming different consoles):**  
mkdir tmp
python scripta/script_A.py
python scripta/script_B.py
`tmp` - is a an output folder

**Build docker image locally:**  
sudo systemctl start docker
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scripta:v1 scripta
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scriptb:v1 scriptb

**Run docker image locally: **  
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scripta:v1
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scriptb:v1
`-v ~/tmp:/tmp` - turn container /tmp into local ~/tmp

You can check not running docker image like:
docker run --entrypoint '/bin/sh' pmandrik/scripta:v1 -c 'ls; echo `pwd`;'

Shell access to the running container:
docker exec -it $CONTAINER_ID /bin/bash

**Push Images:**  
docker login
docker push pmandrik/scripta:v1
docker push pmandrik/scriptb:v1

**K8 testbed deployment (https://cms-http-group.docs.cern.ch/k8s_cluster/deploy-srv/):**  
Create OpenStack profile (https://clouddocs.web.cern.ch/tutorial/create_your_openstack_profile.html)
login lxplus8
Get testbed config:
export KUBECONFIG=/afs/cern.ch/user/m/mimran/public/cmsweb-k8s/config.cmsweb-test4
export OS_TOKEN=$(openstack token issue -c id -f value)
Check available clusters with `kubectl config get-clusters`
wget https://raw.githubusercontent.com/dmwm/CMSKubernetes/master/kubernetes/cmsweb/scripts/deploy-srv.sh
Modify it to work with local copy of scripta.yaml or push scripta.yaml to cmsweb repo :D
test4 is a DQM dedicated testbed ( https://cms-http-group.docs.cern.ch/k8s_cluster/cmsweb_developers_k8s_documentation/ )

First test - this way docker container will create output files in the container /tmp:
deploy-srv.sh scripta v1 test4  
Check the status: kubectl get pods -n default
To login to the pod: kubectl exec -it scripta-... sh -n default
To see logs of a pod: kubectl logs scripta-... -n default
To delete : kubectl delete pod scripta-6b4c867475-4xlzd - NOT WORKING
Check deployments: kubectl get deployments -n default
To delete : kubectl delete -n default deployment scripta

**K8 testbed deployment with eos **WIP**
Following https://cms-http-group.docs.cern.ch/k8s_cluster/eos/
Use scripta_eos.yaml
Check output /eos/project/c/cmsweb/www/dqm/k8test

**K8 testbed deployment with cephfs**
Create cephfs share volume: https://clouddocs.web.cern.ch/file_shares/quickstart.html
Get local enviroment of DQM project following: https://clouddocs.web.cern.ch/using_openstack/environment_options.html
Set enviroment:
. CMS_DQM_DC_openrc.sh
Create a share:
openstack share create --name myshare01 --share-type "Geneva CephFS Testing" CephFS 1
Check available share: manila list
Add manila access-allow myshare01  cephx cmsweb-auth
Get osShareID : manila list myshare01
Get osShareAccessID : manila access-list myshare01
osShareID & osShareAccessID Used in the k8 .yaml config
Get mount path : manila share-export-location-list myshare01 

Create docker image as usual:
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scripta_cephfs:v1 scripta_cephfs
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scripta_cephfs:v1
docker push pmandrik/scripta_cephfs:v1

Deploy to k8:
deploy-srv.sh scripta_cephfs v1 test4  

Mount at cluster:
ceph-fuse /cephfs/testbed/confdb-logs --id=cmsweb-auth --client-mountpoint=/volumes/_nogroup/9392e470-ef2c-4165-8caa-6063954e4e72













