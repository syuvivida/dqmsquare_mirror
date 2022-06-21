# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import time, os
import configparser as ConfigParser

### default values === >
cfg = {}

cfg_SECTION = 'OPTIONS'

cfg["VERSION"] = "1.1.0"
print( "\n\n\n================================== dqmsquare_cfg() v", cfg["VERSION"])

cfg["SLEEP_TIME"] = 5 #sec, int
cfg["SLEEP_TIME_LONG"] = 30 #sec, int
cfg["TMP_FILES_LIFETIME"] = 24 * 30 # h, int
cfg["TMP_CLEAN_FILES"] = True
cfg["TMP_FOLDER_TO_CLEAN"] = "tmp"
cfg["LOGGER_ROTATION_TIME"] = 24 #h, int
cfg["LOGGER_MAX_N_LOG_FILES"] = 15 # int
cfg["FIREFOX_RELOAD_NITERS"] = 5000 # 10000 # int ~ twice per week - 24 * 7 * 60 * 60 / 30
cfg["FFF_SECRET_NAME"] = 'selenium-secret-secret'
cfg["FFF_PORT"] = '9215'

#cfg["SERVER_LOCAL"] = True
cfg["SERVER_DEBUG"] = True
cfg["SERVER_K8"]    = False
cfg["SERVER_HOST"]  = '0.0.0.0'
cfg["SERVER_PORT"]  = 8887
cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = "tmp/content_parser_production"
cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = "tmp/content_parser_playback"
cfg["SERVER_RELOAD_TIME"]             = 5000 #msec, int
cfg["SERVER_LOG_PATH"]                = "log/server.log"
cfg["SERVER_DATA_PATH"]               = "/"
cfg["SERVER_FFF_CR_PATH"]             = "https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin"
cfg["SERVER_GRID_CERT_PATH"]          = "/home/pmandrik/CERT_TEST/np/usercert.pem"
cfg["SERVER_GRID_KEY_PATH"]           = "/home/pmandrik/CERT_TEST/np/userkey.pem"
cfg["SERVER_SIMULATOR_RUN_KEYS"]      = "cosmic_run,pp_run,commisioning_run"
cfg["SERVER_LINK_PREFIX"]             = ""

