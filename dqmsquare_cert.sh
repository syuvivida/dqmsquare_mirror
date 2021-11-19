set -x

tar -xf other/vm352ut3.default-default.tar.xz
mv vm352ut3.default-default /firefox_profile_path

openssl pkcs12 -export -out Cert.p12 -in /etc/robots/robotcert.pem -inkey /etc/robots/robotkey.pem -passin pass:changeme -passout pass:changeme
mkdir /db999
certutil -N --empty-password -d sql:/db999
pk12util -i Cert.p12 -d sql:/db999 -W changeme
cp /db999/* /firefox_profile_path/.

chmod 777 /firefox_profile_path
find /firefox_profile_path -type d -exec chmod 777 {} \; 
find /firefox_profile_path -type f -exec chmod 777 {} \;
