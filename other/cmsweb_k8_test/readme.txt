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
get testbed config:
wget https://cernbox.cern.ch/index.php/s/o4pP0BKhNdbPhCv/download -O config.cmsweb-testbed4
export OS_TOKEN=$(openstack token issue -c id -f value)
export KUBECONFIG=$PWD/config.cmsweb-testbed4
Check available clusters with `kubectl config get-clusters`
wget https://raw.githubusercontent.com/dmwm/CMSKubernetes/master/kubernetes/cmsweb/scripts/deploy-srv.sh
test4 is a DQM dedicated testbed ( https://cms-http-group.docs.cern.ch/k8s_cluster/cmsweb_developers_k8s_documentation/ )
deploy-srv.sh pmandrik/scripta v1 test4
