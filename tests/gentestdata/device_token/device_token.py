import hashlib
import base64


def generate_wifi_token(wifi_ssid, wifi_psk):
    h = hashlib.sha256()
    h.update(wifi_ssid.encode('utf-8'))
    h.update(wifi_psk.encode('utf-8'))
    return base64.urlsafe_b64encode(h.digest()).decode('ascii').strip("=")


def generate_secure_token(key, baseless_url):
    h = hashlib.sha256()
    h.update(key.encode('ascii'))
    h.update(baseless_url.encode('ascii'))
    return base64.urlsafe_b64encode(h.digest()).decode('ascii').strip("=")
