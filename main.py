#! /usr/bin/env python
import sys
import json
import RPi.GPIO as gpio
import subprocess
from flask import Flask
from flask import request
from flask import render_template
from os import path

#Exit codes:
#  0 means "Be an access point"
#  1 means "Be a client"
#
#    if python script.py; then
#        echo "Starting client mode..."
#        ifup wlan0
#    else
#        echo "The script should have never exited on its own while in AP mode.
#        echo "Continuing with the login process..."
#    fi

script_dir  = path.dirname(__file__)
config_file = "config.json"
json_file_path = path.join(script_dir, config_file)
try:
    with open(json_file_path) as json_file:
        json_data = json.load(json_file)
except IOError as e:
    print "Exception raised trying to read the JSON file:\n\t%s" %(e)

### Script routines ###
def exit(exit_code):
    #gpio.cleanup()
    sys.exit(exit_code)

def gpio_init():
    # Use GPIO numbers not pin numbers
    GPIO.setmode(GPIO.BCM)
    # set up the GPIO channels - one input and one output
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)

### JSON ###
def get_boot_mode():
    global json_data
    return json_data["boot_mode"]

def read_config_file():
    '''not sure what it's gonna do yet. Ignore returns and exits ATM'''
    global json_data
    if json_data["boot_mode"] == "AP":
        ap_file         = json_data["AP"]["file"]
        ap_ssid         = json_data["AP"]["ssid"]
        country_code    = json_data["AP"]["country_code"]
        driver          = json_data["AP"]["driver"]
        hw_mode         = json_data["AP"]["hw_mode"]
        channel         = json_data["AP"]["channel"]
        wpa             = json_data["AP"]["wpa"]
        wpa_passphrase  = json_data["AP"]["wpa_passphrase"]
        wpa_key_mgmt    = json_data["AP"]["wpa_key_mgmt"]
        return 1
    else:
        exit(0) #we are supposed to run as a client, so exit this script.

def save_json_file():
    '''Save the modified json values to its original file.'''
    global json_file_path
    global json_data
    try:
        with open(json_file_path, "r+") as json_file:
            #rewind to beginning of file:
            json_file.seek(0)  
            #write the updated version:
            json_file.write(json.dumps(json_data,indent=4)) 
            #truncate the remainder of the data in the file:
            json_file.truncate() 
    except IOError as e:
        print "Exception raised trying to mod JSON file in save_json_file: "
        print e

### misc ###
def configure_boot(boot_mode, ssid, password, channel, encryption):
    global json_data
    json_data["boot_mode"] = boot_mode
    if boot_mode == "AP":
        json_data["AP"]["ssid"] = ssid
        json_data["AP"]["wpa_passphrase"] = password
        json_data["AP"]["channel"] = channel
        if encryption == "WPA2-PSK":
            json_data["AP"]["wpa"] = 2
            json_data["AP"]["wpa_key_mgmt"] = "WPA-PSK"
        elif encryption == "WPA-PSK":
            json_data["AP"]["wpa"] = 1
            json_data["AP"]["wpa_key_mgmt"] = "WPA-PSK"

    elif boot_mode == "CLIENT":
        json_data["CLIENT"]["ssid"] = ssid
        json_data["CLIENT"]["psk"] = password
        json_data["CLIENT"]["channel"] = channel
        if encryption == "WPA2-PSK":
            json_data["CLIENT"]["key_mgmt"] = "WPA2-PSK"
            json_data["CLIENT"]["proto"] = "WPA2"
        elif encryption == "WPA-PSK":
            json_data["CLIENT"]["key_mgmt"] = "WPA-PSK"
            json_data["CLIENT"]["proto"] = "WPA"
    save_json_file()

