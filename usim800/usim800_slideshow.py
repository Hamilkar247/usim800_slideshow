import logging

import serial
from usim800_slideshow.usim800.Communicate_slideshow import communicate_slideshow
from usim800_slideshow.usim800.Request_slideshow import request_slideshow
from usim800_slideshow.usim800.Request_slideshow import request_ftp


class sim800_slideshow(communicate_slideshow):
    TIMEOUT = 1

    def __init__(self, baudrate, path):
        logging.debug("dziendobry sim800_slideshow")
        self.port = serial.Serial(path, baudrate, timeout=sim800_slideshow.TIMEOUT)
        print("port: " + str(self.port))
        super().__init__(self.port)

        self.requests = request_slideshow(self.port)
        ###self.info = info(self.port)
        ###self.sms = sms(self.port)


class ftp_slideshow(communicate_slideshow):
    TIMEOUT = 1

    def __init__(self, baudrate, path, reset_pin):
        logging.debug("ftp")
        self.port = serial.Serial(path, baudrate, timeout=ftp_slideshow.TIMEOUT)
        print("port: " + str(self.port))
        super().__init__(self.port)

        self.request_ftp = request_ftp(self.port)
        self.request_ftp.set_reset_pin(reset_pin)
