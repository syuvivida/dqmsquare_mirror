
##### DQM^2 Mirror Page
This is a system to grab the information about DQM jobs from DQM^2 site, 
parse it, removing sensitive information, and show selections outside the P5 are.

The architecture is sequential:
* dqmsquare_robber.py - uses firefox webdriver (installed on the same pc) & selenium library to load DQM^2 page and execute JavaScript and save a copy to local folder. It is also used to click on *log* button in order to get the logs of the jobs withing the page, click on *graph* button in order to get the link to the graph-images and then save them as separate files into the tmp folder, click on *run number* buttons in order to switch to old runs and grab them too as separate files. Because DQM^2 need some time to load the content from DB we also need to wait SLEEP\_TIME. Dqmsquare\_robber.py will try to download all info from old runs, because of this you need to wait SLEEP\_TIME * (number of old runs) at the beginning.
* dqmsquare_parser.py - parses the files made by dqmsquare_robber.py using based on BeautifulSoupin order to extract job status information and logs, lumis and run information and put it into html files. The parser is also remove tmp files older than TMP_FILES_LIFETIME.
* dqmsquare_server.py - simple server to show html files made by dqmsquare_parser.py
* dqmsquare_cfg.py - for CFG and common code, run it to produce default .cfg file
The work is periodic: dqmsquare_robber.py retrieves the information every X seconds, 
dqmsquare_parser.py tries to produce new html files every Y seconds,
JS at dqmsquare_server.py tries to update the content of the page using html files every Z seconds.

Other scripts/files:
* dqmsquare_deploy.sh - to download some extra software and run PyInstaller. We are using PyInstaller to pack python together with extra libraries (not a firefox!) into single executable ignoring lack of the software at P5 machines.
* dqmsquare_mirror.spec - to specify the RPM properties. Check this file in order to change the files used for the installation and paths. 
* services/dqmsquare_mirror@.service - configuration of daemons for DQM^2 Mirror services
* services/dqmsquare_mirror_wrapper.sh - used in order to define the working folder and execute dqmsquare_robber, dqmsquare_parser or dqmsquare_server
* static/dqm_mirror_template.html - the only 

Folders:
* log - folder to put logs files
* tmp - folder to put output from dqmsquare_robber and dqmsquare_parser
The RPM post-install script will create this folders. They are also hardcoded in the dqmsquare_server.py.

##### Requirements
Tested with:  
* Python: 2.7.14  
* Platform: Linux-4.12.14-lp150.12.82-default-x86_64-with-glibc2.2.5  
* Bottle: 0.12.19  
* Geckodriver: 0.29.1  
* PyInstaller: 3.4  

For the creation of RPM:
* rpm-build  

##### Deployment
Download repo to your local linux machine. 
Check dqmsquare_deploy.sh to download extra dependencies and create executables.
Several options:

1. For testing copy whole package manually to the P5 machine (fusermount works well for me).
   From the same folder run dqmsquare_server.py at server machine, dqmsquare_robber.py at machine with firefox, dqmsquare_parser.py at any machine..
2. .. or copy RPM created by dqmsquare_deploy.sh to the P5 machine and install.  
   sudo rpm -i dqmsquare_mirror-1.0.0-1.x86_64.rpm  
   sudo systemctl enable dqmsquare_mirror@robber.service dqmsquare_mirror@robber_oldruns.service dqmsquare_mirror@parser.service dqmsquare_mirror@server.service  
   sudo systemctl start dqmsquare_mirror@robber.service dqmsquare_mirror@robber_oldruns.service dqmsquare_mirror@parser.service dqmsquare_mirror@server.service  
   You can also install this locally with --prefix=PATH option.

##### Usefull extras
* Bottle built-in default server is not for a heavy server load, just for 3-5 shifters
* Number of logs created by dqmsquare_robber/dqmsquare_parser/dqmsquare_server is limited by TimedRotatingFileHandler
* dqmsquare_robber.py spawn lot of firefox subprocesses. In case of the dqmsquare_robber process is killed they may persist, requiring the manual killing to free the resources.
*  to build  
 ./dqmsquare_deploy.sh build
* at p5 for installation, for example  
  sudo rpm -e dqmsquare_mirror; sudo rpm -i /nfshome0/pmandrik/dqmsquare_mirror-1.0.0-1.x86_64.rpm

##### TODO
Some ideas for future development:
* geckodriver log cleaner  
* switch to python3  
* help page  


