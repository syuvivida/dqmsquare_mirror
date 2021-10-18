import time
from os import listdir
from os.path import isfile, join
import sys

folder = "./tmp/"
try:
  folder = str(sys.argv[1])
except: pass

print "Output:", folder

N_file = 0
while True:
  files = [f for f in listdir(folder) if isfile(join(folder, f))]
  if len(files) > 10:
    time.sleep(10)
    continue
  print "Iter # ", N_file
  f = open( folder + "test" + str(N_file) + ".txt" , "w")
  f.write('This is a test # ' + str(N_file) + '\n')
  N_file += 1;
  f.close()
  time.sleep(10)
