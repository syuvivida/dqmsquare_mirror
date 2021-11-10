import time

geckodriver="../../../DQM/TMP/dqmsquare_mirror/geckodriver/geckodriver"
profile="/home/pmandrik/.mozilla/firefox/vm352ut3.default-default"
profile="/home/pmandrik/vm352ut3.default-default"
firefox="/usr/bin/firefox"
if False:
  geckodriver="/usr/bin/geckodriver"
  profile="/firefox_profile_path"
  firefox="/opt/firefox/firefox"

def test_selenium_firefox():
  print("========= 0. imports")
  from selenium import webdriver
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.firefox.options import Options
  from selenium.webdriver.common.action_chains import ActionChains
  from selenium.webdriver.firefox.service import Service

  print("========= 1. set options")
  options = Options()
  options.headless = True
  options.add_argument("start-maximized")
  options.add_argument("disable-infobars")
  options.add_argument("--disable-extensions")
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-application-cache')
  options.add_argument('--disable-gpu')
  options.add_argument("--disable-dev-shm-usage")
  options.binary_location = firefox

  print("========= 2. load drivers")
  fp = webdriver.FirefoxProfile( profile )
  driver = webdriver.Firefox(fp, executable_path=geckodriver, options=options)

  print("========= 3. get google.com")
  driver.get( "https://google.com" );
  time.sleep( 3 )
  print(   driver.page_source.encode('utf-8') )

def test_selenium_firefox_cert():
  print("========= 0. imports")
  from selenium import webdriver
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.firefox.options import Options
  from selenium.webdriver.common.action_chains import ActionChains
  from selenium.webdriver.firefox.service import Service

  print("========= 1. set options")
  options = Options()
  options.headless = True
  options.add_argument("start-maximized")
  options.add_argument("disable-infobars")
  options.add_argument("--disable-extensions")
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-application-cache')
  options.add_argument('--disable-gpu')
  options.add_argument("--disable-dev-shm-usage")
  options.binary_location = firefox

  print("========= 2. load drivers")
  fp = webdriver.FirefoxProfile( profile )
  driver = webdriver.Firefox(fp, executable_path=geckodriver, options=options)

  print("========= 3. get https://cmsweb-testbed.cern.ch/dqm/dqm-square/")
  driver.get( "https://cmsweb-testbed.cern.ch/dqm/dqm-square/" );
  time.sleep( 3 )
  print(   driver.page_source.encode('utf-8') )

if __name__ == '__main__':
  print("\n\n\n  test_selenium_firefox():")
  #test_selenium_firefox()

  print("\n\n\n  test_selenium_firefox_cert():")
  test_selenium_firefox_cert()




