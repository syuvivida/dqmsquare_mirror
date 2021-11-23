# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import os
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

#cfg["SERVER_LOCAL"] = True
cfg["SERVER_DEBUG"] = True
cfg["SERVER_K8"]    = False
cfg["SERVER_HOST"]  = '0.0.0.0'
cfg["SERVER_PORT"]  = 8887
cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = "tmp/content_parser_production"
cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = "tmp/content_parser_playback"
cfg["SERVER_RELOAD_TIME"]             = 5000 #msec, int
cfg["SERVER_LOG_PATH"]                = "log/server.log"
cfg["SERVER_DATA_PATH"]               = "."

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

def set_k8_options():
  global cfg

  mount_path = "/cephfs/testbed/dqmsquare_mirror/"
  cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = mount_path[1:] + cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] 
  cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = mount_path[1:] + cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]
  cfg["TMP_FOLDER_TO_CLEAN"] = mount_path + cfg["TMP_FOLDER_TO_CLEAN"]
  cfg["SERVER_PORT"] = 8084
  cfg["SERVER_DATA_PATH"] = mount_path
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
    set_k8_options()

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

import time, os
def clean_folder(path_to_outfile, threshold, log):
  if log : log.debug( "clean_folder(): remove old files for %s" % path_to_outfile )
  dir_name = os.path.dirname( path_to_outfile )
  for item in os.listdir( dir_name ) : 
    f = os.path.join(dir_name, item)
    timestamp = os.path.getmtime( f )
    now = time.time()
    if abs(timestamp - now) / 60 / 60 < threshold : continue
    delete_file( f, log )









