import sys
import traceback

from usim800.Communicate_slideshow import communicate_slideshow
import logging
import time


class request_slideshow(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status_code = None
        self._numberOfBytes = None
        self._sleep_to_read_bytes = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None

    def init(self):
        self._status_code = None
        self._numberOfBytes = None
        self._sleep_to_read_bytes = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None

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

    def getFile(self, url, sleep_to_read_bytes, header=None):
        logging.debug("Jestem w getFile")
        self.init()
        self._url = url
        self._sleep_to_read_bytes = sleep_to_read_bytes
        try:
          self._IP = self._bearer(self._APN)
        except Exception as e:
            print(f"przy przydzielaniu IP urządzeniu wystąpił błąd {e}")

        #inicjalizacja połączenia HTTP
        cmd = 'AT+HTTPINIT'
        self._send_cmd(cmd)
        #cmd = 'AT+HTTPPARA="CID", 1'
        #self._send_cmd(cmd)
        cmd = f'AT+HTTPPARA="URL","{url}"'
        self._send_cmd(cmd)
        #ustawia nam _status_code i _number_of_bytes
        self.parserHTTPACTION(cmd)
        try:
            file_bytes=self.receiveHTTTPREAD(cmd)
            print(file_bytes)
        except Exception as e:
            print("Wystapil blad przy odbieraniu danych")
            print(f"tresc błędu {e}")
            file_bytes=None
        return file_bytes

    def parserHTTPACTION(self, cmd):
        try:
            time.sleep(2)
            cmd = 'AT+HTTPACTION=0'
            answerAT=self._send_cmd(cmd, get_decode_data=False, return_data=True, t=self._sleep_to_read_bytes)
            time.sleep(2)
            self._status_code = b''
            self._numberOfBytes = b''
            #przykladowa odpowiedz AT b'AT+HTTPACTION=0\r\r\nOK\r\n\r\n+HTTPACTION: 0,200,2729\r\n'
            status_and_number = answerAT.split(b'+HTTPACTION: 0,')[1][0:-2]
            print(status_and_number)
            self._status_code = status_and_number.split(b',')[0]
            self._numberOfBytes = status_and_number.split(b',')[1]
            print(self._status_code)
            print(self._numberOfBytes)
        except Exception as e:
            print(f"wystapil blad w parserHTTTPACTION - treść {e}")
            traceback.print_exc()

    def receiveHTTTPREAD(self, cmd):
        try:
            time.sleep(1)
            cmd = 'AT+HTTPREAD'
            bytes_file_and_at_com=self._send_cmd(cmd, get_decode_data=False, return_data=True, t=self._sleep_to_read_bytes)
            logging.debug(f"pobrane {bytes_file_and_at_com}")
            logging.debug(f"typ {type(bytes_file_and_at_com)}")
            logging.debug(f"podzielone")
            #przykladowo efekt bedzie b'2729'+b'\r\n'
            splitter=b"HTTPREAD: "+self._numberOfBytes+b"\r\n"
            logging.debug(bytes_file_and_at_com.split(splitter))
            only_bytes_file=bytes_file_and_at_com.split(splitter)[1]
            logging.debug(sys.getsizeof(only_bytes_file))
            return only_bytes_file
        except Exception as e:
            print(f"wystapil blad w receiveHTTPREAD treść {e}")
            traceback.print_exc()
    #def receiveHTTPREAD_ReadFile(self, till=b'\n', count=2, counter=0):

