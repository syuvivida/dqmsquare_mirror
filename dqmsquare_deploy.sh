#!/bin/bash
# P.S.~Mandrik, IHEP, https://github.com/pmandrik

sfolder=`pwd`
tmp_folder=`pwd`/tmp
log_folder=`pwd`/log
build_folder=`pwd`/build

mkdir -p $tmp_folder
mkdir -p $log_folder
mkdir -p $build_folder

### DOWNLOAD IF UNEXIST ###
echo "dqmsquare_deploy.sh: DOWNLOAD ..."
# bottle
cd $sfolder
echo "dqmsquare_deploy.sh: check bottle ..."
if [ ! -d "bottle" ] ; then
  echo "dqmsquare_deploy.sh: install bottle ..."
  mkdir -p "bottle"; cd "bottle"
  wget https://github.com/bottlepy/bottle/archive/refs/tags/0.12.19.tar.gz .
  tar -xvzf 0.12.19.tar.gz
  cp bottle-0.12.19/bottle.py .
else 
  echo "dqmsquare_deploy.sh: skip bottle ..."
fi

# geckodriver
cd $sfolder
echo "dqmsquare_deploy.sh: check geckodriver ..."
if [ ! -d "geckodriver" ] ; then
  echo "dqmsquare_deploy.sh: install geckodriver ..."
  mkdir -p "geckodriver"; cd "geckodriver"
  wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz .
  tar -xvzf geckodriver-v0.29.1-linux64.tar.gz
else 
  echo "dqmsquare_deploy.sh: skip geckodriver ..."
fi

### BUILD ###
if [ $1 == "build" ] ; then
  echo "dqmsquare_deploy.sh: BUILD ..."
  cd $sfolder
  cp dqmsquare_robber_oldruns.py $build_folder/.
  cp dqmsquare_robber.py $build_folder/.
  cp dqmsquare_parser.py $build_folder/.
  cp dqmsquare_cfg.py    $build_folder/.
  cd $build_folder

  python -m PyInstaller --onefile --hidden-import=dqmsquare_cfg dqmsquare_robber.py
  python -m PyInstaller --onefile --hidden-import=dqmsquare_cfg dqmsquare_robber_oldruns.py
  python -m PyInstaller --onefile --hidden-import=dqmsquare_cfg dqmsquare_parser.py

  cp dist/dqmsquare_robber $sfolder/.
  cp dist/dqmsquare_robber_oldruns $sfolder/.
  cp dist/dqmsquare_parser $sfolder/.
fi

# create def cfg
cd $sfolder
python dqmsquare_cfg.py

# pack into rpm
echo "dqmsquare_deploy.sh: RPM ..." "s/__PDQM__/"$RPM_INSTALL_PREFIX"/g"
mkdir -p $sfolder/RPMBUILD/{RPMS/{noarch},SPECS,BUILD,SOURCES,SRPMS}

cp -r $sfolder/static $sfolder/RPMBUILD/SOURCES/.
cp -r $sfolder/bottle $sfolder/RPMBUILD/SOURCES/.
cp -r $sfolder/geckodriver $sfolder/RPMBUILD/SOURCES/.
cp -r $sfolder/services $sfolder/RPMBUILD/SOURCES/.

cp $sfolder/*.py $sfolder/RPMBUILD/SOURCES/.
cp $sfolder/dqmsquare_parser $sfolder/RPMBUILD/SOURCES/.
cp $sfolder/dqmsquare_robber $sfolder/RPMBUILD/SOURCES/.
cp $sfolder/dqmsquare_robber_oldruns $sfolder/RPMBUILD/SOURCES/.

rpmbuild --define "_topdir "$sfolder"/RPMBUILD" -bb dqmsquare_mirror.spec

cp $sfolder/RPMBUILD/RPMS/x86_64/* .







