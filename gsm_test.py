from usim800.usim800 import sim800
import os
import json
import logging

class GsmHami:
    def __init__(self):
       self.gsm = sim800(baudrate=9600, path="/dev/ttyUSB0")
       self.gsm.requests._APN = "internet"
       self.r = None

    def test_print(self):
        print("statusCode:"+str(self.r.status_code))
        print("content:"+str(self.r.content))
        print("json:"+str(self.r.json()))
        print("IP:"+str(self.r.IP))

    def download_config(self):
        nazwa_configa="config.json"
        self.gsm.requests.getFile(url="http://134.122.69.201/config/kiosk/Lokalne_Kusy/gsm_test_config.json")
        self.r = self.gsm.requests
        self.test_print()
        if os.path.isfile(nazwa_configa):
          print("juz byl config, zostanie zastapiony")
        else:
            f=open(nazwa_configa, "w+")
        with open(nazwa_configa, 'wb') as file_json:
            file_json.write(self.r.content)
        print("koniec downloadConfig funkcji")

    def download_picture(self):
        nazwa_obrazka="widget.png"
        self.gsm.requests.getFile(url="https://134.122.69.201/widgetKozienice/")
        self.r = self.gsm.requests
        self.test_print()
        if os.path.isfile(nazwa_obrazka):
           print("już był "+nazwa_obrazka+"zostanie zastąpiony")
        else:
            f=open(nazwa_obrazka, "w+")
        with open(nazwa_obrazka, "wb") as widgetpng:
            widgetpng.write(self.r.content)
        print("koniec downloadPicture funkcji")

    def send_sms(self):
        numer_docelowy="+48532819627"
        self.gsm.sms.send(numer_docelowy, "Helena, mam zawał")
        print("koniec sms funkcji: "+numer_docelowy)

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    gsm_hami = GsmHami()
    #gsm_hami.download_config()
    gsm_hami.download_picture()
    #gsm_hami.send_sms()
