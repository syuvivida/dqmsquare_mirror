import time
from os import listdir, remove
from os.path import isfile, join

folder = "./tmp/"

N_file = 0
while True:
  files = [f for f in listdir(folder) if isfile(join(folder, f))]
  if len(files) == 0:
    time.sleep(10)
    continue
  f = open( join(folder, files[0]), "r")
  line = f.readline()
  f.close()
  print line
  remove( join(folder, files[0]) )
  time.sleep(10) 
