# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg

import random, time, os
from datetime import datetime
from collections import defaultdict

from bs4 import BeautifulSoup

import logging
log = logging.getLogger(__name__)

class DQMPageData( ):
  def __init__(self,  cfg, input_file="", output_file=""):
    self.servers = []
    self.jobs_col_attr = ["Timestamp", "TD", "Hostname", "State", "Tag", "LS", "RSS", "Total Ev.", "LOGS"]
    self.jobs = []
    self.jobs_attr = []
    self.jobs_logs = []
    self.cfg = cfg
    self.output_file = output_file
    self.input_file  = input_file
    self.run_number = "-"
    self.origin_run_number = ""
    self.link_prefix = self.cfg["PARSER_LINK_PREFIX"]
    self.old_runs_pages = []

    self.colors = {"G" : "#52BE80", "R" : "#EC7063", "Y" : "#F4D03F", "title" : "#2471a3" }

  def GetJoblogFileName(self, index):
    name = dqmsquare_cfg.get_TMP_parser_log_name(self.output_file, index)
    link = self.link_prefix + name
    return name, link

  def AddServer(self, name, state):
    d = {"name" : self.GetServerName(name), "state" : state}
    d["state_attr"] = 'style="background-color:' + self.colors["Y"] + '"'
    if "live" in state : d["state_attr"] = 'style="background-color:' + self.colors["G"] + '"'
    if "http mode" in state : d["state_attr"] = 'style="background-color:' + self.colors["G"] + '"'
    if "closed" in state : d["state_attr"] = 'style="background-color:' + self.colors["R"] + '"'
    self.servers += [ d ]

  def GetServerName(self, name):
    txt = name.split("-")
    return txt[0] + "-...-" + txt[-1].split(".")[0]

  def CountStates(self):
    R, G, Y = 0, 0, 0
    for job in self.jobs:
      state = job[3]
      if "R" == state   : G+=1
      elif state == "0" : Y+=1
      else              : R+=1
    return R, G, Y

  def AddJob(self, time, ltime, sname, state, tag, lumi, rss, nevents, logs ):
    # self.jobs += [ {"time" : time, "ltime" : ltime, "sname" : sname, "state" : state, "tag" : tag, "lumi" : lumi, "rss" : rss, "nevents" : nevents} ]
    self.jobs += [ [time, ltime, self.GetServerName( sname ), state, tag, lumi, rss, nevents, logs] ]
    self.jobs_logs += [""]

    attrs = {}
    if "R" == state   : attrs['row_attr'] = 'style="background-color:' + self.colors["G"] + '"'
    elif state == "0" : attrs['row_attr'] = 'style="background-color:' + self.colors["Y"] + '"'
    else              : attrs['row_attr'] = 'style="background-color:' + self.colors["R"] + '"'
    self.jobs_attr += [ attrs ]

  def AddJobLogs( self, logs ):
    self.jobs_logs[-1] += logs

    name, link = self.GetJoblogFileName( len(self.jobs)-1 )
    self.jobs[-1][-1] = '<a href="'+link+'" target="_blank"> -> </a>'

    pass

  def Dump(self, write_out=True, write_out_logs=True):
    content = '<p style="clear:both;margin-bottom:5px"></p>\n'

    # IF past run still has ongoing jobs due to delay of robber THAN delete the source file
    state_R, state_G, state_Y = self.CountStates()
    content += '<!--States R:' + str(state_R) + '-->\n'
    content += '<!--States G:' + str(state_G) + '-->\n'
    content += '<!--States Y:' + str(state_Y) + '-->\n\n'

    ### run
    content += '<p style="margin-bottom:1px"> '
    content += 'Run: '
    content += '<strong>' + str(self.run_number) 
    if self.origin_run_number : content += ' (' + str(self.origin_run_number) + ')'
    content += '</strong> &nbsp;&nbsp;&nbsp;&nbsp;'

    ### old runs links:
    if self.old_runs_pages : 
      content += 'Old runs: '
      for run_id, link in self.old_runs_pages :
        if str(run_id) == str(self.run_number) : continue # extra skip the duplicate of on-going run in this list
        if link : 
          content += '<a href="'+self.link_prefix + link+'" target="_blank"> <strong>' + run_id + '</strong> </a> &nbsp;'
        else : 
          content += '<strong>' + run_id + '</strong>&nbsp;'
      content += '\n\n'

    ### timestamps
    parser_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    robber_timestamp = datetime.fromtimestamp(os.path.getmtime( self.input_file )).strftime("%Y-%m-%d %H:%M:%S") if self.input_file else "-"
    content +='<p style="margin-bottom:0px"> DQM &#x25A0 parser time: ' + parser_timestamp + '</p>'
    content +='<p style="margin-top:0px;padding-top:0;margin-bottom:15px"> DQM &#x25A0 grabber time: ' + robber_timestamp + '</p>'

    ### server table
    content += '<table id="servers" style="text-align:center;margin-top:10px;margin-bottom:10px" border=1 frame=hsides rules=rows >\n'
    content += '<tr style="font-weight:bold;"> '
    content += '<td class="job_table_cell"> Hostname <td> '
    content += '<td class="job_table_cell"> State <td> '
    content += "</td>\n"
    for row in self.servers :
      content += "<tr " + row["state_attr"] + "> " 
      content += '<td class="server_table_cell">' + row["name"] + "<td> "
      content += "<td>" + row["state"] + "<td> "
      content += "</td>\n"
    content += "</table>\n"

    ### run number & legends
    content += '<p style="margin-bottom:1px"> '
    content += 'Known cmssw jobs: <strong>' + str(len(self.jobs)) + '</strong> &nbsp;&nbsp;&nbsp;&nbsp;'
    content += 'Legend: '
    content += '<strong><span style="background-color:' + self.colors["G"] + '"> &nbsp;&nbsp; running ' + str(state_G) + ' &nbsp;&nbsp; </span></strong>'
    content += '<strong><span style="background-color:' + self.colors["Y"] + '"> &nbsp;&nbsp; stopped ' + str(state_Y) + ' &nbsp;&nbsp; </span></strong>'
    content += '<strong><span style="background-color:' + self.colors["R"] + '"> &nbsp;&nbsp; crashed ' + str(state_R) + '&nbsp;&nbsp; </span></strong>'
    content += ' </p>\n'

    ### jobs table
    content += '<table id="jobs" style="text-align:center;margin-top:1px;margin-bottom:10px" border=1 frame=hsides rules=rows >\n'
    
    content += '<tr style="font-weight:bold;"> '
    for c_title in self.jobs_col_attr : 
      content += '<td class="job_table_cell">' + c_title + "<td> "
    content += "</td>\n"
      
    for attr, row in zip(self.jobs_attr, self.jobs) :
      content += "<tr " + attr['row_attr'] + "> "
      for col in row : 
        content += '<td class="job_table_cell">' + col + "</td> "
      content += "</tr>\n"
    content += "</table>\n"

    ### images if exist
    if self.input_file : 
      dir_name = os.path.dirname(self.input_file)
      fname    = os.path.basename(self.input_file)
      for item in os.listdir( dir_name ) : 
        if not dqmsquare_cfg.is_TMP_robber_canvas_name( fname, item ) : continue
        content += "<img src=" + self.link_prefix + os.path.join(dir_name, item) + ">\n"

    ### write out body
    if self.output_file and write_out : 
      file = open( self.output_file, "w" )
      file.write( content )
      file.close()

    ### write out logs
    if self.output_file and write_out_logs :
      for i, jlog in enumerate( self.jobs_logs ) :
        oname, link = self.GetJoblogFileName( i )
        file = open( oname,"w" )
        file.write( jlog )
        file.close()

    return content

