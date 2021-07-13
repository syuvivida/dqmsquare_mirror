# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import time, base64

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import logging
log = logging.getLogger(__name__)

if __name__ == '__main__':
  NAME = "dqmsquare_robber_oldruns.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  dqmsquare_cfg.set_log_handler(log, cfg["ROBBER_OLDRUNS_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["ROBBER_DEBUG"])

  log.info("begin ...")
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
    file = open( path, "w" )
    file.write( content )
    file.close()

  ### know python 2.7, firefox is required to be installed in the system
  if cfg["ROBBER_BACKEND"] == "selenium" :
    log.info("setup Selenium WebDriver ...")
    options = Options()
    options.headless = True
    driver = None

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
            log.warning( error_log )

      log.info("restart_browser(): setup Selenium WebDriver ...")
      driver = webdriver.Firefox(options=options, executable_path=cfg["ROBBER_GECKODRIVER_PATH"], log_path='./log/geckodriver.log')

      ### open new tabs
      log.info("restart_browser(): open tabs ...")
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
          except bool(cfg["ROBBER_DEBUG"]) or Exception as error_log:
            if error_logs.Check( "click on log button", error_log ) :
              log.warning( "dqm_2_grab(): cant click on log button" )
              log.warning( error_log )

      if bool( cfg["ROBBER_GRAB_GRAPHS"] ):
        if delete_old_canvases : 
          # remove outdate canvases to not show accidentally
          for j in xrange(9): # any big number
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
                log.warning( error_log )
              n_tries -=1
              time.sleep( int(cfg["SLEEP_TIME"]) )
              continue
            finally :
              log.debug( "dqm_2_grab(): save new graphs %s" % opath_canv )
              break

      log.debug("dqm_2_grab(): return data ... ")
      return driver.page_source.encode('utf-8')

    ### get old runs time-to-time
    def get_old_runs(driver, opath, link, parser_info={}):
      if not bool(cfg["ROBBER_GRAB_OLDRUNS"]) : return
      driver.switch_to_window( driver.window_handles[-1] )
      log.debug( "get_old_runs(): load link %s ..." % link )
      driver.get( link )
      time.sleep( int(cfg["SLEEP_TIME"]) )

      runs_done = []
      while True:
        runs_checkboxes = driver.find_elements_by_xpath( '//input[@type="checkbox"]' )

        if not runs_checkboxes : 
          log.warning( "get_old_runs(): no show-runs checkbox at %s, skip" % link )
          break

        try:
          scroll_shim( driver, runs_checkboxes[0] )
          ActionChains(driver).move_to_element(runs_checkboxes[0]).click().perform()
        except Exception as error_log:
          if error_logs.Check( "get_old_runs(): can't click on checkbox", error_log ) :
            log.warning( "get_old_runs(): can't click on checkbox at %s, skip" % sites[i] )
            log.warning( error_log )
          break

        all_runs_links = driver.find_elements_by_xpath( '//a[@class="label-run label label-info ng-binding ng-scope"]' )
        has_new_runs = False

        run_link_sorted = []
        for run_link in all_runs_links :
          if run_link.text in runs_done : continue
          if not run_link.text : continue
          if not run_link.text.isdigit() : continue
          run_link_sorted += [ run_link ]
        run_link_sorted = sorted( run_link_sorted, key=lambda x : -int(x.text) )

        # skip first oldrun which is ongoing
        if len(run_link_sorted) : run_link_sorted = run_link_sorted[1:]

        for run_link in run_link_sorted :
          has_new_runs = True
          output_path = dqmsquare_cfg.get_TMP_robber_page_name( opath, run_link.text )

          ### check if parser output in a bad state, than force reload
          n_ongoing_runs = 0
          try:
            for key, item_dic in parser_info.items():
              if run_link.text not in key : continue # same run number in the names of tmp robber and parser names
              if item_dic.has_key("States G") :
                n_ongoing_runs = int( item_dic["States G"] )
          except Exception as error_log:
            if bool(cfg["ROBBER_DEBUG"]) :
              log.warning( "get_old_runs(): can't get correctly parser state, ignore parser info" )
              log.warning( error_log )

          ### check if output already exist
          if not n_ongoing_runs :
            if os.path.isfile( output_path ) :
              timestamp = os.path.getmtime( output_path )
              now = time.time()
              if abs(timestamp - now) / 60 / 60 < float(cfg["ROBBER_OLDRUNS_UPDATE_TIME"]) :
                log.debug("get_old_runs(): skip oldrun link: " + run_link.text)
                continue
          else : 
            log.debug( "force reload oldrun link due to the parser state: " + run_link.text)

          ### click and load content
          log.debug( "process oldrun link: " + run_link.text)
          try:
            scroll_shim( driver, run_link )
            ActionChains(driver).move_to_element(run_link).click().perform()
            time.sleep( int(cfg["SLEEP_TIME_LONG"]) )
            content = dqm_2_grab(driver, output_path, delete_old_canvases=False )
            log.debug( "get_old_runs(): get content from old run " + sites[i] + "\"" + content[:100] + "...\"" )
            save_site( content, output_path )
          except Exception as error_log:
            if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "get_old_runs(): can't reach %s skip" % sites[i], error_log ) :
              log.warning( "get_old_runs(): can't reach %s skip ..." % sites[i] )
              log.warning( error_log )

          runs_done += [ run_link.text ]

        if has_new_runs : continue
        break

    ### loop
    reload_driver = False
    restart_browser()
    log.info("loop ...")
    while True:
      try:
        ### get content from old sites
        for i in range(N_targets):
          log.debug( "get old run contents from " + sites[i] )
          parser_page_info = dqmsquare_cfg.get_parser_info( parser_paths[i] )
          log.debug( "parser metacontent %s " % str(parser_page_info) )
          get_old_runs(driver, opaths[i], sites[i], parser_page_info)

      except KeyboardInterrupt:
        break
      except Exception as error_log:
        if bool(cfg["ROBBER_DEBUG"]) or error_logs.Check( "grabber crashed", error_log ) :
          log.warning("grabber crashed ...")
          log.warning(error_log)
          reload_driver = True

      while reload_driver:
        log.info("going to reload driver ... ")
        try:
          restart_browser()
        except Exception as error_log:
          log.warning("not able to reload ... sleep more")
          log.warning(error_log)
          time.sleep( int(cfg["SLEEP_TIME_LONG"]) )
          continue
        log.info("going to reload driver ... ok")
        reload_driver = False

      log.debug( "z-Z-z" )
      time.sleep( int(cfg["SLEEP_TIME_LONG"]) )

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




