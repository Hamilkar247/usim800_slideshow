import logging

import serial
from usim800_slideshow.usim800.Communicate_slideshow import communicate_slideshow
from usim800_slideshow.usim800.Request_slideshow import request_httpconnection
from usim800_slideshow.usim800.Request_slideshow import request_ftpconnection


class sim800_slideshow(communicate_slideshow):
    TIMEOUT = 1

    def __init__(self, baudrate, path, APN, sleep_to_read_bytes,
                 reset_pin, time_packet_ftp):
        logging.debug("sim800_slideshow http i ftp")
        self.port = serial.Serial(path, baudrate, timeout=sim800_slideshow.TIMEOUT)
        print("port: " + str(self.port))
        super().__init__(self.port)

        self.requests = request_httpconnection(self.port)
        self.requests.set_reset_pin(reset_pin)
        self.requests.set_APN(APN)
        self.requests.set_sleep_to_read_bytes(sleep_to_read_bytes=sleep_to_read_bytes)

        self.request_ftp = request_ftpconnection(self.port)
        self.request_ftp.set_time_packet_ftp(time_packet_ftp=time_packet_ftp)
        self.request_ftp.set_reset_pin(reset_pin)
        ###self.info = info(self.port)
        ###self.sms = sms(self.port)

    def __update__(self, baudrate, path, APN, sleep_to_read_bytes,
                   reset_pin, time_packet_ftp):
        logging.debug("ftp")
        self.port = serial.Serial(path, baudrate, timeout=sim800_slideshow.TIMEOUT)
        print("port: " + str(self.port))
        super().__init__(self.port)

        self.requests.set_APN(APN=APN)
        self.requests.set_sleep_to_read_bytes(sleep_to_read_bytes=sleep_to_read_bytes)
        self.requests.set_reset_pin()

        self.request_ftp = request_ftpconnection(self.port)
        self.request_ftp.set_time_packet_ftp(time_packet_ftp)
        self.request_ftp.set_reset_pin(reset_pin)
