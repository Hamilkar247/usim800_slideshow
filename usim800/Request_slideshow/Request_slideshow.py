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
        self._send_cmd(cmd)
        time.sleep(2)
        cmd = "AT+HTTPREAD"
        text=self._send_cmd(cmd, get_decode_data=False, return_data=True)
        logging.debug(f"ahjo text {text}")

        #data = self._getdata(
        #    data_to_decode=[], string_to_decode=None, till=b'\n', count=2, counter=0)
        #tk = ParserFile(data)
        return text
