# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import time, base64

if __name__ == '__main__':
  NAME = "dqmsquare_robber.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )

  sites  = cfg["ROBBER_TARGET_SITES"].split(",")
  opaths = cfg["ROBBER_OUTPUT_PATHS"].split(",")
  N_targets = len(sites)
  if len(sites) != len(opaths) :
    print( NAME, "len(ROBBER_TARGET_SITES) != len(ROBBER_OUTPUT_PATHS)", len(sites), len(opaths), "; exit" )
    exit()

  def save_site( content, path ):
    file = open( path, "w" )
    file.write( content )
    file.close()

  ### know python 2.7, firefox is required to be installed in the system
  if cfg["ROBBER_BACKEND"] == "selenium" :
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=cfg["ROBBER_GECKODRIVER_PATH"])

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
          except : pass

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
            except :
              n_tries -=1
              if bool(cfg["ROBBER_DEBUG"]) : print( NAME, "cant load and save image", opath_canv, ", N tries left = ", n_tries )
              time.sleep( int(cfg["SLEEP_TIME"]) )
              continue
            finally :
              break

      return driver.page_source.encode('utf-8')

    ### get old runs time-to-time
    def get_old_runs(driver, opath, link):
      if not bool(cfg["ROBBER_GRAB_OLDRUNS"]) : return
      driver.switch_to_window( driver.window_handles[-1] )
      if bool(cfg["ROBBER_DEBUG"]) : print( NAME, "load link", link )
      driver.get( link );
      time.sleep( int(cfg["SLEEP_TIME_LONG"]) )

      runs_done = []
      while True:
        runs_checkboxes = driver.find_elements_by_xpath( '//input[@type="checkbox"]' )

        if not runs_checkboxes : 
          print( NAME, "get_old_runs(): no checkbox in ", link, ", skip" )
          break
        scroll_shim( driver, runs_checkboxes[0] )
        ActionChains(driver).move_to_element(runs_checkboxes[0]).click().perform()

        all_runs_links = driver.find_elements_by_xpath( '//a[@class="label-run label label-info ng-binding ng-scope"]' )
        has_new_runs = False
        print all_runs_links

        for run_link in all_runs_links :
          if run_link.text in runs_done : continue
          if not run_link.text : continue
          has_new_runs = True

          output_path = opath + "_run" + run_link.text
          #try:
          if True:
            scroll_shim( driver, run_link )
            ActionChains(driver).move_to_element(run_link).click().perform()
            time.sleep( int(cfg["SLEEP_TIME"]) )
            content = dqm_2_grab(driver, output_path )
            if bool(cfg["ROBBER_DEBUG"]) : print( NAME, "get content from RUN", run_link.text, content[:100] )
            save_site( content, output_path )
          #except: pass

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
        except :
          print(NAME, "can't reach", sites[i], "skip ...")
          list_good_sites[i] = False

      time.sleep( int(cfg["SLEEP_TIME"]) )
      return list_good_sites

    ### loop
    n_iters = int(cfg["ROBBER_RELOAD_NITERS"]) + 1
    try:
      ### the DQM is updates by JavaScript, so we are
      while True:
        n_iters += 1
        if n_iters > int(cfg["ROBBER_RELOAD_NITERS"]) : 
          n_iters = 0
          list_good_sites = reload_pages()

          for i in range(N_targets):
            if not list_good_sites[i] : continue
            get_old_runs(driver, opaths[i], sites[i])

        for i in range(N_targets):
          if not list_good_sites[i] : continue

          driver.switch_to_window( driver.window_handles[i] )
          content = dqm_2_grab(driver, opaths[i])

          if bool(cfg["ROBBER_DEBUG"]) : print( NAME, "get content from", sites[i], content[:100] )
          save_site( content, opaths[i] )

        time.sleep( int(cfg["SLEEP_TIME"]) )
    except KeyboardInterrupt:
      print(NAME, 'interrupted, exiting')

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




