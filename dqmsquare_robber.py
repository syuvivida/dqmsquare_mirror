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
  NAME = "dqmsquare_robber.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  dqmsquare_cfg.set_log_handler(log, cfg["ROBBER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["ROBBER_DEBUG"])
  log.info("begin ...")

  sites  = cfg["ROBBER_TARGET_SITES"].split(",")
  opaths = cfg["ROBBER_OUTPUT_PATHS"].split(",")
  N_targets = len(sites)
  if len(sites) != len(opaths) :
    log.error("len(ROBBER_TARGET_SITES) != len(ROBBER_OUTPUT_PATHS) %d %d; exit" % ( len(sites), len(opaths) ) )
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
    driver = webdriver.Firefox(options=options, executable_path=cfg["ROBBER_GECKODRIVER_PATH"])
    log.info("setup Selenium WebDriver ... ok")

    ### define scroll hack
    def scroll_shim(driver, object):
      driver.execute_script( 'window.scrollTo(%s,%s);' % (object.location['x'], object.location['y']) )
      driver.execute_script( 'window.scrollBy(0, -120);' )

    ### open new tabs
    for i in range(N_targets):
      driver.execute_script("window.open('about:blank');")
    if bool(cfg["ROBBER_GRAB_OLDRUNS"]) : driver.execute_script("window.open('about:blank');")

    ### def DQM^2 site grabber
    def dqm_2_grab(driver, save_prefix):
      if bool( cfg["ROBBER_GRAB_LOGS"] ):
        all_logs = driver.find_elements_by_xpath("//a[@class='hover-hide btn btn-default btn-xs']")
        for span in all_logs:
          try : 
            if span.get_attribute("ng-click") == "_show_inline = 'log'":
              scroll_shim( driver, span )
              ActionChains(driver).move_to_element(span).click().perform()
          except Exception as error_log:
            log.warning( "cant click on log button" )
            log.warning( error_log )

      if bool( cfg["ROBBER_GRAB_GRAPHS"] ):
        canvases = driver.find_elements_by_css_selector("canvas")
        for j, canv in enumerate(canvases):
          opath_canv = save_prefix + "_canv" + str(j)
          n_tries = 5
          while n_tries > 0:
            try : 
              canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canv)
              canvas_png = base64.b64decode(canvas_base64)
              with open(opath_canv, 'wb') as f:
                f.write(canvas_png)
            except Exception as error_log:
              n_tries -=1
              log.warning( "cant load and save image %s N tries left = %d" % ( opath_canv, n_tries) )
              log.warning( error_log )
              time.sleep( int(cfg["SLEEP_TIME"]) )
              continue
            finally :
              break

      return driver.page_source.encode('utf-8')

    ### get old runs time-to-time
    def get_old_runs(driver, opath, link):
      if not bool(cfg["ROBBER_GRAB_OLDRUNS"]) : return
      driver.switch_to_window( driver.window_handles[-1] )
      log.debug( "load link %s" % link )
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
          log.warning( "get_old_runs(): can't click on checkbox at %s, skip" % sites[i] )
          log.warning( error_log )
          break

        all_runs_links = driver.find_elements_by_xpath( '//a[@class="label-run label label-info ng-binding ng-scope"]' )
        has_new_runs = False

        for run_link in all_runs_links :
          if run_link.text in runs_done : continue
          if not run_link.text : continue
          has_new_runs = True
          output_path = opath + "_run" + run_link.text

          ### check if output already exist
          if os.path.isfile( output_path ) :
            timestamp = os.path.getmtime( output_path )
            now = time.time()
            if abs(timestamp - now) / 60 / 60 < int(cfg["ROBBER_OLDRUNS_UPDATE_TIME"]) :
              log.debug("skip oldrun link: " + run_link)
              continue
  
          ### click and load content
          try:
            scroll_shim( driver, run_link )
            ActionChains(driver).move_to_element(run_link).click().perform()
            time.sleep( int(cfg["SLEEP_TIME_LONG"]) )
            content = dqm_2_grab(driver, output_path )
            log.debug( "get content from old run " + sites[i] + "\"" + content[:100] + "...\"" )
            save_site( content, output_path )
          except Exception as error_log:
            log.warning( "can't reach %s skip ..." % sites[i] )
            log.warning( error_log )

          runs_done += [ run_link.text ]

        if has_new_runs : continue
        break

    ### start site sessions
    def reload_pages():
      list_good_sites = [ False for i in xrange(N_targets) ]
      for i in range(N_targets):
        driver.switch_to_window( driver.window_handles[i] )
        try:
          driver.get( sites[i] );
          list_good_sites[i] = True
        except Exception as error_log:
          log.warning( "can't reach %s skip ..." % sites[i] )
          log.warning( error_log )
          list_good_sites[i] = False

      time.sleep( int(cfg["SLEEP_TIME"]) )
      return list_good_sites

    ### loop
    n_iters = int(cfg["ROBBER_RELOAD_NITERS"]) + 1
    log.info("loop ...")
    while True:
      try:
        n_iters += 1
        if n_iters > int(cfg["ROBBER_RELOAD_NITERS"]) : 
          n_iters = 0
          list_good_sites = reload_pages()

          for i in range(N_targets):
            if not list_good_sites[i] : continue
            log.debug( "get old run contents from " + sites[i] )
            get_old_runs(driver, opaths[i], sites[i])

        for i in range(N_targets):
          if not list_good_sites[i] : continue

          driver.switch_to_window( driver.window_handles[i] )
          content = dqm_2_grab(driver, opaths[i])

          log.debug( "get content from " + sites[i] + "\"" + content[:100] + "...\"" )
          save_site( content, opaths[i] )

      except KeyboardInterrupt:
        break
      except Exception as error_log:
        log.warning("grabbed crashed ...")
        log.warning(error_log)

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