cfg["PARSER_DEBUG"]  = False
cfg["PARSER_RANDOM"] = False
cfg["PARSER_PARSE_OLDRUNS"] = True
cfg["PARSER_OLDRUNS_UPDATE_TIME"] = 1. # h float
cfg["PARSER_LOG_UPDATE_TIME"] = 10. # minutes float
cfg["PARSER_MAX_OLDRUNS"]  = 17 # int
cfg["PARSER_INPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["PARSER_OUTPUT_PATHS"] = "tmp/content_parser_production,tmp/content_parser_playback"
cfg["PARSER_LOG_PATH"]     = "log/parser.log"
cfg["PARSER_LINK_PREFIX"]  = ""

cfg["ROBBER_BACKEND"] = "selenium"
cfg["ROBBER_GECKODRIVER_PATH"] = "geckodriver/geckodriver"
cfg["ROBBER_DEBUG"] = True
cfg["ROBBER_GRAB_LOGS"] = True
cfg["ROBBER_GRAB_GRAPHS"] = True
cfg["ROBBER_GRAB_OLDRUNS"] = True
cfg["ROBBER_TARGET_SITES"] = "http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
cfg["ROBBER_OLDRUNS_TARGET_SITES"] = "http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
cfg["ROBBER_OUTPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["ROBBER_RELOAD_NITERS"] = 100
cfg["ROBBER_LOG_PATH"]         = "log/robber1.log"
cfg["ROBBER_OLDRUNS_LOG_PATH"] = "log/robber2.log"
cfg["ROBBER_GECKODRIVER_LOG_PATH"]         = "log/geckodriver1.log"
cfg["ROBBER_OLDRUNS_GECKODRIVER_LOG_PATH"] = "log/geckodriver2.log"
cfg["ROBBER_OLDRUNS_UPDATE_TIME"] = 2. # h, float
cfg["ROBBER_K8"] = False
cfg["ROBBER_K8_LOGIN_PAGE"] = ""
cfg["ROBBER_FIREFOX_PATH"] = ""
cfg["ROBBER_FIREFOX_PROFILE_PATH"] = ""

def set_k8_options(testbed = False):
  global cfg

  mount_path = "/cephfs/testbed/dqmsquare_mirror/"
  cfg["SERVER_FFF_CR_PATH"]             = "https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin"
  cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = mount_path[1:] + cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] 
  cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = mount_path[1:] + cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]
  cfg["SERVER_GRID_CERT_PATH"]   = '/etc/robots/robotcert.pem'
  cfg["SERVER_GRID_KEY_PATH"]    = '/etc/robots/robotkey.pem'
  cfg["TMP_FOLDER_TO_CLEAN"] = mount_path + cfg["TMP_FOLDER_TO_CLEAN"]
  cfg["SERVER_PORT"] = 8084
  cfg["SERVER_DATA_PATH"] = mount_path
  cfg["SERVER_LINK_PREFIX"]  = "/dqm/dqm-square-k8"
  cfg["SERVER_K8"] = True
  cfg["SERVER_LOG_PATH"]     = mount_path + cfg["SERVER_LOG_PATH"]
  cfg["PARSER_INPUT_PATHS"]  = ",".join( [mount_path + x for x in cfg["PARSER_INPUT_PATHS"].split(",")] )
  cfg["PARSER_OUTPUT_PATHS"] = ",".join( [mount_path + x for x in cfg["PARSER_OUTPUT_PATHS"].split(",")] )
  cfg["PARSER_LOG_PATH"]     = mount_path + cfg["PARSER_LOG_PATH"]
  cfg["PARSER_LINK_PREFIX"]  = "/dqm/dqm-square-k8"
  cfg["ROBBER_OUTPUT_PATHS"] = ",".join( [mount_path + x for x in cfg["ROBBER_OUTPUT_PATHS"].split(",")] )
  cfg["ROBBER_LOG_PATH"]         = mount_path + cfg["ROBBER_LOG_PATH"]
  cfg["ROBBER_OLDRUNS_LOG_PATH"] = mount_path + cfg["ROBBER_OLDRUNS_LOG_PATH"]
  cfg["ROBBER_GECKODRIVER_LOG_PATH"]         = mount_path + cfg["ROBBER_GECKODRIVER_LOG_PATH"]
  cfg["ROBBER_OLDRUNS_GECKODRIVER_LOG_PATH"] = mount_path + cfg["ROBBER_OLDRUNS_GECKODRIVER_LOG_PATH"]
  cfg["ROBBER_K8"] = True
  cfg["ROBBER_K8_LOGIN_PAGE"] = "https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin/login"
  cfg["ROBBER_FIREFOX_PATH"]  = "/opt/firefox/firefox"
  cfg["ROBBER_GECKODRIVER_PATH"] = "/usr/bin/geckodriver"
  cfg["ROBBER_FIREFOX_PROFILE_PATH"] = "/firefox_profile_path"
  cfg["ROBBER_TARGET_SITES"] = "https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?trackRun&hosts=production_c2f11&showFiles&showJobs&showTimestampsGraph&showEventsGraph,https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?trackRun&hosts=playback_c2f11&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
  cfg["ROBBER_OLDRUNS_TARGET_SITES"] = "https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,https://cmsweb-testbed.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"

  if not testbed : 
    cfg["SERVER_FFF_CR_PATH"]   = "https://cmsweb.cern.ch/dqm/dqm-square-origin"
    cfg["ROBBER_K8_LOGIN_PAGE"] = "https://cmsweb.cern.ch/dqm/dqm-square-origin/login"
    cfg["ROBBER_TARGET_SITES"]  = "https://cmsweb.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?trackRun&hosts=production_c2f11&showFiles&showJobs&showTimestampsGraph&showEventsGraph,https://cmsweb.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?trackRun&hosts=playback_c2f11&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
    cfg["ROBBER_OLDRUNS_TARGET_SITES"] = "https://cmsweb.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,https://cmsweb.cern.ch/dqm/dqm-square-origin/static/index.html#/lumi/?hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"

### load values === >
def load_cfg( path, section=cfg_SECTION ):
  if not path : return cfg

  config = ConfigParser.SafeConfigParser( cfg )
  try:
    config.read( path )
  except:
    print( "dqmsquare_cfg.load_cfg(): can't load", path, "cfg; return default cfg")
    return cfg;

  options = []
  try:
    options = config.items( section )
  except:
    print( "dqmsquare_cfg.load_cfg(): can't find", section, "section in", path, "cfg; return default cfg")
    return cfg;

  answer = {}
  for key, val in options : 
    if val == 'True' : val = True
    if val == 'False' : val = False
    answer[ key.upper() ] = val

  return answer

