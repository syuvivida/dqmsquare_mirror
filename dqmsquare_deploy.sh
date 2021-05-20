#!/bin/bash
# P.S.~Mandrik, IHEP, https://github.com/pmandrik

sfolder=`pwd`
tmp_folder=`pwd`/tmp
build_folder=`pwd`/build

mkdir -p $tmp_folder
mkdir -p $build_folder

### DOWNLOAD IF UNEXIST ###
# bottle
cd $sfolder
if [ ! -d "bottle" ] ; then
  mkdir -p "bottle"; cd "bottle"
  wget https://github.com/bottlepy/bottle/archive/refs/tags/0.12.19.tar.gz .
  tar -xvzf 0.12.19.tar.gz
  cp bottle-0.12.19/bottle.py .
fi

# geckodriver
cd $sfolder
if [ ! -d "geckodriver" ] ; then
  mkdir -p "geckodriver"; cd "geckodriver"
  wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz .
  tar -xvzf geckodriver-v0.29.1-linux64.tar.gz
fi

### BUILD ###
cd $sfolder
cp dqmsquare_robber.py $build_folder/.
cp dqmsquare_parser.py $build_folder/.
cp dqmsquare_cfg.py    $build_folder/.
cd $build_folder

python -m PyInstaller --onefile --hidden-import=dqmsquare_cfg dqmsquare_robber.py
python -m PyInstaller --onefile --hidden-import=dqmsquare_cfg dqmsquare_parser.py

cp dist/dqmsquare_robber $sfolder/.
cp dist/dqmsquare_parser $sfolder/.



 
