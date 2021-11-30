# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bottle'))

import bottle
from bottle import template, static_file, error
from bottle import route, get, post, request
from bottle import default_app

import logging
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

  if cfg["SERVER_K8"] :
    ### K8
    SERVER_DATA_PATH = cfg["SERVER_DATA_PATH"]
    @route('/dqm/dqm-square-k8')
    @route('/dqm/dqm-square-k8/')
    def greet(name='Stranger'):
      return static_file("dqm_mirror.html", root='./static/')

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
    ### DQM^2 Mirror ###
    @route('/')
    def greet(name='Stranger'):
      return static_file("dqm_mirror.html", root='./static/')

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
    def do_login():
      username = request.forms.get('username')
      password = request.forms.get('password')
      print( check_login(username, password) ) 
      if check_login(username, password):
        bottle.response.set_cookie( "dqmsquare-mirror-cr-account", username, secret=cookie_secret )
        bottle.redirect("/cr")
        return "<p>Your login information was correct.</p>"
      else:
        return "<p>Login failed.</p>"

    def check_auth(fn):
      def check_auth_(**kwargs):
        username = request.get_cookie( "dqmsquare-mirror-cr-account", secret=cookie_secret )
        if not check_login( username, None, True ) :
          bottle.redirect("/cr/login")
        else : return fn(**kwargs)
      return check_auth_

    @route('/cr')
    @check_auth
    def get_static(name='Stranger'):
      return static_file("dqm_cr.html", root='./static/')

    @get('/cr/login')
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

    # DQM & FFF
    @route('/cr/get_dqm_machines')
    @check_auth
    def cr_get_dqm_machines():
      machines = '["ws://bu-...-01", "ws://fu-...-01", "ws://fu-...-02", "ws://fu-...-03", "ws://fu-...-04"]'
      return machines

    @route('/cr/get_playback_config')
    @check_auth
    def cr_get_dqm_machines():
      machines = '["ws://bu-...-01", "ws://fu-...-01", "ws://fu-...-02", "ws://fu-...-03", "ws://fu-...-04"]'
      return machines

    @route('/cr/start_playback_run')
    @check_auth
    def cr_get_dqm_machines():
      machines = '["ws://bu-...-01", "ws://fu-...-01", "ws://fu-...-02", "ws://fu-...-03", "ws://fu-...-04"]'
      return machines

    # HLTD
    @route('/cr/get_hltd_versions')
    @check_auth
    def cr_get_hltd_versions():
      import time
      time.sleep( 5 )
      print( request.headers.keys() )
      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return 'This is an AJAX request'
      else:
        return 'This is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request'

    @route('/cr/restart_hltd')
    @check_auth
    def cr_restart_hltd():
      return 'This is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request'

    @route('/cr/get_hltd_logs')
    @check_auth
    def cr_get_hltd_logs():
      import time
      time.sleep( 5 )
      return 'This is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request\nThis is a normal request'

  log.info("make_dqm_mirrow_page() call ... ")
  make_dqm_mirrow_page( cfg )

  log.info("start_server() call ... ")
  start_server( cfg )
  log.info("start_server() end ... ")