def generate_client_file():
    '''those subprocess.call are not clean. Should be changed'''
    global json_data
    script_dir  = path.dirname(__file__)
    config_file_name = "wpa_supplicant.conf"
    config_file_path = path.join(script_dir, config_file_name)
    subprocess.call(["rm -f", config_file_path], shell=True)
    subprocess.call(["touch", config_file_path], shell=True)

    try:
        with open(config_file_name, 'w+') as f:
            f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n")
            f.write("update_config=1\n\n")
            f.write("network={\n")
            ssid_line = '    ssid="%s"\n' %(json_data["CLIENT"]["psk"])
            f.write(ssid_line)
            psk_line = '    psk="%s"\n' %(json_data["CLIENT"]["psk"])
            f.write(psk_line)
            keymgmt_line = '    key_mgmt="%s"\n' %(json_data["CLIENT"]["key_mgmt"])
            f.write(keymgmt_line)
            channel_line = '    channel=%s\n' %(json_data["CLIENT"]["channel"])
            f.write(channel_line)
            f.write("}")
            f.close()
            return 1

    except Exception, e:
        print e
        return 0

def generate_ap_file():
    '''those subprocess.call are not clean. Should be changed'''
    global json_data
    script_dir  = path.dirname(__file__)
    config_file_name = "hostapd.conf"
    config_file_path = path.join(script_dir, config_file_name)
    subprocess.call(["rm -f", config_file_path], shell=True)
    subprocess.call(["touch", config_file_path], shell=True)

    try:
        with open(config_file_name, 'w+') as f:
            f.write("interface=wlan0\n")
            f.write("driver=nl80211\n")
            f.write("country_code=UK\n")
            ssid_line = 'ssid="%s"\n' %(json_data["AP"]["ssid"])
            f.write(ssid_line)
            hwmode_line = 'hw_mode="%s"\n' %(json_data["AP"]["hw_mode"])
            f.write(hwmode_line)
            channel_line = 'channel="%s"\n' %(json_data["AP"]["channel"])
            f.write(channel_line)
            wpa_line = 'wpa="%s" wpa_passphrase="%s"\n' %(json_data["AP"]["wpa"], json_data["AP"]["wpa_passphrase"])
            f.write(wpa_line)
            wpakeymgmt_line = 'wpa_key_mgmt="%s"' %(json_data["AP"]["wpa_key_mgmt"])
            f.write(wpakeymgmt_line)
            f.close()
            return 1

    except Exception, e:
        print e
        return 0

def move_client_file():
    '''that subprocess.call is not clean. Should be changed'''
    global json_data
    script_dir  = path.dirname(__file__)
    config_file_name = "wpa_supplicant.conf"
    config_file_path = path.join(script_dir, config_file_name)
    config_file_destination_path = json_data["CLIENT"]["file"]
    subprocess.call(["mv", config_file_path, config_file_destination_path], shell=True)

def move_ap_file():
    '''that subprocess.call is not clean. Should be changed'''
    global json_data
    script_dir  = path.dirname(__file__)
    config_file_name = "hostapd.conf"
    config_file_path = path.join(script_dir, config_file_name)
    config_file_destination_path = json_data["AP"]["file"]
    subprocess.call(["mv", config_file_path, config_file_destination_path], shell=True)

### Flask ###
app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template("index.html")

@app.route('/connect_to_ap.asp', methods=['POST'])
def my_form_post():
    ssid        = request.form['ssid']
    passphrase  = request.form['password']
    channel     = request.form['channel']
    encryption  = request.form['encryption']

    checkBoxVal = 0
    try:
        checkBox    = request.form['boot_mode']
        boot_mode   = "CLIENT"
    except Exception, e:
        boot_mode   = "AP"

    configure_boot(boot_mode, ssid, passphrase, channel, encryption)
    print "The wifi SSID selected is: %s" %(ap_ssid)
    print "The wifi Pass selected is: %s" %(passphrase)
    print "On restart, boot as: %s" %(boot_mode)
    return "Success!"

### main ###
if __name__ == '__main__':
    # input from GPIO7
    gpio_input_val = GPIO.input(7)
    if (gpio_input_val == GPIO.LOW) or (get_boot_mode == "CLIENT"):
        #If jumper not set AND "CLIENT" defined in config.json
        #Start CLIENT mode
        exit(1)

    else:
        #Jumper is set
        # or
        #we have defined AP in software (config.json)
        app.run(port=80, debug=True)
    #That else should never return
