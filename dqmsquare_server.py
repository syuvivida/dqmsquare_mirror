# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bottle'))

import requests
import bottle
from bottle import template, static_file, error
from bottle import route, get, post, request
from bottle import default_app

import logging
import json
log = logging.getLogger(__name__)

### wrapper for logs
from functools import wraps
from datetime import datetime
def log_to_logger(fn):
  @wraps(fn)
  def _log_to_logger(*args, **kwargs):
    request_time = datetime.now()
    actual_response = fn(*args, **kwargs)
    log.info('%s %s %s %s %s' % (bottle.request.remote_addr, request_time, bottle.request.method, bottle.request.url, bottle.response.status))
    return actual_response
  return _log_to_logger

def start_server( cfg ):
  bottle.install( log_to_logger )
  # remember to remove reloader=True and debug(True) when you move your
  # application from development to a productive environment
  bottle.debug(bool(cfg["SERVER_DEBUG"]))
  bottle.run(reloader=bool(cfg["SERVER_DEBUG"]), host=str(cfg["SERVER_HOST"]), port=int(cfg["SERVER_PORT"]))

if __name__ == '__main__':
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  dqmsquare_cfg.set_log_handler(log, cfg["SERVER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], True)
  SERVER_DATA_PATH = cfg["SERVER_DATA_PATH"]

  log.info("\n\n\n =============================================================================== ")
  log.info("\n\n\n dqmsquare_server ============================================================== ")

  def make_dqm_mirrow_page(cfg):
    ifile = open("static/dqm_mirror_template.html","r")
    content = ifile.read( )
    ifile.close()

    #if cfg["SERVER_LOCAL"] :  
    content = content.replace( "%PATH_TO_PRODUCTION_PAGE%", cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] )
    content = content.replace( "%PATH_TO_PLAYBACK_PAGE%",   cfg["SERVER_PATH_TO_PLAYBACK_PAGE"]   )
    #else : 
    #  content = content.replace( "%PATH_TO_PRODUCTION_PAGE%",  "/dqm/dqm-square/" + cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] )
    #  content = content.replace( "%PATH_TO_PLAYBACK_PAGE%",    "/dqm/dqm-square/" + cfg["SERVER_PATH_TO_PLAYBACK_PAGE"] )

    content = content.replace( "%RELOAD_TIME%", str(cfg["SERVER_RELOAD_TIME"]) )

    ofile = open("static/dqm_mirror.html","w")
    ofile.write( content )
    ofile.close()

  ### DQM^2 Mirror ###
  @route('')
  @route('/')
  @route('/dqm/dqm-square-k8')
  @route('/dqm/dqm-square-k8/')
  def greet(name='Stranger'):
    return static_file("dqm_mirror.html", root='./static/')

  if cfg["SERVER_K8"] :
    ### K8
    @route('/dqm/dqm-square-k8/static/<filename>')
    def get_static(filename):
      return static_file(filename, root='./static/')

    @route('/dqm/dqm-square-k8' + SERVER_DATA_PATH + 'tmp/<filename>')
    @route('/dqm/dqm-square-k8' + SERVER_DATA_PATH + 'tmp/tmp/<filename>')
    def get_tmp(filename):
      content = static_file(filename, root=SERVER_DATA_PATH+'tmp/')
      return content

    @route('/dqm/dqm-square-k8' + SERVER_DATA_PATH + 'log/<filename>')
    @route('/dqm/dqm-square-k8' + SERVER_DATA_PATH + 'tmp/log/<filename>')
    def get_tmp(filename):
      content = static_file(filename, root=SERVER_DATA_PATH+'log/')
      return content
  else :
    @route('/static/<filename>')
    def get_static(filename):
      return static_file(filename, root='./static/')

    @route('/tmp/<filename>')
    @route('/tmp/tmp/<filename>')
    def get_tmp(filename):
      content = static_file(filename, root='./tmp/')
      return content

    @route('/log/<filename>')
    @route('/tmp/log/<filename>')
    def get_tmp(filename):
      content = static_file(filename, root='./log/')
      return content

  if True:
    ### CR ###
    cr_usernames      = dqmsquare_cfg.get_cr_usernames(log, "DQM_CR_USERNAMES")
    env_cookie_secret = dqmsquare_cfg.get_env_secret(log, "DQM_CR_PASSWORD")
    cookie_secret = env_cookie_secret if env_cookie_secret else "secret"
    def check_login(username, password, cookie=False):
      if username not in cr_usernames : return False
      if cookie : return True
      if password != cr_usernames[ username ] : return False
      return True
  
    @post('/cr/login')
    @post('/dqm/dqm-square-k8/cr/login')
    def do_login():
      username = request.forms.get('username')
      password = request.forms.get('password')
      log.info( "login result " + str(check_login(username, password)) ) 
      if check_login(username, password):
        bottle.response.set_cookie( "dqmsquare-mirror-cr-account", username, secret=cookie_secret, path="/", max_age=24*60*60, httponly=True)
        bottle.redirect("/dqm/dqm-square-k8/cr")
        if cfg["SERVER_K8"] : bottle.redirect("https://cmsweb.cern.ch/dqm/dqm-square-k8/cr")
        else                : bottle.redirect("/dqm/dqm-square-k8/cr")
        return "<p>Your login information was correct.</p>"
      else:
        return "<p>Login failed.</p>"

    @route('/cr/logout')
    @route('/dqm/dqm-square-k8/cr/logout') # https://cmsweb.cern.ch/dqm/dqm-square-k8/
    def do_logout():
      log.info( "logout" )
      bottle.response.set_cookie( "dqmsquare-mirror-cr-account", "random", secret=cookie_secret, path="/", httponly=True )
      if cfg["SERVER_K8"] : bottle.redirect("https://cmsweb.cern.ch/dqm/dqm-square-k8/")
      else                : bottle.redirect("/")
      return "<p>Your login information cleared.</p>"

    def check_auth(redirect=True):
      def check_auth_(fn):
        def check_auth__(*args, **kwargs):
          username = request.get_cookie( "dqmsquare-mirror-cr-account", secret=cookie_secret )
          if not check_login( username, None, True ) :
            if redirect: 
              if cfg["SERVER_K8"] : bottle.redirect("https://cmsweb.cern.ch/dqm/dqm-square-k8/cr/login")
              else                : bottle.redirect("/dqm/dqm-square-k8/cr/login")
            else : return "Please login ..."
          else : return fn(*args, **kwargs)
        return check_auth__
      return check_auth_

    @route('/cr')
    @route('/cr/')
    @route('/dqm/dqm-square-k8/cr')
    @route('/dqm/dqm-square-k8/cr/')
    @check_auth()
    def get_static(name='Stranger'):
      return static_file("dqm_cr.html", root='./static/')

    @get('/cr/login')
    @get('/dqm/dqm-square-k8/cr/login')
    def login():
        return '''
            <style>
	          .title {
                padding-left: 16px;
                padding-top: 7px;
                padding-right: 16px;
                padding-bottom: 6px;
                text-decoration: none;
                font-size: 18px;
                background-color: #2471a3;
                color:  #d4e6f1 ;
                font-weight: bold;
              }
            </style>
            <div class="title">
              DQM <sup>2</sup> &#x25A0; Welcom!
            </div> <br>
            <form action="/dqm/dqm-square-k8/cr/login" method="post">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''

    # DQM & FFF & HLTD
    cr_path = cfg["SERVER_FFF_CR_PATH"]
    cert_path = [ cfg["SERVER_GRID_CERT_PATH"], cfg["SERVER_GRID_KEY_PATH"] ]
    selenium_secret = "changeme"
    env_secret = dqmsquare_cfg.get_env_secret(log, 'DQM_PASSWORD')
    if env_secret : selenium_secret = env_secret
    cookies = { str(cfg["FFF_SECRET_NAME"]) : selenium_secret }
    @route('/cr/exe')
    @route('/dqm/dqm-square-k8/cr/exe') # http://0.0.0.0:8887/dqm/dqm-square-k8/cr/exe?what=get_dqm_machines&
    @check_auth(False)
    def cr_exe():
      log.info( bottle.request.urlparts )
      what = bottle.request.query.what

      #if what in ["get_dqm_clients", "change_dqm_client"] :
      #  return json.dumps( '[["a.py",0], ["b.py",1], ["c.py",0]]' )

      ### get data from DQM^2 Mirror
      if what == "get_simulator_run_keys" :
        try:
          answer = str(cfg["SERVER_SIMULATOR_RUN_KEYS"].split(","))
          return answer
        except Exception as error_log:
          bottle.response.status = 400
          log.warning( error_log )
          return repr(error_log)

      ### get data from DQM^2
      # initial request
      url = cr_path + "/cr/exe?" + bottle.request.urlparts.query
      answer = None
      try:
        r = requests.get(url, cert=cert_path, verify=False, cookies=cookies)
        dqm2_answer = r.content
      except Exception as error_log:
        bottle.response.status = 400
        log.warning( "cr_exe() initial request : " + repr(error_log) )
        return repr(error_log)

      log.warning( what )

      if what in ["get_dqm_machines", "get_simulator_config", "get_hltd_versions", "get_fff_versions", "restart_hltd", "restart_fff", "get_simulator_runs", "start_playback_run", "get_dqm_clients", "change_dqm_client"] :
        # change format to be printable
        if what in [ "get_dqm_clients", "change_dqm_client" ] :
          print( url )

        answer = dqm2_answer
        try:
          format = bottle.request.query.get('format', default=None)
          if ( what in ["get_hltd_versions", "get_fff_versions"] ) and format :
            answer = ""
            data   = json.loads( dqm2_answer )
            for key, lst in sorted( data.items() ):
              answer += "<strong>" + key + "</strong>\n"
              for host, version in sorted( lst.items() ) :
                answer += host + " " + version

          if what == "get_dqm_machines" and format :
            answer = ""
            data   = json.loads( dqm2_answer )
            for key, lst in sorted( data.items() ):
              answer += "<strong>" + key + "</strong> " + str( lst ) + "\n"

          if what == "get_simulator_config":
            answer = json.loads( dqm2_answer )

        except Exception as error_log:
          bottle.response.status = 400
          log.warning( "cr_exe() change format to be printable : " + repr(error_log) )
          return repr(error_log)

        return answer

      ### get logs data in new window tabs from DQM^2
      if what in ["get_fff_logs", "get_hltd_logs"]:
        data  = ["No data from fff available ..."]

        try:
          data  = json.loads( dqm2_answer )
        except Exception as error_log:
          bottle.response.status = 400  
          log.warning( "cr_exe() : can't json.loads from DQM^2 data " + dqm2_answer )
          log.warning( repr(error_log) )
          return repr(error_log)

        fnames = []
        for item in data:
          if not len(item) : continue
          try:
            fname = dqmsquare_cfg.dump_tmp_file( item, SERVER_DATA_PATH+'tmp/', what, ".txt" )
          except Exception as error_log:
            log.warning( "cr_exe() : error in dqmsquare_cfg.dump_tmp_file for file:" )
            log.warning( repr(error_log) )
            continue
          fnames += [ SERVER_DATA_PATH+'/tmp/' + fname ]
        return str(fnames)

      # default answer
      log.warning( "cr_exe() : No actions defined for that request : " + repr(what) )
      return "No actions defined for that request"

  log.info("make_dqm_mirrow_page() call ... ")
  make_dqm_mirrow_page( cfg )

  log.info("start_server() call ... ")
  start_server( cfg )
  log.info("start_server() end ... ")