def create_dummy_page( path ):
  text = "Waiting for the input from grabber ... "
  file = open( path, "w" )
  file.write( text )
  file.close()

if __name__ == '__main__':
  NAME = "dqmsquare_parser.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  dqmsquare_cfg.set_log_handler(log, cfg["PARSER_LOG_PATH"], cfg["LOGGER_ROTATION_TIME"], cfg["LOGGER_MAX_N_LOG_FILES"], cfg["PARSER_DEBUG"])

  log.info("\n\n\n =============================================================================== ")
  log.info("\n\n\n dqmsquare_parser ============================================================== ")

  # prefix = "/dqm/dqm-square/"
  # if cfg["SERVER_LOCAL"] :  prefix = ""

  ipaths = cfg["PARSER_INPUT_PATHS"].split(",")
  opaths = cfg["PARSER_OUTPUT_PATHS"].split(",")
  N_targets = len(ipaths)
  if len(ipaths) != len(opaths):
    log.error("len(PARSER_INPUT_PATHS) != len(PARSER_OUTPUT_PATHS) %d %d; exit" % ( len(ipaths), len(opaths) ) )
    exit()

  def load_html(path):
    try:
      ifile = open( path ,"r" )
      html_doc = ifile.read( )
      ifile.close()
      return html_doc
    except:
      return ""

  # return True if [1. input file yuanger than output file] [2. output file yuanger than threshold]
  def check_lifetime_output(inp_name, out_name, threshold) :
    if not os.path.isfile( out_name ) : return True
    timestamp = os.path.getmtime( out_name )
    now = time.time()
    if os.path.isfile( inp_name ):
      timestamp_input = os.path.getmtime( inp_name )
      if timestamp_input > timestamp : return True
    if abs(timestamp - now) / 60 / 60 < threshold: return False
    return True
    
  def parse_dqmsquare_page( input_page, output_page ):
    log.debug("parse_dqmsquare_page(): %s -> %s" % (input_page, output_page) )

    html_doc = load_html( input_page )
    if not html_doc :
      log.info( "waiting for the input file %s" % input_page )
      return None

    soup = BeautifulSoup(html_doc, 'html.parser')
    soup.prettify()
    dqm_data = DQMPageData( cfg, input_page, output_page )

    ### get server states ...
    for link in soup.find_all( 'a', attrs={"class":"ng-binding"} ):
      if link["class"][0] != u'ng-binding' : continue
      if "href" in link.attrs : continue
      if "ng-href" in link.attrs : continue

      try:
        name = link.contents[0].split()[0]
        state = link.findChildren("strong" , recursive=False)[0].text
        log.debug("add server %s %s" % (name, state) )
        dqm_data.AddServer( name, state )
      except : pass

    ### get Run number ...
    run_number = "-"
    breadcrumbs = soup.find_all("ol", {"class": "breadcrumb"}  )
    for bread in breadcrumbs:
      has_text = bread.find_all("span", string="Known cmssw jobs")
      if len(has_text) : 
        spans = bread.find_all('strong', {"class": "ng-binding"} )
        if len(spans) : run_number = spans[0].text
        log.debug("get run number %s" % (spans[0].text) )
        break
    dqm_data.run_number = run_number

    ### original Run number
    origin_run_number = ""
    breadcrumbs = soup.find_all("div", {"ng-controller": "CachedDocumentCtrl"}  )
    for bread in breadcrumbs:
      candidate = bread.find_all("strong", {"class": "ng-binding"} )
      for cand in candidate:
        if not cand.has_attr("title") : continue
        for part in cand["title"].split("/") :
          if not "run" in part : continue
          origin_run_number = part[len("run"):]
          log.debug("get original run number %s" % origin_run_number )
          break
    dqm_data.origin_run_number = origin_run_number

    ### get jobs states ...
    for table in soup.find_all( 'tbody' ):
      if table.attrs : continue

      # table_body = table.find('tbody')
      rows = table.find_all('tr')
      data = []
      for row_index, row in enumerate(rows):
        if row.has_attr("ng-if") :
          if row["ng-if"] != "_show_inline == 'log'" : continue
          logs_parts = row.find_all('dqm-log')
          if not logs_parts : continue
          logs = "\n ... \n".join( [ ele.text.strip() for ele in logs_parts ] )
          log.debug("add logs for job row %d" % row_index )
          dqm_data.AddJobLogs( logs )
          continue

        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        dtime, ltime, sname, state, tag, lumi, rss, nevents,logs = "-","-","-","-","-","-","-","-","-"

        def get_def_I(index):
          try:    return cols[ index ].strip()
          except: return "-"

        def get_def_II(index, sindex):
          try:    return cols[index].split("\n")[sindex].strip()
          except: return "-"

        dtime   = get_def_II(0,0)
        ltime   = get_def_II(0,1)
        sname   = get_def_I(1)
        state   = get_def_II(3,0)
        tag     = get_def_I(4)
        lumi    = get_def_I(5)
        rss     = get_def_I(6)
        nevents = get_def_II(7,0)

        log.debug("add job" + str(dtime) + " " + str(ltime) + " " + str(sname) + " " + str(state) + " " + str(tag) + " " + str(lumi) + " " + str(rss) + " " + str(nevents))
        if bool(cfg["PARSER_RANDOM"]): ltime = str( random.randint(0, 100) )
        dqm_data.AddJob(dtime, ltime, sname, state, tag, lumi, rss, nevents, logs )

    return dqm_data

  ### parser loop === >
  processes_pages_n = 0
  lastlog_timestamp = 0
  while True:
    processes_pages = []

    ### targets old runs ...
    old_runs_pages_dic = defaultdict( list )
    if bool(cfg["PARSER_PARSE_OLDRUNS"]) : 
      try:
        for i in range(N_targets):
          dir_name = os.path.dirname( ipaths[i] )
          fname    = os.path.basename(ipaths[i] )

          input_oldrun_files = []
          for item in os.listdir( dir_name ) : 
            if item == fname : continue # skip ongoing runs here
            if not dqmsquare_cfg.is_TMP_robber_page( fname, item ) : continue
            f = os.path.join(dir_name, item)
            input_oldrun_files += [ [f, os.path.getmtime( f )] ]

          input_oldrun_files = sorted( input_oldrun_files, key=lambda x : -x[1] )
          input_oldrun_files = input_oldrun_files[:min(len(input_oldrun_files), int(cfg["PARSER_MAX_OLDRUNS"]))]

          for f, created_time in input_oldrun_files :
            run_id   = dqmsquare_cfg.get_TMP_robber_page_run( f )
            out_name = dqmsquare_cfg.get_TMP_parser_page_name( opaths[i], run_id )

            if not check_lifetime_output(f, out_name, float(cfg["PARSER_OLDRUNS_UPDATE_TIME"])) :
              log.debug("skip oldrun " + str(run_id))
              old_runs_pages_dic[ i ] += [ [run_id, out_name] ]
              continue

            log.debug("parse oldrun " + str(run_id))
            dqm_data = parse_dqmsquare_page( f, out_name )
            old_runs_pages_dic[ i ] += [ [run_id, out_name] ]
            dqm_data.Dump(True, True)
            processes_pages += [ f ]

          if i in old_runs_pages_dic:
            old_runs_pages_dic[ i ] = sorted( old_runs_pages_dic[ i ], key=lambda x : -int(x[0]) )

      except Exception as error_log:
        print( error_log )
        log.warning("parser crashed for old runs ...")
        log.warning( repr(error_log) )

    ### targets ...
    try:
      for i in range(N_targets):
        dqm_data = parse_dqmsquare_page( ipaths[i], opaths[i] )
        if not dqm_data : 
          create_dummy_page( opaths[i] )
          continue
        dqm_data.old_runs_pages = old_runs_pages_dic[ i ]
        dqm_data.Dump(True, True)
        processes_pages += [ ipaths[i] ]

      if bool(cfg["TMP_CLEAN_FILES"]) :
        for folder in cfg["TMP_FOLDER_TO_CLEAN"].split(",") :
          try:
            dqmsquare_cfg.clean_folder( folder, int(cfg["TMP_FILES_LIFETIME"]), log )
          except Exception as error_log:
            log.warning("parser crashed for cleaning tmp folders ...")
            log.warning( repr(error_log) )
    except Exception as error_log:
      log.warning("parser crashed for current runs ...")
      log.warning( repr(error_log) )

    ### print out ...
    try:
      processes_pages_n += len( processes_pages )
      if abs( lastlog_timestamp - time.time() ) > float(cfg["PARSER_LOG_UPDATE_TIME"]) * 60 :
        lastlog_timestamp = time.time()
        log.info("processes N pages = %d" % processes_pages_n )
        processes_pages_n = 0
      else : log.debug("processes pages %s" % ",".join(processes_pages) )
    except Exception as error_log:
      log.warning("parser crashed for something else (logger, timestamp) ...")
      log.warning( repr(error_log) )

    time.sleep( int(cfg["SLEEP_TIME"]) )











