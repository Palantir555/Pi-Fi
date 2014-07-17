Required 2 different architectures:

1 - Boot as an AP

    a. launch hostapd from rc.local.

    b. settings of the AP are in /etc/hostapd/hosapd.conf

    c. Start web server (run python+flask script)

    d. Need to use port 80, so we don't need to redirect traffic (tell the user: navigate to pi.local)

    e. in rc.local, we need an if(gpioPinX is HIGH): run the "be an AP" script.

2 - Connect to an existing wifi

    a. We need a file with the wifi settings (SSID, password, encryption...) in machine-readable format (json?) that will bo loaded to the /etc/wpa_supplicant/wpa_supplicant.conf

    b. From rc.local, if(gpioPinX is LOW): ifup wlan0

    c. Run some script (from rc.local?)
