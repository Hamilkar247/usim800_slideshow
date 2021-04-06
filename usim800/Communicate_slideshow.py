import logging
import serial

class communicate_slideshow:
    cmd_list = []

    def __init__(self, port):
        self._port = port
        self._port=0

    def _setcmd(self, cmd, end='\r\n'):
        end = '\r\n'
        return (cmd + end)

    def _readtill(self, till="OK"):
        receive = self._port.read(14816)      #ta liczba to się wydaje że to liczba bajtów
        receive_decode= receive.decode()
        while "OK" not in receive_decode:
            receive_decode += receive_decode.decode()
            receive = self._port.read(14816)