### dump default values === >
if __name__ == '__main__' :
  import sys
  if len(sys.argv) > 1 and sys.argv[1] == "k8":
    set_k8_options( testbed = False )
  if len(sys.argv) > 1 and sys.argv[1] == "k8_testbed":
    set_k8_options( testbed = True )

  config = ConfigParser.RawConfigParser()
  config.add_section('OPTIONS')
  opts = [ a for a in cfg.items() ]
  opts = sorted( opts, key=lambda x : x[0] )
  for opt in opts:
    config.set(cfg_SECTION, opt[0], opt[1])

  with open('dqmsquare_mirror.cfg', 'w') as configfile:
      config.write(configfile)

  cfg_ = load_cfg( 'dqmsquare_mirror.cfg' )
  items = list( cfg_.items() )
  items = sorted(items,key=lambda x : x[0])
  for item in items:
    print( item )

### get logger ===>
import logging
from logging import handlers
def set_log_handler(logger, path, interval, nlogs, debug_level):
  # add a rotating handler
  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  handler = logging.handlers.TimedRotatingFileHandler(path, when='h', interval=int(interval), backupCount=int(nlogs))
  handler.setFormatter(formatter)
  handler.setLevel(logging.INFO)
  logger.setLevel(logging.INFO)

  if debug_level :
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

  logger.addHandler(handler)
  logger.info("create %s log file" % path)

### error logger ===>
class ErrorLogs():
  def __init__(self):
    self.logs = {}

  def Check(self, id, log_text):
    if id not in self.logs :
      self.logs[ id ] = log_text
      return True
  
    old_log = self.logs[ id ]
    if old_log == log_text : return False
    self.logs[ id ] = log_text
    return True

### TMP output naming convention
# robber will create:
# ROBBER_OUTPUT_PATHS + get_TMP_robber_canvas_name(ROBBER_OUTPUT_PATHS, index)
# get_TMP_robber_page_name(ROBBER_OUTPUT_PATHS, run_index) + get_TMP_robber_canvas_name(get_TMP_robber_page_name(ROBBER_OUTPUT_PATHS, run_index), index)
def get_TMP_robber_page_name( path, run_index ):
  return path + "ROBBER" + "_run" + str(run_index)

def get_TMP_robber_canvas_name( path, index ):
  return path + "ROBBER" + "_canv" + str(index)

def is_TMP_robber_page( path, item ):
  if path == item : return True
  if not "ROBBER" in item: return False
  if "canv"   in item: return False
  if get_TMP_robber_page_name(path, "") not in item : return False
  return True

def is_TMP_robber_canvas_name( path, item ):
  if not "ROBBER" in item: return False
  if get_TMP_robber_canvas_name(path, "") not in item : return False
  return True

def get_TMP_robber_page_run( path ):
  run_id   = path.split("run")[1]
  return run_id

# parser will create ... 
def get_TMP_parser_page_name( path, run_index ):
  return path + "PARSER" + "_run" + str(run_index)

def get_TMP_parser_log_name( path, index ):
  return path + "PARSER" + "_job" + str(index) + ".log"

def is_TMP_parser_page( path, item ):
  if path == item : return True
  if not "PARSER" in item: return False
  if "job" in item: return False
  if "log" in item: return False
  if not get_TMP_parser_page_name(path, "") in item : return False
  return True

### parser=>rober backward communication
def get_parser_info( path_to_parser_output_page ):
  dir_name = os.path.dirname( path_to_parser_output_page )
  info_dic = {}
  for item in os.listdir( dir_name ) : 
    f = os.path.join(dir_name, item)
    if not is_TMP_parser_page(path_to_parser_output_page, f) : continue
    page_dic = {}
    text = ""
    try:
      ifile = open( f,"r" )
      text = ifile.read( )
      ifile.close()
    except: pass

    try:
      for line in text.split("\n"):
        if "<!--" not in line: continue
        content = line[len("<!--"):-len("-->")]
        content = content.split(":")
        page_dic[ content[0] ] = content[1]
    except: pass

    info_dic[f] = page_dic
  return info_dic

### Other
def dump_tmp_file( data, path, prefix, postfix ):
  import tempfile
  f = tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix=postfix, dir=path, delete=False)
  f.write( data )
  f.close()
  return os.path.basename( f.name )

