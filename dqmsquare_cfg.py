# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import ConfigParser

### default values === >
cfg = {}

cfg_SECTION = 'OPTIONS'

cfg["SLEEP_TIME"] = 5 #sec
cfg["SLEEP_TIME_LONG"] = 30 #sec
cfg["LOGGER_ROTATION_TIME"] = 24 #h
cfg["LOGGER_MAX_N_LOG_FILES"] = 100

cfg["SERVER_LOCAL"] = True
cfg["SERVER_DEBUG"] = False
cfg["SERVER_HOST"]  = '0.0.0.0'
cfg["SERVER_PORT"]  = 8887
cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = "tmp/content_parser_production"
cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = "tmp/content_parser_playback"
cfg["SERVER_RELOAD_TIME"]             = 5000 #msec
cfg["SERVER_LOG_PATH"]                = "log/dqmsquare_server.log"

cfg["ROBBER_BACKEND"] = "selenium"
cfg["ROBBER_GECKODRIVER_PATH"] = "geckodriver/geckodriver"
cfg["ROBBER_DEBUG"] = True
cfg["ROBBER_GRAB_LOGS"] = True
cfg["ROBBER_GRAB_GRAPHS"] = True
cfg["ROBBER_GRAB_OLDRUNS"] = True
cfg["ROBBER_TARGET_SITES"] = "http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
cfg["ROBBER_OUTPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["ROBBER_RELOAD_NITERS"] = 100
cfg["ROBBER_LOG_PATH"]      = "log/dqmsquare_robber.log"
cfg["ROBBER_OLDRUNS_UPDATE_TIME"] = 2 # h

cfg["PARSER_DEBUG"] =  False
cfg["PARSER_RANDOM"] = False
cfg["PARSER_PARSE_OLDRUNS"] = True
cfg["PARSER_OLDRUNS_UPDATE_TIME"] = 1 # h
cfg["PARSER_MAX_OLDRUNS"]  = 17
cfg["PARSER_INPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["PARSER_OUTPUT_PATHS"] = "tmp/content_parser_production,tmp/content_parser_playback"
cfg["PARSER_LOG_PATH"]     = "log/dqmsquare_parser.log"

### load values === >
def load_cfg( path, section=cfg_SECTION ):
  if not path : return cfg

  config = ConfigParser.SafeConfigParser( cfg )
  try:
    config.read( path )
  except:
    print "dqmsquare_cfg.load_cfg(): can't load", path, "cfg; return default cfg"
    return cfg;

  options = []
  try:
    options = config.items( section )
  except:
    print "dqmsquare_cfg.load_cfg(): can't find", section, "section in", path, "cfg; return default cfg"
    return cfg;

  answer = {}
  for key, val in options : 
    if val == 'True' : val = True
    if val == 'False' : val = False
    answer[ key.upper() ] = val

  return answer

### dump default values === >
if __name__ == '__main__' :
  config = ConfigParser.RawConfigParser()
  config.add_section('OPTIONS')
  opts = [ a for a in cfg.items() ]
  opts = sorted( opts, key=lambda x : x[0] )
  for opt in opts:
    config.set(cfg_SECTION, opt[0], opt[1])

  with open('dqmsquare_mirror.cfg', 'w') as configfile:
      config.write(configfile)

  cfg_ = load_cfg( 'dqmsquare_mirror.cfg' )
  print cfg_


### get logger ===>
import logging
from logging import handlers
def set_log_handler(logger, path, interval, nlogs, debug_level):
  # add a rotating handler
  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  handler = logging.handlers.TimedRotatingFileHandler(path, when='h', interval=interval, backupCount=nlogs)
  handler.setFormatter(formatter)
  handler.setLevel(logging.INFO)
  logger.setLevel(logging.INFO)

  if debug_level :
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

  logger.addHandler(handler)
  logger.info("create %s log file" % path)










