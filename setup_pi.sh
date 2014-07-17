#!/usr/bin/env bash

#We are assuming the user is running this on Raspbian Wheezy.
#The (advanced) user should decide whether or no they want to expand the filesystem,
#language config, etc. using raspi-config.

if [ "$(whoami)" != "root" ]; then
    echo "You need to be root to run this script. Try using sudo."
    exit 1
fi

#Update apt
apt-get -y update
apt-get -y upgrade
apt-get -y dist-upgrade

#Clean the home folder
rm -rf /home/pi/python_games
rm     /home/pi/*.png

#Source: http://www.linuxuser.co.uk/tutorials/set-up-a-wireless-access-point-with-a-raspberry-pi
#hostapd - access point management and authentication
#bridge-utils - bridge Ethernet and WiFi interfaces
#iw - info about the wireless interface
#dnsmasq - dchp server
apt-get -y install hostapd bridge-utils iw dnsmasq
apt-get -y install python-pip

#Install the python web framework we are going to use: flask
pip install flask

#In hostapd.conf:
HOSTAPD_CONF=/etc/hostapd/hostaped.conf
echo "interface=wlan0"                  >> $HOSTAPD_CONF
#echo "bridge=br0"                       >> $HOSTAPD_CONF #no ethernet-wifi bridge
echo "driver=nl80211"                   >> $HOSTAPD_CONF
echo "country_code=UK"                  >> $HOSTAPD_CONF
echo "ssid=RaspberryPint"               >> $HOSTAPD_CONF
echo "hw_mode=g"                        >> $HOSTAPD_CONF
echo "channel=6"                        >> $HOSTAPD_CONF
echo "wpa=2 wpa_passphrase=raspberry"   >> $HOSTAPD_CONF
echo "wpa_key_mgmt=WPA-PSK"             >> $HOSTAPD_CONF
#</hostapd.conf>
#I think this will cause hostapd to start on boot. We don't want that, we want to run
#from rc.local only -> `if(gpio.pin==HIGH) sudo /etc/init.d/hostapd start`
#sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/g'  /etc/default/hostapd

#Set the screen settings, in case the user wants to use a display.
DISP_FILE=/boot/config.txt
echo "disable_overscan=1"           >> $DISP_FILE
echo "framebuffer_width=1900"       >> $DISP_FILE
echo "framebuffer_height=1080"      >> $DISP_FILE
echo "framebuffer_depth=32"         >> $DISP_FILE
echo "framebuffer_ignore_alpha=1"   >> $DISP_FILE
echo "hdmi_pixel_encoding=1"        >> $DISP_FILE
echo "hdmi_group=2"                 >> $DISP_FILE

#Install git and svn
apt-get -y install git
apt-get -y install subversion

#Install/update pip and othe python dev tools
apt-get -y install python-dev build-essential
wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py -O - | python
easy_install pip
pip install -U pip

#Install RPi.GPIO library
wget --no-check-certificate "https://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.5.5.tar.gz"
tar zxf "RPi.GPIO-0.5.5.tar.gz"
cd "RPi.GPIO-0.5.5"
python setup.py install
cd ..
rm -rf "RPi.GPIO-0.5.5"
rm "RPi.GPIO-0.5.5.tar.gz"

#Set the hostname `pi`, in case the default is different.
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
echo pi > /etc/hostname
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\pi/g" /etc/hosts
hostname verdeva

#Install avahi-daemon, so you can 'ssh pi@pi.local'
apt-get -y install avahi-daemon

#Ping to google once/min in order to prevent the wifi interface from sleeping.
CRON_TMP_FILE=/tmp/cron_tmp
crontab -l > $CRON_TMP_FILE
echo "*/1 * * * * ping -c 1 8.8.8.8" >> $CRON_TMP_FILE
crontab $CRON_TMP_FILE
rm $CRON_TMP_FILE

#Define the wifi to automatically connect to: SSID=verdeva and PASSWD=xively_demo! (WPA2 PSK)
WIFI_FILE=/etc/wpa_supplicant/wpa_supplicant.conf
echo 'network={'                    >> $WIFI_FILE
echo '        ssid="verdeva"'       >> $WIFI_FILE
echo '        scan_ssid=1'          >> $WIFI_FILE
echo '        key_mgmt=WPA-PSK'     >> $WIFI_FILE
echo '        proto=WPA2'           >> $WIFI_FILE
echo '        psk="xively_demo!"'   >> $WIFI_FILE
echo '}'                            >> $WIFI_FILE

#Modify /etc/rc.local
RCLOCAL=/etc/rc.local
sed -i 's/exit 0//' $RCLOCAL
#Careful with this git pull on boot! Remove the line if you don't want it.
echo 'git pull https://github.com/Palantir555/Pi-Fi.git'        >> $RCLOCAL
echo 'if python script.py; then'                                >> $RCLOCAL
echo '    echo "- Starting client mode..."'                     >> $RCLOCAL
echo '    ifup wlan0'                                           >> $RCLOCAL
echo 'else'                                                     >> $RCLOCAL
echo '    echo "- The script should have never exited on its'   >> $RCLOCAL
echo '    echo "  own while in AP mode."'                       >> $RCLOCAL
echo '    echo "- Continuing with the login process..."'        >> $RCLOCAL
echo 'fi'                                                       >> $RCLOCAL
#Finished modifying /etc/rc.local
echo 'exit 0' >> $RCLOCAL
