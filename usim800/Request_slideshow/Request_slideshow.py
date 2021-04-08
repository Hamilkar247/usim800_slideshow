from usim800.Communicate_slideshow import communicate_slideshow
import logging
import time


class request_slideshow(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status_code = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None

    def init(self):
        self._status_code = None
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

    def getFile(self, url, header=None):
        logging.debug("Jestem w getFile")
        self.init()
        self._url = url
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
        time.sleep(3)
        cmd = 'AT+HTTPACTION=0'
        number_of_bytes=self.readNumberOfBytes(cmd, return_data=True)

        try:
            cmd = 'AT+HTTPREAD'
            file_bytes=self.receiveHTTTPREAD(cmd)
            print(file_bytes)
        except Exception as e:
            print("Wystapil blad przy odbieraniu danych")
            print(f"tresc błędu {e}")
            file_bytes=None
        return file_bytes

    def readNumberOfBytes(self):
        time.sleep(2)

    def receiveHTTTPREAD(self, cmd):
        time.sleep(2)
        bytes_file_and_at_com=self._send_cmd(cmd, get_decode_data=False, return_data=True)
        logging.debug(f"pobrane {bytes_file_and_at_com}")
        logging.debug(f"typ {type(bytes_file_and_at_com)}")
        logging.debug(f"podzielone")
        logging.debug(bytes_file_and_at_com.split(b'2729\r\n'))
        only_bytes_file=bytes_file_and_at_com.split(b'2729\r\n')[1]
        return only_bytes_file
