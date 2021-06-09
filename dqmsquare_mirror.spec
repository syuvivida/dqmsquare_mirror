Name:       dqmsquare_mirror
Version:    1.0.2
Release:    1
Summary:    DQM^2 grabber/parser/server
License:    GPL
Prefix:     /opt/dqmsquare_mirror

%description
https://github.com/pmandrik/dqmsquare_mirror

%prep
%build
mkdir -p $RPM_BUILD_ROOT/opt/dqmsquare_mirror
mkdir -p $RPM_BUILD_ROOT/opt/dqmsquare_mirror/log
mkdir -p $RPM_BUILD_ROOT/opt/dqmsquare_mirror/tmp

cp -r ../SOURCES/static $RPM_BUILD_ROOT/opt/dqmsquare_mirror/static
cp -r ../SOURCES/bottle $RPM_BUILD_ROOT/opt/dqmsquare_mirror/bottle
cp -r ../SOURCES/geckodriver $RPM_BUILD_ROOT/opt/dqmsquare_mirror/geckodriver

cp ../SOURCES/*.py $RPM_BUILD_ROOT/opt/dqmsquare_mirror/.
cp ../SOURCES/dqmsquare_parser $RPM_BUILD_ROOT/opt/dqmsquare_mirror/.
cp ../SOURCES/dqmsquare_robber $RPM_BUILD_ROOT/opt/dqmsquare_mirror/.

mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system

cp ../SOURCES/services/dqmsquare_mirror_wrapper.sh $RPM_BUILD_ROOT/usr/bin/.
cp ../SOURCES/services/dqmsquare_mirror@.service   $RPM_BUILD_ROOT/etc/systemd/system/.

%install
%files
/opt/dqmsquare_mirror
/usr/bin/dqmsquare_mirror_wrapper.sh
/etc/systemd/system/dqmsquare_mirror@.service

%post
sed -i "s%__PDQM__%"$RPM_INSTALL_PREFIX"%g" /usr/bin/dqmsquare_mirror_wrapper.sh
echo "Install to \""$RPM_INSTALL_PREFIX"\""
echo "Done!"
echo "Start it with: \n systemctl start dqmsquare_mirror@robber.service dqmsquare_mirror@parser.service dqmsquare_mirror@server.service"



