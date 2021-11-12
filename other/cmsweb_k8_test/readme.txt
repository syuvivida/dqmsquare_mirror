** Create personal VM:**
https://clouddocs.web.cern.ch/tutorial/openstack_command_line.html
openstack server create --key-name lxplus --flavor m2.small --image "CC7 - x86_64 [2021-10-01]" vmname
openstack server show voname
openstack volume create --size 20 voname
openstack volume list
openstack server add volume vmname voname
openstack console url show vmname
Login via : 
ssh root@vmname.cern.ch

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
Check the status: 
kubectl get pods -n default
To login to the pod: 
kubectl exec -it dqmsquare-mirror-grabber-testbed-bc75d969c-675dc bash -n default
To see logs of a pod: 
kubectl logs scripta-... -n default
To delete : 
kubectl delete pod ${POD_NAME} - NOT WORKING
Check deployments: 
kubectl get deployments -n default
To delete : 
kubectl delete -n default deployment scripta
To get Pod logs: 
kubectl describe pods ${POD_NAME}

**K8 testbed deployment with eos **WIP**
Following https://cms-http-group.docs.cern.ch/k8s_cluster/eos/
Use scripta_eos.yaml
Check output /eos/project/c/cmsweb/www/dqm/k8test

**K8 testbed deployment with cephfs**
Create cephfs share volume: https://clouddocs.web.cern.ch/file_shares/quickstart.html
Get local enviroment of DQM project following: https://clouddocs.web.cern.ch/using_openstack/environment_options.html

For DQM DC cluster:
. CMS_DQM_DC_openrc.sh - for DQM DC project
Create a share:
openstack share create --name myshare01 --share-type "Geneva CephFS Testing" CephFS 1
Check available share: manila list
Add manila access-allow myshare01  cephx cmsweb-auth
Get osShareID : manila list
Get osShareAccessID : manila access-list myshare01
osShareID & osShareAccessID Used in the k8 .yaml config
Get mount path : manila share-export-location-list myshare01 

For CMSWEB K8 testbed clusters:
. CMS_WebtoolMig_openrc.sh
manila list
manila access-list pvc-c856be26-9de9-11e9-93c2-02163e01bcd6

Create docker image as usual:
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scripta_cephfs:v1 scripta_cephfs
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scripta_cephfs:v1
docker push pmandrik/scripta_cephfs:v1

Deploy to k8:
kubectl apply -f cephfs_claim.yaml
kubectl apply -f scripta_cephfs.yaml

Now not only the pods will be created but cephfs volumes and volums claims:
kubectl get pv -n default
kubectl get pvc -n default
To delete:
kubectl delete storageclass  dqmpv    --grace-period=0 --force
kubectl delete pv dqmpv    --grace-period=0 --force
kubectl delete pvc dqmpv  --grace-period=0 --force
To check:
kubectl describe storageclass  dqmpv
kubectl describe pvc  dqmpvc

Mount at cluster from any VM (check Install ceph-fuse (for CC7) if ceph-fuse is not installed):
ceph-fuse /cephfs/testbed/confdb-logs --id=cmsweb-auth --client-mountpoint=/volumes/_nogroup/9bac97f9-3e4e-4627-9e1b-d2666d14b8fc

** Install ceph-fuse (for CC7): **
Follow https://manjusri.ucsc.edu/2017/09/25/ceph-fuse/

Create config /etc/ceph/ceph.conf with following content (for Geneva testing share):
[global]
admin socket = /var/run/ceph/\$cluster-\$name-\$pid.asok
client reconnect stale = true
debug client = 0/2
fuse big writes = true
mon host = cephmond.cern.ch:6790

Create key config following 
https://clouddocs.web.cern.ch/file_shares/manual_cephfs.html
and 
https://github.com/dmwm/CMSKubernetes/blob/master/kubernetes/cmsweb/docs/storage.md











