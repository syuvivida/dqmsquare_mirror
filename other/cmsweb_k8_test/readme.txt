**Run locally (assuming different consoles):**  
mkdir tmp
python scripta/script_A.py
python scripta/script_B.py
`tmp` - is a an output folder

**Build docker image locally:**  
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scripta:v1 scripta
docker build --build-arg CMSK8S=http://cmsweb-testbed.cern.ch -t pmandrik/scriptb:v1 scriptb

**Run docker image locally: **  
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scripta:v1
docker run --rm -h `hostname -f` -v ~/tmp:/tmp -i -t pmandrik/scriptb:v1
`-v ~/tmp:/tmp` - turn container /tmp into local ~/tmp

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
export KUBECONFIG=$PWD/config.cmsweb-testbed4
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

**K8 testbed deployment with cephfs**
Create cephfs share volume: https://clouddocs.web.cern.ch/file_shares/quickstart.html
kubectl get storageclass
openstack share create --name myshare01 --share-type "Geneva CephFS Testing" CephFS 1



