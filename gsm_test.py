from usim800.usim800 import sim800
import os
import json
import logging
import re
import pathlib

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
        try:
            self.gsm = sim800_slideshow(baudrate=115200, path="/dev/ttyUSB1")
            self.gsm.requests._APN = "internet"
            self.r = None
        except Exception as e:
            print("Wystąpił błąd przy próbie otwarcia portu GsmSlideshow - możliwe że inny program używa już podanego portu!")

    def download_file(self, nazwa, url, sleep_to_read_bytes):
        try:
            nazwa_pliku=nazwa
            file_bytes=self.gsm.requests.getFile(url, sleep_to_read_bytes)
            logging.debug("po pobraniu pliku")
            logging.debug(f"ahjo {file_bytes}")
            #self.r = self.gsm.requests
            #self.test_print()
            if os.path.isfile(nazwa_pliku):
                print("uwaga już był plik pobrany")
            else:
                f = open(nazwa_pliku, "wb")
            with open(nazwa_pliku, 'wb') as file:
                file.write(file_bytes)
        except Exception as e:
            print("Niestety jest błąd - wyrzuciło download_file w GsmSlideshow")
            print(f"{e}")
        logging.debug("koniec pliku")

    def test_print(self):
        print("statusCode:" + str(self.r.status_code))
        print("content:" + str(self.r.content))
        print("json:" + str(self.r.json()))
        print("IP:" + str(self.r.IP))


def parserIPNumber():
    bytes=b'AT+SAPBR=2,1\r\r\n+SAPBR: 1,1,"10.242.37.232"\r\n\r\nOK\r\n'
    print(bytes.split())
    answerWithIP = bytes.split()[2]
    print(answerWithIP)
    ip = answerWithIP.split("\"".encode())[1] #encode daje to samo co b"\""
    print(ip.decode())


def parserHTTPACTION():
    answerAT=b'AT+HTTPACTION=0\r\r\nOK\r\n\r\n+HTTPACTION: 0,200,2729\r\n'
    status=''
    numberOfBytes=''
    status_and_number=answerAT.split(b'+HTTPACTION: 0,')[1][0:-2]
    print(status_and_number)
    status=str(status_and_number.split(b',')[0])
    numberOfBytes=str(status_and_number.split(b',')[1])
    print(status)
    print(numberOfBytes)

def concatenate_list_data(list):
    result=b''
    for element in list:
        result += element
    return result

def parserPictureHTTPREAD():
    with open("widgetPiaseczno.png", "rb") as f:
        data=[]
        while True:
            byte = f.read(1)
            if not byte:
                break
            data.append(byte)
            if byte == b'\n':
                print(concatenate_list_data(data))
                data.clear()

if __name__ == "__main__":
    logging.root.setLevel(logging.DEBUG)
    #gsm_hami = GsmHami()
    #gsm_hami.download_config()

    gsm_slideshow = GsmSlideshow()
    gsm_slideshow.download_file("config.json", "http://134.122.69.201/config/kiosk/Lokalne_Kusy/gsm_test_config.json"
                                , sleep_to_read_bytes=2)
    gsm_slideshow.download_file("blank.png", "http://134.122.69.201/config/kiosk/Lokalne_Kusy/blank.png"
                                , sleep_to_read_bytes=1)
    gsm_slideshow.download_file("widgeturl.png", "http://imgurl.pl/img2/widgetkozienice_6065b42f78c5f.png"
                                , sleep_to_read_bytes=30)
    #gsm_slideshow.download_file("widgetserwer-ssl.png", "https://134.122.69.201/widgetKozienice/"
    #                            , sleep_to_read_bytes=30)
    gsm_slideshow.download_file("widgetserwer-bezssl.png", "http://134.122.69.201/widgetKozienice/"
                                , sleep_to_read_bytes=30)
    #parserIPNumber()
    #parserHTTPACTION()
    #parserPictureHTTPREAD()