# Petr~S.~Mandrik, 2021, IHEP, https://github.com/pmandrik

from diagrams import Cluster, Diagram, Edge
from diagrams.programming.flowchart import InputOutput as nIO
from diagrams.programming.flowchart import Action      as nA
from diagrams.programming.flowchart import StartEnd    as nSE
from diagrams.programming.flowchart import MultipleDocuments as nMD
from diagrams.programming.flowchart import OffPageConnectorLeft as nL
from diagrams.programming.flowchart import OffPageConnectorRight as nR

graph_attr = {"fontsize": "45"}
node_attr  = {"fontsize": "10"}

#class ClusterColored(Cluster):
#  def __init__(self)

with Diagram("HLTD FU Machines", show=False, graph_attr=graph_attr, node_attr=node_attr, outformat="pdf"):
  with Cluster("HLT daemon service                   ", graph_attr={"bgcolor":"#EBF3E7"}):
    demon = nSE("/usr/lib/systemd/system/hltd.service")

  with Cluster("/opt/hltd/scratch/python/hltd.py"):
    hltd = nA("cleanup /fff/data\nlink /opt/hltd/cgi  to  /fff/data/cgi-bin\nstart http server port 9000\ncreate ResInfo()")

  with Cluster("/opt/hltd/scratch/python/HLTDInfo.py"): 
    ResInfo = nA("interface to work with Clients statuses\n/etc/appliance/dqm_resources/*")

  with Cluster("/opt/hltd/python/ResourceRanger.py            "):
    resr = nA("watch clients /etc/appliance/dqm_resources/*\n Run.StartOnResource() when find indle clients")

  with Cluster("/opt/hltd/python/RunRanger.py"):
    runr = nA("watch /fff/data\n for new run:\n create Run(...)\ncall Run.Start()")

  with Cluster("/opt/hltd/python/inotifywrapper.py", graph_attr={"bgcolor":"#ECE8F6"}):
    inotify = nA("inotify wrapper")

  with Cluster("/opt/hltd/python/Run.py                          "):
    run = nA("Run.__init__(): create anelasticDQM() \n Run.Start() -> Run.StartOnResource() -> \n -> OnlineResource.StartNewProcess()")

  with Cluster("/opt/hltd/python/Resource.py | OnlineResource", graph_attr={"bgcolor":"#EBF3E7"}):
    res = nMD("StartNewProcess():\n parse run .global files\n create ProcessWatchdog()\n Popen(startRun.sh)")

  with Cluster("/opt/hltd/python/Resource.py | ProcessWatchdog", graph_attr={"bgcolor":"#EBF3E7"}):
    wdog = nMD("wait return code from startRun.sh\ncrash -> restart, OnlineResource.moveUsedToBroken()\ncan't restart -> OnlineResource.moveUsedToQuarantined()\nsuccess -> OnlineResource.moveUsedToIdles()")

  with Cluster("/opt/hltd/python/startRun.sh", graph_attr={"bgcolor":"#EBF3E7"}):
    srun = nMD("execute cmsRun")

  with Cluster("/opt/hltd/python/anelasticDQM.py", graph_attr={"bgcolor":"#FDF7E3"}):
    anel = nA("create DQMFileWatcherFU(runNumber)\nwatch /home/dqmdevlocal/output/upload/\nrename and they move to a BU.")

  psutil = nR("psutil")
  bu = nL("BU machine")

  clients = nL("Clients: /etc/appliance/dqm_resources/*")

  guiold = nR("DQM GUI OLD")
  outfolder = nR("/home/dqmdevlocal/output/upload/\n/home/dqmprolocal/output/upload/")
  

  demon >> hltd
  hltd >> resr
  hltd >> runr
  hltd >> ResInfo

  resr << Edge(color="darkgreen") >> ResInfo
  ResInfo << Edge(color="darkgreen") >> clients

  resr - Edge(color="brown", style="dashed") - inotify
  runr - Edge(color="brown", style="dashed") - inotify
  anel - Edge(color="brown", style="dashed") - inotify

  runr >> run >> res >> srun
  res << Edge(color="darkgreen") >> wdog
  res << Edge(color="darkgreen") >> ResInfo

  # srun >> Edge(label="exitcode") >> wdog  
  srun >> wdog  
  srun >> guiold
  resr >> run
  run  >> anel >> bu
  psutil >> anel 
  run  << Edge(color="darkgreen") >> ResInfo
  srun >> outfolder >> anel
  
  
