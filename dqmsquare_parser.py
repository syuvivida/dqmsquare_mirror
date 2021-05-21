# P.S.~Mandrik, IHEP, https://github.com/pmandrik

import dqmsquare_cfg
from bs4 import BeautifulSoup
import random, time, os
from datetime import datetime

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

    self.colors = {"G" : "#52BE80", "R" : "#EC7063", "Y" : "#F4D03F" }
    

  def AddServer(self, name, state):
    d = {"name" : self.GetServerName(name), "state" : state}
    d["state_attr"] = 'style="background-color:' + self.colors["Y"] + '"'
    if "live" in state : d["state_attr"] = 'style="background-color:' + self.colors["G"] + '"'
    if "closed" in state : d["state_attr"] = 'style="background-color:' + self.colors["R"] + '"'
    self.servers += [ d ]

  def GetServerName(self, name):
    txt = name.split("-")
    return txt[0] + "-...-" + txt[-1].split(".")[0]

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
    self.jobs[-1][-1] = "->"

    i = len(self.jobs)-1
    if cfg["SERVER_LOCAL"] :  
      link = os.path.splitext( self.output_file )[0] + "_jlog" + str(i) + ".log"
    else : 
      link = "/dqm/dqm-square/" + os.path.splitext( self.output_file )[0] + "_jlog" + str(i) + ".log"

    self.jobs[-1][-1] = '<a href="'+link+'" target="_blank"> -> </a>'

    pass

  def Dump(self):
    content = '<p style="clear:both;margin-bottom:5px"></p>'

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
    content += 'Run: <strong>' + str(self.run_number) + '</strong> &nbsp;&nbsp;&nbsp;&nbsp;'
    content += 'Legend: '
    content += '<strong><span style="background-color:' + self.colors["G"] + '"> &nbsp;&nbsp; running ' + str(len([attr for attr in self.jobs_attr if self.colors["G"] in attr['row_attr']])) + ' &nbsp;&nbsp; </span></strong>'
    content += '<strong><span style="background-color:' + self.colors["Y"] + '"> &nbsp;&nbsp; stopped ' + str(len([attr for attr in self.jobs_attr if self.colors["Y"] in attr['row_attr']])) + ' &nbsp;&nbsp; </span></strong>'
    content += '<strong><span style="background-color:' + self.colors["R"] + '"> &nbsp;&nbsp; crashed ' + str(len([attr for attr in self.jobs_attr if self.colors["R"] in attr['row_attr']])) + '&nbsp;&nbsp; </span></strong>'
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
        content += '<td class="job_table_cell">' + col + "<td> "
      content += "</td>\n"
    content += "</table>\n"

    ### images if exist
    if self.input_file : 
      dir_name = os.path.dirname(self.input_file)
      fname    = os.path.basename(self.input_file)
      for item in os.listdir( dir_name ) : 
        if not item.endswith(".png") : continue
        if fname not in item : continue
        content += "<img src=" + os.path.join(dir_name, item) + ">\n"

    ### write out
    if self.output_file : 
      file = open(self.output_file,"w")
      file.write( content )
      file.close()

      ### logs
      for i, jlog in enumerate(self.jobs_logs) :
        oname = os.path.splitext( self.output_file )[0] + "_jlog" + str(i) + ".log"
        file = open(oname,"w")
        file.write( jlog )
        file.close()

    else : print content

if __name__ == '__main__':
  NAME = "dqmsquare_parser.py:"
  cfg  = dqmsquare_cfg.load_cfg( 'dqmsquare_mirror.cfg' )
  print cfg

  ipaths = cfg["PARSER_INPUT_PATHS"].split(",")
  opaths = cfg["PARSER_OUTPUT_PATHS"].split(",")
  N_targets = len(ipaths)
  if len(ipaths) != len(opaths) :
    print( NAME, "len(PARSER_INPUT_PATHS) != len(PARSER_OUTPUT_PATHS)", len(ipaths), len(opaths), "; exit" )
    exit()

  def load_html(path):
    try:
      ifile = open( path ,"r" )
      html_doc = ifile.read( )
      ifile.close()
      return html_doc
    except:
      return ""
    
  def parse_dqmsquare_page( input_page, output_page ):
    html_doc = load_html( input_page )
    if not html_doc :
      print( NAME, "waiting for the input file", input_page )
      continue

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
        if bool(cfg["PARSER_DEBUG"]) : print NAME, "add server", name, state 
        dqm_data.AddServer( name, state )
      except : pass

    ### get Run number ...
    run_number = "-"
    breadcrumbs = soup.find_all("ol", {"class": "breadcrumb"}  )
    for bread in breadcrumbs:
      has_text = bread.find_all("span", string="Known cmssw jobs")
      if len(has_text) : 
        spans = bread.find_all('strong', {"class": "ng-binding"} )
        print spans, spans[0].text
        if len(spans) : run_number = spans[0].text
        break
    dqm_data.run_number = run_number

    ### get jobs states ...
    for table in soup.find_all( 'tbody' ):
      if table.attrs : continue

      # table_body = table.find('tbody')
      rows = table.find_all('tr')
      data = []
      for row_index, row in enumerate(rows):
        # print len(dqm_data.jobs), row_index, "ROW\n\n\n"
        if row.has_attr("ng-if") :
          if row["ng-if"] != "_show_inline == 'log'" : continue
          logs_parts = row.find_all('dqm-log')
          if not logs_parts : continue
          logs = "\n ... \n".join( [ ele.text.strip() for ele in logs_parts ] )
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

        if bool(cfg["PARSER_DEBUG"]) : print NAME, "add job", dtime, ltime, sname, state, tag, lumi, rss, nevents
        if bool(cfg["PARSER_RANDOM"]) : ltime = str( random.randint(0, 100) )
        dqm_data.AddJob(dtime, ltime, sname, state, tag, lumi, rss, nevents, logs )

    dqm_data.Dump()

  while True:
    ### targets old runs ...
    for i in xrange(N_targets):
      for 

    ### targets ...
    for i in xrange(N_targets):
      dqm_data = parse_dqmsquare_page( ipaths[i], opaths[i] )

    time.sleep( int(cfg["SLEEP_TIME"]) )










