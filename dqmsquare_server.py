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

  def enable_cors(fn):
    from bottle import request, response
    def _enable_cors(*args, **kwargs):
      # set CORS headers
      response.headers['Access-Control-Allow-Origin']  = '*'
      response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
      response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
      response.headers['Access-Control-Allow-Credentials'] = 'true'
      if bottle.request.method != 'OPTIONS':
        # actual request; reply with the actual response
        return fn(*args, **kwargs)
      return _enable_cors

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
    cr_username = "username"
    cr_password = "password"
    cookie_secret = "secret"
    def check_login(username, password, cookie=False):
      print(username == cr_username, password == cr_password)
      if username != cr_username : return False
      if cookie : return True
      if password != cr_password : return False
      return True
  
    @post('/cr/login')
    @post('/dqm/dqm-square-k8/cr/login')
    def do_login():
      username = request.forms.get('username')
      password = request.forms.get('password')
      print( check_login(username, password) ) 
      if check_login(username, password):
        bottle.response.set_cookie( "dqmsquare-mirror-cr-account", username, secret=cookie_secret, path="/", httponly=True )
        bottle.redirect("/dqm/dqm-square-k8/cr")
        return "<p>Your login information was correct.</p>"
      else:
        return "<p>Login failed.</p>"

    @route('/cr/logout')
    @route('/dqm/dqm-square-k8/cr/logout')
    def do_logout():
      bottle.response.set_cookie( "dqmsquare-mirror-cr-account", "random", secret=cookie_secret, path="/", httponly=True )
      bottle.redirect("/")
      return "<p>Your login information cleared.</p>"

    def check_auth(fn):
      def check_auth_(**kwargs):
        username = request.get_cookie( "dqmsquare-mirror-cr-account", secret=cookie_secret )
        print( username )
        if not check_login( username, None, True ) :
          bottle.redirect("/cr/login")
        else : return fn(**kwargs)
      return check_auth_

    @route('/cr')
    @route('/cr/')
    @route('/dqm/dqm-square-k8/cr')
    @route('/dqm/dqm-square-k8/cr/')
    @check_auth
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
            <form action="/cr/login" method="post">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''

    # DQM & FFF & HLTD
    cr_path = cfg["SERVER_FFF_CR_PATH"]
    cert_path = [cfg["SERVER_GRID_CERT_PATH"], cfg["SERVER_GRID_KEY_PATH"]]
    cookies = {'selenium-secret': 'changeme'}
    @route('/cr/exe')
    @route('/dqm/dqm-square-k8/cr/exe') # http://0.0.0.0:8887/dqm/dqm-square-k8/cr/exe?what=get_dqm_machines&
    #@check_auth
    def cr_exe():
      log.debug( bottle.request.urlparts )
      what = bottle.request.query.what
      print(what, what == "get_dqm_machines")

      if what == "get_simulator_run_keys" :
        return str(cfg["SERVER_SIMULATOR_RUN_KEYS"].split(","))

      if what == "get_simulator_runs" :
        return str(["123", "456", "789"])

      if what == "get_simulator_config" :
        return json.dumps( {"source" : "/asd/ads/asdasd/asddasas/asddasdas/789", "number_of_ls" : 501, "run_key": "pp_run"} )

      if what in ["get_dqm_machines", "get_simulator_config", "get_hltd_versions", "restart_hltd", "restart_fff", "get_simulator_runs", "start_playback_run"] :
        url = cr_path + "/cr/exe?" + bottle.request.urlparts.query
        try:
          print( cert_path )
          r = requests.get(url, cert=cert_path, verify=False, cookies=cookies)
          print( r.content )
          print( r.json() )
          return r.content
        except:
          return "Access Error"

      if what in ["get_fff_logs", "get_hltd_logs"]:
        url = cr_path + "/cr/exe?" + bottle.request.urlparts.query
        r = requests.get(url, cert=cert_path, verify=False, cookies=cookies)
        data  = ["No data from fff available ..."]

        try:
          data  = json.loads( r.json() )
          data = ["123", "456", "789"]
        except: pass

        fnames = []
        for item in data:
          fname = dqmsquare_cfg.dump_tmp_file( item, SERVER_DATA_PATH+'tmp/', what )
          fnames += [ SERVER_DATA_PATH+'/tmp/' + fname ]
        return str(fnames)

      if what == "start_playback_run" :
        pass

      # start_playback_run
      return "No actions defined for that request"

  log.info("make_dqm_mirrow_page() call ... ")
  make_dqm_mirrow_page( cfg )

  log.info("start_server() call ... ")
  start_server( cfg )
  log.info("start_server() end ... ")




