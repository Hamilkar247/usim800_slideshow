import traceback

from usim800.usim800 import sim800
import os
import logging

from usim800.usim800_slideshow import sim800_slideshow


class GsmSlideshow:
    def __init__(self, path):
        try:
            self.gsm = sim800_slideshow(baudrate=115200, path=path)
            self.gsm.requests._APN = "internet"
            self.r = None
        except Exception as e:
            print("Wystąpił błąd przy próbie otwarcia portu GsmSlideshow - możliwe że inny program używa już podanego portu!")
            traceback.print_exc()

    def download_file(self, nazwa, url, sleep_to_read_bytes):
        try:
            nazwa_pliku=nazwa
            self.gsm.requests.getFile(url, sleep_to_read_bytes, nazwa_pliku)
        except Exception as e:
            print("Niestety jest błąd - wyrzuciło download_file w GsmSlideshow")
            print(f"{e}")
        logging.debug("koniec pliku")


def gsm_config(gsm_slideshow):
    gsm_slideshow.download_file("config.json", "http://134.122.69.201/config/kiosk/Lokalne_Kusy/gsm_test_config.json"
                                , sleep_to_read_bytes=2)


def gsm_kozienice(gsm_slideshow):
    gsm_slideshow.download_file("kozienice_map.png", "https://134.122.69.201/config/kiosk/Lokalne_Kusy/kozienice_map.png"
                                , sleep_to_read_bytes=40)


def gsm_blank(gsm_slideshow):
    gsm_slideshow.download_file("blank.png", "http://134.122.69.201/config/kiosk/Lokalne_Kusy/blank.png"
                                , sleep_to_read_bytes=1)


def gsm_widgetimgurl(gsm_slideshow):
    gsm_slideshow.download_file("pobraneimgurl.png", "http://imgurl.pl/img2/widgetkozienice_6065b42f78c5f.png"
                                , sleep_to_read_bytes=30)


def gsm_widgetserwer_ssl(gsm_slideshow):
    gsm_slideshow.download_file("widgetserwer-ssl.png", "https://134.122.69.201/widgetKozienice/"
                                , sleep_to_read_bytes=30)


def gsm_widgetserwer_bezssl(gsm_slideshow):
    gsm_slideshow.download_file("widgetserwer-bezssl.png", "http://134.122.69.201/widgetKozienice/"
                                , sleep_to_read_bytes=30)


if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    gsm_slideshow = GsmSlideshow(path="/dev/ttyUSB0")
    #gsm_config(gsm_slideshow)
    #gsm_blank(gsm_slideshow)
    #gsm_widgetimgurl(gsm_slideshow)
    gsm_widgetserwer_bezssl(gsm_slideshow)
    #gsm_kozienice(gsm_slideshow

