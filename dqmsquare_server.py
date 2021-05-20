# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bottle'))

import bottle
from bottle import route, template, request, static_file, error
from bottle import default_app

#@error(404)
#@error(403)
@route('/')
def greet(name='Stranger'):
  return static_file("dqm_mirror.html", root='./static/')

@route('/static/<filename>')
def get_static(filename):
  return static_file(filename, root='./static/')

@route('/tmp/<filename>')
def get_tmp(filename):
  content = static_file(filename, root='./tmp/')
  print( content )
  return static_file(filename, root='./tmp/')

def start_server( cfg ):
  # remember to remove reloader=True and debug(True) when you move your
  # application from development to a productive environment
  bottle.debug(bool(cfg["SERVER_DEBUG"]))
  bottle.run(reloader=bool(cfg["SERVER_DEBUG"]), host=str(cfg["SERVER_HOST"]), port=int(cfg["SERVER_PORT"]))

if __name__ == '__main__':
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )

  def make_dqm_mirrow_page(cfg):
    ifile = open("static/dqm_mirror_template.html","r")
    content = ifile.read( )
    ifile.close()

    if cfg["SERVER_LOCAL"] :  
      content = content.replace( "%PATH_TO_PRODUCTION_PAGE%", cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] )
      content = content.replace( "%PATH_TO_PLAYBACK_PAGE%",   cfg["SERVER_PATH_TO_PLAYBACK_PAGE"] )
    else : 
      content = content.replace( "%PATH_TO_PRODUCTION_PAGE%",  "/dqm/dqm-square/" + cfg["SERVER_PATH_TO_PRODUCTION_PAGE"] )
      content = content.replace( "%PATH_TO_PLAYBACK_PAGE%",    "/dqm/dqm-square/" + cfg["SERVER_PATH_TO_PLAYBACK_PAGE"] )

    content = content.replace( "%RELOAD_TIME%", str(cfg["SERVER_RELOAD_TIME"]) )

    ofile = open("static/dqm_mirror.html","w")
    ofile.write( content )
    ofile.close()

  make_dqm_mirrow_page( cfg )
  start_server( cfg )