def delete_file( path_to_file, log ):
  try:
    if not os.path.exists( path_to_file ) : return False
    if not os.path.isfile( path_to_file ) : return False
    os.remove( path_to_file )
  except:
    log.warning( "delete_file(): can't delete %s" % path_to_file )
    return False

  log.debug( "delete_file(): remove file %s" % path_to_file )
  return True

def clean_folder(path_to_outfile, threshold, log):
  if log : log.debug( "clean_folder(): remove old files for %s" % path_to_outfile )
  dir_name = os.path.dirname( path_to_outfile )
  for item in os.listdir( dir_name ) : 
    f = os.path.join(dir_name, item)
    timestamp = os.path.getmtime( f )
    now = time.time()
    if abs(timestamp - now) / 60 / 60 < threshold : continue
    delete_file( f, log )

def get_env_secret(log, secret_name='DQM_PASSWORD'):
  import base64
  env_secret=None
  try : 
    env_secret = os.environ[secret_name]
    # temp = temp.encode()
    # temp = base64.b64encode( temp )
    # env_secret = temp.decode("utf-8")
  except Exception as error_log:
    log.warning( "get_env_secret(): can't load DQM_PASSWORD cookie" )
    log.warning( repr(error_log) )
  return env_secret

def get_cr_usernames(log, secret_name='DQM_CR_USERNAMES'):
  raw_data = get_env_secret(log, secret_name)
  if not raw_data : return { "username" : "password" }
  answer = {}
  for pairs in raw_data.split(",") :
    try : 
      username, password = pairs.split(":")
      answer[ username ] = password
    except Exception as error_log:
      log.warning( "get_cr_usernames(): can't split data \"" + pairs + "\"" )
  return answer

