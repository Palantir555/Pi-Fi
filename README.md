Required 2 different architectures:

1 - Boot as an AP
    a. launch hostapd from rc.local.
    b. settings of the AP are in /etc/hostapd/hosapd.conf

    c. Start web server (run python+flask script)
    d. Need to use port 80, so we don't need to redirect traffic (tell the user: navigate to pi.local)

    e. in rc.local, we need a if(gpioPinX is HIGH): run the "be an AP" script.

2 - Connect to an existing wifi
    a. We need a file with the wifi settings (SSID, password, encryption...) in machine-readable format (json?) that will bo loaded to the /etc/wpa_supplicant/wpa_supplicant.conf
    b. From rc.local, if(gpioPinX is LOW): ifup wlan0
    c. Run some script (from rc.local?)





config file:
{
    "boot_mode":"AP",
    "AP":
    [
        {
            "file":"/etc/hostapd/hostapd.conf",
            "ssid":"RaspberryPint",
            "country_code":"UK",
            "driver":"nl80211",
            "hw_mode":"g",
            "channel":6,
            "wpa":2,
            "wpa_passphrase":"raspberry",
            "wpa_key_mgmt":"WPA-PSK"
        }
    ],
    "CLIENT":
    [
        {
            "file":"/etc/wpa_supplicant/wpa_supplicant.conf",
            "ssid":"MyHomeRouter",
            "key_mgmt":"WPA-PSK",
            "proto":"WPA2",
            "psk":"MySuperSecurePassword!"
        }
    ]
}
