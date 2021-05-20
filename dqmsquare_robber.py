# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import time, base64

if __name__ == '__main__':
  NAME = "dqmsquare_rebber.py:"
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

    for i in range(N_targets):
      driver.execute_script("window.open('about:blank');")

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

    list_good_sites = reload_pages()

    n_iters = 0
    try:
      ### the DQM is updates by JavaScript, so we are
      while True:
        n_iters += 1
        if n_iters > int(cfg["ROBBER_RELOAD_NITERS"]) : 
          n_iters = 0
          list_good_sites = reload_pages()

        for i in range(N_targets):
          if not list_good_sites[i] : continue

          driver.switch_to_window( driver.window_handles[i] )

          if bool( cfg["ROBBER_GRAB_LOGS"] ):
            def scroll_shim(passed_in_driver, object):
              passed_in_driver.execute_script( 'window.scrollTo(%s,%s);' % (object.location['x'], object.location['y']) )
              passed_in_driver.execute_script( 'window.scrollBy(0, -120);' )

            all_logs = driver.find_elements_by_xpath("//a[@class='hover-hide btn btn-default btn-xs']")
            for span in all_logs:
              if span.get_attribute("ng-click") == "_show_inline = 'log'":
                scroll_shim( driver, span )
                ActionChains(driver).move_to_element(span).click().perform()

          print bool( cfg["ROBBER_GRAB_GRAPHS"] )
          if bool( cfg["ROBBER_GRAB_GRAPHS"] ):
            canvases = driver.find_elements_by_css_selector("canvas")
            print canvases
            for j, canv in enumerate(canvases):
              canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canv)
              canvas_png = base64.b64decode(canvas_base64)
              opath_canv = opaths[i] + "canv_" + str(j) + ".png"
              with open(opath_canv, 'wb') as f:
                f.write(canvas_png)

          content = driver.page_source.encode('utf-8')

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

  ### no nothing about JS
  elif cfg["ROBBER_BACKEND"] == "urllib" :
    import urllib
    f = urllib.urlopen( sites[0] )
    content = f.read()
    if bool(cfg["ROBBER_DEBUG"]) : print( NAME, content )




