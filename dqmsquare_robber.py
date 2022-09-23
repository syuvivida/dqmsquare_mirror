# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import time, base64, os, sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import logging
log = logging.getLogger(__name__)

if __name__ == '__main__':
  NAME = "dqmsquare_robber.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  dqmsquare_cfg.set_log_handler(log, cfg["ROBBER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["ROBBER_DEBUG"])
  is_k8 = bool( cfg["ROBBER_K8"] )

  selenium_secret="changeme"
  if is_k8: selenium_secret = dqmsquare_cfg.get_env_secret(log, 'DQM_PASSWORD')

  log.info("\n\n\n =============================================================================== ")
  log.info("\n\n\n begin dqmsquare_robber ======================================================== ")
  error_logs = dqmsquare_cfg.ErrorLogs()

  sites  = cfg["ROBBER_TARGET_SITES"].split(",")
  opaths = cfg["ROBBER_OUTPUT_PATHS"].split(",")
  parser_paths = cfg["PARSER_OUTPUT_PATHS"].split(",")
  N_targets = len(sites)
  if len(sites) != len(opaths) :
    log.error("len(ROBBER_TARGET_SITES) != len(ROBBER_OUTPUT_PATHS) %d %d; exit" % ( len(sites), len(opaths) ) )
    exit()
  if len(parser_paths) != len(opaths):
    log.error("len(PARSER_INPUT_PATHS) != len(PARSER_OUTPUT_PATHS) %d %d; exit" % ( len(parser_paths), len(opaths) ) )
    exit()

  def save_site( content, path ):
    file = open( path, "w", encoding="utf8" )
    file.write( content )
    file.close()

  ### know python 2.7, firefox is required to be installed in the system
  if cfg["ROBBER_BACKEND"] == "selenium" :
    log.info("setup Selenium WebDriver ...")
    options = Options()
    options.headless = True
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-application-cache')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")
    if str(cfg["ROBBER_FIREFOX_PATH"]) : options.binary_location = str(cfg["ROBBER_FIREFOX_PATH"])
    driver = None

    ### login cmsweb dqm
    def cmsweb_dqm_login( driver ):
      if not is_k8 : return
      driver.get( str(cfg["ROBBER_K8_LOGIN_PAGE"]) );
      driver.add_cookie({"name": str(cfg["FFF_SECRET_NAME"]), "value": selenium_secret})
      time.sleep( int(cfg["SLEEP_TIME"]) )

    ### setup browser driver
    def restart_browser():
      global driver
      if driver :
        log.info("restart_browser(): close Selenium WebDriver ...")
        try:
          driver.close()
          driver.quit()
        except Exception as error_log:
          if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "", error_log ) :
            log.warning( "restart_browser(): can't close the browser, mb it already crashed?" )
            log.warning( repr(error_log) )

      log.info("restart_browser(): setup Selenium WebDriver ...")
      if str(cfg["ROBBER_FIREFOX_PROFILE_PATH"]):
        fp = webdriver.FirefoxProfile( str(cfg["ROBBER_FIREFOX_PROFILE_PATH"]) )
        driver = webdriver.Firefox(fp, options=options, executable_path=cfg["ROBBER_GECKODRIVER_PATH"], log_path=cfg['ROBBER_GECKODRIVER_LOG_PATH'])
      else :
        driver = webdriver.Firefox(options=options, executable_path=cfg["ROBBER_GECKODRIVER_PATH"], log_path=cfg['ROBBER_GECKODRIVER_LOG_PATH'])

      ### open new tabs
      log.info("restart_browser(): open tabs ...")
      for i in range(N_targets):
        driver.execute_script("window.open('about:blank');")

    ### define scroll hack
    def scroll_shim(driver, object):
      driver.execute_script( 'window.scrollTo(%s,%s);' % (object.location['x'], object.location['y']) )
      driver.execute_script( 'window.scrollBy(0, -120);' )

    ### def DQM^2 site grabber
    def dqm_2_grab(driver, save_prefix, delete_old_canvases=False):
      if bool( cfg["ROBBER_GRAB_LOGS"] ):
        log.debug("dqm_2_grab(): load logs ... ")
        all_logs = driver.find_elements_by_xpath("//a[@class='hover-hide btn btn-default btn-xs']")
        for span in all_logs:
          try : 
            if span.get_attribute("ng-click") == "_show_inline = 'log'":
              scroll_shim( driver, span )
              ActionChains(driver).move_to_element(span).click().perform()
          except Exception as error_log:
            if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "click on log button", error_log ) :
              log.warning( "dqm_2_grab(): can't click on log button" )
              log.warning( repr(error_log) )

      if bool( cfg["ROBBER_GRAB_GRAPHS"] ):
        if delete_old_canvases : 
          # remove outdate canvases to not show accidentally
          for j in range(9): # any big number
            opath_canv = dqmsquare_cfg.get_TMP_robber_canvas_name(save_prefix, str(j))
            dqmsquare_cfg.delete_file( opath_canv, log )

        log.debug("dqm_2_grab(): load graphs ... ")
        canvases = driver.find_elements_by_css_selector("canvas")
        for j, canv in enumerate(canvases):
          opath_canv = dqmsquare_cfg.get_TMP_robber_canvas_name(save_prefix, str(j))
          n_tries = 5
          while n_tries > 0:
            try : 
              canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canv)
              canvas_png = base64.b64decode(canvas_base64)
              with open(opath_canv, 'wb') as f:
                f.write(canvas_png)
            except Exception as error_log:
              if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "cant load and save image", error_log ) :
                log.warning( "dqm_2_grab(): can't load and save image %s N tries left = %d" % ( opath_canv, n_tries) )
                log.warning( repr(error_log) )
              n_tries -=1
              time.sleep( int(cfg["SLEEP_TIME"]) )
              continue
            finally :
              log.debug( "dqm_2_grab(): save new graphs %s" % opath_canv )
              break

      log.debug("dqm_2_grab(): return data ... ")
      return driver.page_source

    ### start site sessions
    list_good_sites = []
    def reload_pages():
      global list_good_sites
      list_good_sites = [ False for i in range(N_targets) ]
      for i in range(N_targets):
        driver.switch_to_window( driver.window_handles[i] )
        try:
          if is_k8 : cmsweb_dqm_login( driver)
          driver.get( sites[i] );
          list_good_sites[i] = True
        except Exception as error_log:
          if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "reload_pages(): can't reach %s skip" % sites[i], error_log ) :
            log.warning( "reload_pages(): can't reach %s skip ..." % sites[i] )
            log.warning( repr(error_log) )
          list_good_sites[i] = False

      time.sleep( int(cfg["SLEEP_TIME"]) )
      return list_good_sites

    ### loop
    reload_driver = False
    restart_browser()
    n_iters = int(cfg["ROBBER_RELOAD_NITERS"]) + 1
    N_loops = 0
    log.info("loop ...")
    while True:
      try:
        ### reload all pages time-to-time
        n_iters += 1
        if n_iters > int(cfg["ROBBER_RELOAD_NITERS"]) or not sum(list_good_sites): 
          n_iters = 0
          list_good_sites = reload_pages()

        ### get content from active sites
        for i in range(N_targets):
          if not list_good_sites[i] : continue

          driver.switch_to_window( driver.window_handles[i] )
          content = dqm_2_grab(driver, opaths[i], delete_old_canvases=True)

          log.debug( "get content from " + sites[i] + " - \"" + content[:100] + "...\"" )
          save_site( content, opaths[i] )
          if is_k8: driver.refresh()

      except KeyboardInterrupt:
        break
      except Exception as error_log:
        if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "grabber crashed", error_log ) :
          log.warning("grabber crashed ...")
          log.warning( repr(error_log) )
          reload_driver = True

      N_loops += 1
      if int(cfg["FIREFOX_RELOAD_NITERS"]) and N_loops > int(cfg["FIREFOX_RELOAD_NITERS"]) : 
        reload_driver = True
        N_loops       = 0
        log.info("N_loops > int(cfg[\"FIREFOX_RELOAD_NITERS\"])")

      while reload_driver:
        log.info("going to reload driver ... ")
        try:
          restart_browser()
        except Exception as error_log:
          log.warning("not able to reload ... sleep more")
          log.warning( repr(error_log) )
          time.sleep( int(cfg["SLEEP_TIME_LONG"]) )
          continue
        log.info("going to reload driver ... ok")
        n_iters = int(cfg["ROBBER_RELOAD_NITERS"]) + 1
        reload_driver = False

      log.debug( "z-Z-z" )
      time.sleep( int(cfg["SLEEP_TIME"]) )

    driver.close()
    driver.quit()

  ### only work for python 3.6
  elif cfg["ROBBER_BACKEND"] == "HTMLSession" :
    from requests_html import HTMLSession
    session = HTMLSession()
    response = session.get( sites[0] )
    response.html.render()
    content = response.html.html
    if bool(cfg["ROBBER_DEBUG"]) : print( NAME, content )

  ### know nothing about JS
  elif cfg["ROBBER_BACKEND"] == "urllib" :
    import urllib
    f = urllib.urlopen( sites[0] )
    content = f.read()
    if bool(cfg["ROBBER_DEBUG"]) : print( NAME, content )




