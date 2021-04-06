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

    def getFile(self, url, header=None):
        self.init()
        self._url = url
        self._IP = self._bearer(self._APN)

        #inicjalizacja połączenia HTTP
        cmd = 'AT+HTTPINIT'
        self._send_cmd(cmd)
        cmd = 'AT+HTTPPARA="CID", 1'
        self._send_cmd(cmd)
        cmd = 'AT+HTTPARA="URL", "{}"'.format(url)
        self._send_cmd(cmd)
        time.sleep(3)
        cmd = 'AT+HTTPACTION=0'
        self._send_cmd(cmd)
        time.sleep(2)
        cmd = "AT+HTTPREAD"
        self._send_cmd(cmd, get_decode_data=True)
        data = self._getdata(
            data_to_decode=[], string_to_decode=None, till=b'\n', count=2, counter=0)
        #tk = ParserFile(data)

