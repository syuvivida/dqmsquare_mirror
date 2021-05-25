# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import ConfigParser

### default values === >
cfg = {}

cfg_SECTION = 'OPTIONS'
cfg["SLEEP_TIME"] = 5
cfg["SLEEP_TIME_LONG"] = 30
cfg["SERVER_LOCAL"] = True
cfg["SERVER_DEBUG"] = False
cfg["SERVER_HOST"]  = '0.0.0.0'
cfg["SERVER_PORT"]  = 8887
cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] = "tmp/content_parser_production"
cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   = "tmp/content_parser_playback"
cfg["SERVER_RELOAD_TIME"]             = 5000

cfg["ROBBER_BACKEND"] = "selenium"
cfg["ROBBER_GECKODRIVER_PATH"] = "geckodriver/geckodriver"
cfg["ROBBER_DEBUG"] = True
cfg["ROBBER_GRAB_LOGS"] = True
cfg["ROBBER_GRAB_GRAPHS"] = True
cfg["ROBBER_GRAB_OLDRUNS"] = True
cfg["ROBBER_TARGET_SITES"] = "http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=production_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph,http://fu-c2f11-11-01.cms:9215/static/index.html#/lumi/?trackRun&hosts=playback_c2f11&run=&showFiles&showJobs&showTimestampsGraph&showEventsGraph"
cfg["ROBBER_OUTPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["ROBBER_RELOAD_NITERS"] = 100

cfg["PARSER_DEBUG"] = True
cfg["PARSER_RANDOM"] = False
cfg["PARSER_PARSE_OLDRUNS"] = True
cfg["PARSER_INPUT_PATHS"]  = "tmp/content_robber_production,tmp/content_robber_playback"
cfg["PARSER_OUTPUT_PATHS"] = "tmp/content_parser_production,tmp/content_parser_playback"

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



