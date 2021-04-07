from usim800.usim800 import sim800
import os
import json
import logging

from usim800.usim800_slideshow import sim800_slideshow


class GsmHami:
    def __init__(self):
        self.gsm = sim800(baudrate=115200, path="/dev/ttyUSB0")
        self.gsm.requests._APN = "internet"
        self.r = None

    def test_print(self):
        print("statusCode:" + str(self.r.status_code))
        print("content:" + str(self.r.content))
        print("json:" + str(self.r.json()))
        print("IP:" + str(self.r.IP))

    def download_config(self):
        nazwa_configa = "config.json"
        self.gsm.requests.getConfig(url="http://134.122.69.201/config/kiosk/Lokalne_Kusy/gsm_test_config.json")
        self.r = self.gsm.requests
        self.test_print()
        if os.path.isfile(nazwa_configa):
            print("juz byl config, zostanie zastapiony")
        else:
            f = open(nazwa_configa, "w+")
        with open(nazwa_configa, 'wb') as file_json:
            file_json.write(self.r.content)
        print("koniec downloadConfig funkcji")

    def download_picture(self):
        nazwa_obrazka = "widget.png"
        self.gsm.requests.getFile(url="http://imgurl.pl/img2/widgetkozienice_6065b42f78c5f.png")
        self.r = self.gsm.requests
        self.test_print()
        if os.path.isfile(nazwa_obrazka):
            print("już był " + nazwa_obrazka + "zostanie zastąpiony")
        else:
            f = open(nazwa_obrazka, "w+b")
        with open(nazwa_obrazka, "wb") as widgetpng:
            widgetpng.write(self.r.content)
        print("koniec downloadPicture funkcji")

    def send_sms(self):
        numer_docelowy = "+48532819627"
        self.gsm.sms.send(numer_docelowy, "Helena, mam zawał")
        print("koniec sms funkcji: " + numer_docelowy)


class GsmSlideshow:
    def __init__(self):
        self.gsm = sim800_slideshow(baudrate=115200, path="/dev/ttyUSB0")
        self.gsm.requests._APN = "internet"
        self.r = None

    def download_file(self):
        try:
            nazwa_plika="config.json"
            self.gsm.requests.getFile(url="http://134.122.69.201/config/kiosk/Lokalne_Kusy/gsm_test_config.json")
            self.r = self.gsm.requests
            self.test_print()
            if os.path.isfile(nazwa_plika):
                print("uwaga już był plik pobrany")
            else:
                f = open(nazwa_plika, "w+")
            with open(nazwa_plika, 'wb') as file:
                file.write(self.r.content)
        except:
            print("Niestety jest błąd - wyrzuciło download_file w GsmSlideshow")
        logging.debug("koniec pliku")

    def test_print(self):
        print("statusCode:" + str(self.r.status_code))
        print("content:" + str(self.r.content))
        print("json:" + str(self.r.json()))
        print("IP:" + str(self.r.IP))


if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    #gsm_hami = GsmHami()
    #gsm_hami.download_config()

    gsm_slideshow = GsmSlideshow()
    gsm_slideshow.download_file()
