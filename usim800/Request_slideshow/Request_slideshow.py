import os
import re
import traceback

from gpiozero import LED

from usim800_slideshow.usim800.Communicate_slideshow import communicate_slideshow
import logging
import time


class request_slideshow(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status_code = None
        self._numberOfBytes = None
        self._sleep_to_read_bytes = None
        self._nameOfFile = None
        self._extensionFile = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None
        self._png_startFile=b'\x89PNG\r\n'
        self._startFileLine=b''

    def init(self):
        self._status_code = None
        self._numberOfBytes = None
        self._sleep_to_read_bytes = None
        self._nameOfFile = None
        self._extensionFile = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None
        self._png_startFile=b'\x89PNG\r\n'
        self._json_startFile=b'{\n'
        self._startFileLine=b''

    @property
    def text(self):
        return self._text

    @property
    def IP(self):
        return self._IP

    @property
    def APN(self):
        return self._APN

    @APN.setter
    def APN(self, APN):
        self._APN = APN

    @property
    def url(self):
        return self._url

    @property
    def content(self):
        return self._content

    @property
    def status_code(self):
        return self._status_code

    @property
    def numberOfBytes(self):
        return self._numberOfBytes

    @property
    def nameOfFile(self):
        return self._nameOfFile

    @property
    def extension(self):
        return self._extensionFile

    @property
    def startFileLine(self):
        return  self._startFileLine

    def set_reset_pin(self, reset_pin):
        self._reset_pin = reset_pin

    def reset_sim800(self):
        if self._reset_pin != "brak":
            logging.debug(f"resetuje SIM800L, reset pin {self._reset_pin}")
            print(f"resetuje SIM800L, reset pin {self._reset_pin}")
            #PIN GPIO4 na raspberry pi zero
            gpio4 = LED(self._reset_pin)
            gpio4.on()
            print("3,3V")
            logging.debug(f"3,3V")
            time.sleep(2)
            gpio4.off()
            print("0V")
            logging.debug(f"0V")
            time.sleep(2)
            cmd = 'AT'
            return_data=self._send_cmd(cmd, return_data=True, t=1)
            logging.debug(return_data)
            cmd = 'AT'
            return_data=self._send_cmd(cmd, return_data=True, t=1)
            logging.debug(return_data)

    def getFile(self, url,  sleep_to_read_bytes, nameOfFile):
        logging.debug("Jestem w getFile")
        self.reset_sim800()
        self.init()
        self._url = url
        self._sleep_to_read_bytes = sleep_to_read_bytes
        self._nameOfFile = nameOfFile
        try:
          self._IP = self._bearer(self._APN)
        except Exception as e:
            print(f"przy przydzielaniu IP urządzeniu wystąpił błąd {e}")

        #inicjalizacja połączenia HTTP
        cmd = 'AT+HTTPTERM'
        self._send_cmd(cmd, return_data=False)
        cmd = 'AT+HTTPINIT'
        self._send_cmd(cmd, return_data=False)
        cmd = f'AT+HTTPPARA="URL","{url}"'
        self._send_cmd(cmd, return_data=False)
        #ustawia nam _status_code i _number_of_bytes
        self.parserHTTPACTION(cmd)
        try:
            print("try catch")
            print(self._status_code)
            if self._status_code == b'200':
                print("receiveHTTTPREAD")
                result = self.receiveHTTTPREAD()
            else:
                print(f"status_code: {self._status_code}")
                if self._status_code == b'602':
                     print(f"brak pamieci w urządzeniu {self._status_code}")
                #file = self._status_code
        except Exception as e:
            print("Wystapil blad przy odbieraniu danych")
            print(f"tresc błędu {e}")
            traceback.print_exc()
            return False
        print("pobierania zdjecia czesciami")
        #jesli wczesniej nam zwrocil sim800 brak pamieci na tak ciezkie zdjecie
        if self._status_code == b'602':
            print("pobierania zdjecia czesciami")
            if os.path.exists(self._nameOfFile+".download"):
                os.remove(self._nameOfFile+".download")
            end_picture = open(self._nameOfFile+".download", "ab")
            x=0
            while True:
                print(x)
                name_part = self._nameOfFile+"_"+str(x)
                cmd = f'AT+HTTPPARA="URL","http://134.122.69.201/porcjonowanie_zdjec/kozienice/{self._nameOfFile}_{x}"'
                self._send_cmd(cmd, return_data=False)
                # ustawia nam _status_code i _number_of_bytes
                self.parserHTTPACTION(cmd)
                #if self._status_code ==
                try:
                    print("try catch")
                    print(self._status_code)
                    if self._status_code == b'200':
                        print("receiveHTTTPREAD")
                        result = self.receiveHTTTPREAD()
                    else:
                        print(f"blad {self._status_code}")
                    #else:
                    #    print(f"status_code: {self._status_code}")
                    #    if self._status_code == b'602':
                    #        print(f"brak pamieci w urządzeniu {self._status_code}")
                    #        return False
                except Exception as e:
                    print("Wystapil blad przy odbieraniu danych")
                    print(f"tresc błędu {e}")
                    traceback.print_exc()
                    return False
                x=x+1
        else:
            print(f"ahjo ! {self._status_code}")
        return True

    def parserHTTPACTION(self, cmd):
        try:
            time.sleep(2)
            cmd = 'AT+HTTPACTION=0'
            answerAT=self._send_cmd(cmd, return_data=True, get_decode_data=False, t=self._sleep_to_read_bytes)
            print(f"odpowiedz httpaction  {answerAT}")
            time.sleep(2)
            self._status_code = b''
            self._numberOfBytes = b''
            #przykladowa odpowiedz AT b'AT+HTTPACTION=0\r\r\nOK\r\n\r\n+HTTPACTION: 0,200,2729\r\n'
            status_and_number = re.sub(b'AT\+HTTPACTION=0\r\r\nOK\r\n\r\n\+HTTPACTION: 0,', b'', answerAT)
            status_and_number = re.sub(b'\r\n', b'', status_and_number)
            status_and_number = status_and_number.split(b',')
            print(status_and_number)
            if status_and_number == b'AT+HTTPACTION=0\r\r\nOK\r\n':
                raise Exception(" nie otrzymaliśmy odpowiedzi o statusie ( 200, 603, 602) prawdopodnie za krótki czas oczekiwania na sprawdzenie rozmiaru pliku")
            try:
                self._status_code = status_and_number[0]
                self._numberOfBytes = status_and_number[1]
                print(f"self._status_code: {self._status_code}")
                print(f"self._numberOfBytes: {self._numberOfBytes}")
            except Exception as e:
                print("status kod lub liczba bajtów nie ma")
                traceback.print_exc()
        except Exception as e:
            print(f"wystapil blad w parserHTTTPACTION - treść {e}")
            traceback.print_exc()
        logging.debug("koniec parser HTTPACTION")

    def receiveHTTTPREAD(self):
        print("receiveHTTPREAD - method")
        try:
            time.sleep(1)
            print(f"receive HTTPREAD")
            cmd = "AT+HTTPREAD"
            #file = self._http_send_cmd_and_save_answer(cmd, t=self._sleep_to_read_bytes, size=self._numberOfBytes, nameSaveFile="xyz.png")
            readBytes=0
            #if os.path.exists(self._nameOfFile+".download"):
            #    os.remove(self._nameOfFile+".download")
            packet_number = 1024
            koniec = False
            while koniec == False:
                if int(self._numberOfBytes) > readBytes + packet_number:
                    file = self._read_sent_data(cmd, numberOfBytes=packet_number, sleep_to_read_bytes=0.1)
                else:
                    file = self._read_sent_data(cmd, numberOfBytes=int(self._numberOfBytes)-readBytes+100, sleep_to_read_bytes=0.1)
                    koniec=True
                file = re.sub(b'AT\+HTTPREAD\r\r\n\+HTTPREAD: \d+\r\n', b'', file)
                file = re.sub(b'\r\nOK\r\n', b'', file)
                with open(self._nameOfFile+".download", "ab+") as f:
                    print(f"pierwsze 5 znakow {file[0:4]}")
                    f.write(file)
                readBytes = readBytes + packet_number
                print(readBytes)
            print("ahojjjjjjjjjjjj ! ")
        except Exception as e:
            print(f"wystapil blad w receiveHTTPREAD treść {e}")
            print(f"{e}")
            traceback.print_exc()
            return False
        #cmd = "AT+HTTPTERM"
        #logging.debug(f"{cmd}")
        #self._send_cmd(cmd, return_data=False)
        logging.debug("Koniec ftp - getFile")
        return True