### DQM^2 Mirror DB === >
import sqlite3
from collections import defaultdict
class DQM2MirrirDB:
  TB_NAME = "runs"
  DESCRIPTION = "(id TEXT PRIMARY KEY NOT NULL, client TEXT, run INT, rev INT, hostname TEXT, exit_code INT, events_total INT, events_rate REAL, cmssw_run INT, cmssw_lumi INT, client_path TEXT, runkey TEXT, fi_state TEXT, timestamp TIMESTAMP, VmRSS TEXT, stdlog_start TEXT, stdlog_end TEXT )"
  DESCRIPTION_SHORT = "(id , client , run , rev , hostname , exit_code , events_total , events_rate , cmssw_run , cmssw_lumi , client_path , runkey , fi_state, timestamp, VmRSS, stdlog_start, stdlog_end )"

  def __init__(self, log, db=None):
    self.log = log
    self.log.info("\n\n DQM2MirrirDB ===== init ")
    self.db_str = db

    if not self.db_str:
      self.db_str = ":memory:"

    self.conn = sqlite3.connect(self.db_str)
    self.create_tables()

  def create_tables(self):
    self.log.debug( "DQM2MirrirDB.create_tables()" )
    cur = self.conn.cursor()
    cur.execute( "CREATE TABLE IF NOT EXISTS " + self.TB_NAME + ' ' + self.DESCRIPTION )
    self.conn.commit()
    cur.close()

  def fill(self, header, document):
    id = header.get("_id")
    client = header.get("tag", "")
    run    = header.get("run", -1)
    rev    = header.get("_rev", -1)
    hostname = header.get("hostname", "")
    exit_code = document.get("exit_code", -1)
    events_total = document.get("events_total", -1)
    events_rate  = document.get("events_rate", -1)
    cmssw_run    = document.get("cmssw_run", -1)
    cmssw_lumi   = document.get("cmssw_lumi", -1)
    client_path, runkey = "", ""
    try:
      client_path  = document.get("cmdline")[1]
      for item in document.get("cmdline"):
        if "runkey" in item:
          runkey = item
    except: pass
    fi_state     = document.get("fi_state", "")
    timestamp    = header.get("timestamp", -1)

    extra = document.get( "extra", {} )
    ps_info = extra.get( "ps_info", {} )
    VmRSS        = ps_info.get( "VmRSS", "" )
    stdlog_start = str(extra.get( "stdlog_start", "" ))
    stdlog_end   = str(extra.get( "stdlog_end", "" ))

    values = (id , client , run , rev , hostname , exit_code , events_total , events_rate , cmssw_run , cmssw_lumi , client_path , runkey , fi_state, timestamp, VmRSS, stdlog_start, stdlog_end )
    self.log.debug( "DQM2MirrirDB.fill() - " + str(values) )
    template = "(" + ",".join( [ "?" for x in values ] ) + ")" 

    cur = self.conn.cursor()
    cur.execute("INSERT OR REPLACE INTO " + self.TB_NAME + " " + self.DESCRIPTION_SHORT + " VALUES " + template, values)
    self.conn.commit()

  def get(self, run_start, run_end):
    self.log.debug( "DQM2MirrirDB.get() - " + str(run_start) + " " + str(run_end) )
    cur = self.conn.cursor()
    cur.execute("SELECT * FROM " + self.TB_NAME + " WHERE run BETWEEN " + str(run_start) + " AND " + str(run_end) + ";" )
    answer = cur.fetchall()
    self.log.debug( "return " + str(answer) )
    #print( answer )
    return answer

  def make_table_entry( self, data ):
    answer = []
    # values = (id , client , run , rev , hostname , exit_code , events_total , events_rate , cmssw_run , cmssw_lumi , client_path , runkey , fi_state, timestamp )
    client    = data[1]
    run       = data[2]
    hostname  = data[4]
    exit_code  = data[5]
    events_total  = data[6]
    cmssw_run  = data[8]
    cmssw_lumi  = data[9]
    client_path  = data[10]
    runkey  = data[11]
    fi_state  = data[12]
    timestamp = data[13]

    client = self.get_short_client_name( client )
    var = hostname.split("-")
    hostname = "..".join( [ var[0], var[-1] ] )
    runkey = runkey[len("runkey="):]

    cmssw_path = ""
    subfolders = client_path.split("/")
    for folder in subfolders:
      if "CMSSW" in folder : 
        cmssw_path = folder
        break

    cmssw_v = cmssw_path.split("CMSSW_")[1]

    answer =  [ run, client, (hostname, events_total, cmssw_lumi, fi_state, exit_code, timestamp), (cmssw_run, runkey, cmssw_v) ]
    return answer

  def filter_clients(self, name):
    if not name : return False
    if name == "__init__" : return False
    return True

  def get_for_table(self, run_start, run_end):
    runs = self.get(run_start, run_end)
    runs_out = [ self.make_table_entry( run ) for run in runs ]

    dic = defaultdict( dict )
    for run in runs_out :
      run_number = run[0]
      client_name = run[1]
      client_data = run[2]
      run_data = run[3]
      run_item = dic[ run_number ]
      run_item[ "run_data" ] = run_data
      if "clients" not in run_item : run_item[ "clients" ] = defaultdict( dict )
      clients_item = run_item[ "clients" ]

      if client_name not in clients_item : clients_item[ client_name ] = [ client_data ]
      else : clients_item[ client_name ].append( client_data )

    return dict(dic)

  def get_short_client_name(self, client):
    return client[:-len("_dqm_sourceclient-live")] if "_dqm_sourceclient-live" in client else client

  def get_clients(self, run_start, run_end):
    self.log.debug( "DQM2MirrirDB.get_clients()" )
    cur = self.conn.cursor()
    cur.execute( "SELECT DISTINCT client FROM " + self.TB_NAME + " WHERE run BETWEEN " + str(run_start) + " AND " + str(run_end) + " ORDER BY client;" )
    answer = cur.fetchall()
    answer = [ self.get_short_client_name( name[0] ) for name in answer if self.filter_clients( name[0] ) ]
    self.log.debug( "return " + str(answer) )
    return answer
    
  def get_info(self):
    self.log.debug( "DQM2MirrirDB.get_runs_rage()" )
    cur = self.conn.cursor()
    cur.execute( "SELECT MIN(run), MAX(run) FROM " + self.TB_NAME + ";" )
    answer = list(cur.fetchall()[0])
    self.log.debug( "return " + str(answer) )
    return answer

  def get_rev(self, machine):
    if ".cms" in machine : machine = machine[:-len(".cms")]
    self.log.debug( "DQM2MirrirDB.get_rev()" )
    cur = self.conn.cursor()
    cur.execute( "SELECT MAX(rev) FROM " + self.TB_NAME + " WHERE hostname = \"" + str(machine) + "\";" )
    answer = list(cur.fetchall()[0])
    self.log.debug( "return " + str(answer) )
    return answer[0]







