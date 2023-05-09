# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import json
import time, base64, os, sys

import logging
import traceback
log = logging.getLogger(__name__)

if __name__ == '__main__':
  NAME = "dqmsquare_grabber.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  is_k8 = bool( cfg["ROBBER_K8"] )

  # for local tests ... 
  run_modes  = [ "playback", "production" ]
  playback   = [ "dqmrubu-c2a06-03-01", "dqmfu-c2b01-45-01", "dqmfu-c2b02-45-01" ]
  production = [ "dqmrubu-c2a06-01-01", "dqmfu-c2b03-45-01", "dqmfu-c2b04-45-01" ]

  import sys
  if len(sys.argv) > 1 and sys.argv[1] == "playback":
    dqmsquare_cfg.set_log_handler(log, cfg["ROBBER_OLDRUNS_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["GRABBER_DEBUG"])
    run_modes = [ "playback" ]
  elif len(sys.argv) > 1 and sys.argv[1] == "production":
    dqmsquare_cfg.set_log_handler(log, cfg["ROBBER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["GRABBER_DEBUG"])
    run_modes = [ "production" ]
  else:
    dqmsquare_cfg.set_log_handler(log, cfg["GRABBER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["GRABBER_DEBUG"])

  if not is_k8 :
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler2 = logging.StreamHandler(sys.stdout)
    handler2.setFormatter(formatter)
    handler2.setLevel( logging.INFO )
    log.addHandler(handler2)
    playback   = [ "dqmrubu-c2a06-03-01", "dqmfu-c2b01-45-01", "dqmfu-c2b02-45-01" ]
    production = [ "dqmrubu-c2a06-01-01", "dqmfu-c2b03-45-01", "dqmfu-c2b04-45-01" ]

  ### global variables and auth cookies
  cr_path = cfg["SERVER_FFF_CR_PATH"]
  cert_path = [ cfg["SERVER_GRID_CERT_PATH"], cfg["SERVER_GRID_KEY_PATH"] ]
  selenium_secret = "changeme"
  env_secret = dqmsquare_cfg.get_env_secret(log, 'DQM_PASSWORD')
  if env_secret : selenium_secret = env_secret
  cookies = { str(cfg["FFF_SECRET_NAME"]) : selenium_secret }

  ### DQM^2-MIRROR DB CONNECTION
  db_playback, db_production = None, None
  if "playback" in run_modes : 
    db_playback = dqmsquare_cfg.DQM2MirrorDB( log, cfg["GRABBER_DB_PLAYBACK_PATH"] )
  if "production" in run_modes : 
    db_production = dqmsquare_cfg.DQM2MirrorDB( log, cfg["GRABBER_DB_PRODUCTION_PATH"] )

  ### FFF API around SQL DB is websocket based, we need to define event in message and send it
  ### API is simple - we can get only 1000 headers with clients ids and documents per client ids
  ### headers == clients basic info
  ### documents == clients logs and other information
  def get_documents_from_fff( dqm_machine, dqm_port=cfg["FFF_PORT"], runs_ids=[] ) :
    url = cfg["SERVER_FFF_CR_PATH"] + '/redirect?path=' + dqm_machine + '&port=' + str(dqm_port);
    if dqm_machine == cfg["SERVER_FFF_MACHINE"] :
      url = cfg["SERVER_FFF_CR_PATH"] + '/sync_proxy'

    jsn = { "event" : "request_documents", "ids" : runs_ids }
    data = json.dumps( { "messages" : [ json.dumps(jsn) ]  } )
    r = requests.post(url, data=data, cert=cert_path, verify=False, headers = {}, cookies=cookies, timeout=30)
    return r.content

  def get_headers_from_fff( dqm_machine, dqm_port=cfg["FFF_PORT"], revision=0 ) :
    url = cfg["SERVER_FFF_CR_PATH"] + '/redirect?path=' + dqm_machine + '&port=' + str(dqm_port);
    if dqm_machine == cfg["SERVER_FFF_MACHINE"] :
      url = cfg["SERVER_FFF_CR_PATH"] + '/sync_proxy'

    jsn = { "event" : "sync_request", "known_rev" : str(revision) }
    data = json.dumps( { "messages" : [ json.dumps(jsn) ]  } )
    r = requests.post(url, data=data, cert=cert_path, verify=False, headers = {}, cookies=cookies, timeout=30)
    print( url )
    print( jsn )
    return r.content
  
  bad_rvs = []
  def update_db( db_, host, rev = 0 ) :
    global bad_rvs
    log.info("Update host " + host + " " + str(rev))
    if not rev : rev = 0

    headers_answer = get_headers_from_fff(host, revision = rev )
    try:
      headers_answer = json.loads( json.loads(headers_answer)['messages'][0] )
      headers = headers_answer['headers']
      rev = headers_answer['rev']
    except Exception as error_log:
      log.warning( headers_answer )
      log.warning( repr(error_log) )
      log.warning( traceback.format_exc() )
      return

    if not len(headers) : return
    for header in headers :
      id = header["_id"]
      log.info("Process header " + str(id) )

      if host[0] == "b" :
        if "analyze_files" not in id :
          log.debug("Skip, no 'analyze_files' key") 
          continue
        document_answer = get_documents_from_fff(host, runs_ids = [ id ] )
        document = json.loads( json.loads(document_answer)['messages'][0] )["documents"][0]
        log.debug("Fill graph info into DB ... ") 
        answer = db_.fill_graph( header, document )
        if answer : 
          bad_rvs += [ answer ]
      else :
        document_answer = get_documents_from_fff(host, runs_ids = [ id ] )
        document = json.loads( json.loads(document_answer)['messages'][0] )["documents"][0]
        log.debug("Fill doc info into DB ... ") 
        answer = db_.fill( header, document )
        if answer : 
          bad_rvs += [ answer ]

  #update_db("dqmfu-c2b01-45-01", 0 )
  #exit()

  #rev = db.get_rev( "dqmfu-c2b01-45-01" );
  #update_db( "dqmfu-c2b01-45-01", rev )
  #exit()

  log.info( "loop ... " + str(run_modes) )

  while True:
    try:
      ### get content from active sites
      if "playback" in run_modes : 
        for host in playback :
          rev = db_playback.get_rev( host );
          update_db( db_playback, host, rev )
      if "production" in run_modes : 
        for host in production :
          rev = db_production.get_rev( host );
          update_db( db_production, host, rev )
    except KeyboardInterrupt:
      break
    except Exception as error_log:
      log.warning("grabber crashed ...")
      log.warning( repr(error_log) )
      log.warning( traceback.format_exc() )
      continue;

    log.debug( "z-Z-z" )
    if is_k8 : time.sleep( int(cfg["SLEEP_TIME"]) )

    if len( bad_rvs ):
      log.info( "BAD REVISIONS:", bad_rvs ) 















