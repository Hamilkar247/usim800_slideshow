import logging
import serial
import time


class communicate_slideshow:
    cmd_list = []

    def __init__(self, port):
        self._port = port

    def _setcmd(self, cmd, end='\r\n'):
        end = '\r\n'
        return (cmd + end)

    def _readtill(self, till="OK"):
        receive = self._port.read(14816)  # ta liczba to się wydaje że to liczba zczytanych bajtów
        receive_decode = receive.decode()
        while "OK" not in receive_decode:
            receive_decode += receive_decode.decode()
            receive = self._port.read(14816)

    def _ATcmd(self):
        self._port.write(self._setcmd("AT").encode())
        receive = self._port.read(14816)

    def _send_cmd(self, cmd, t=1, bytes=14816, return_data=False, printio=False
                  , get_decode_data=False, read=True):
        cmd = self._setcmd(cmd)
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if not get_decode_data:
                receive = self._port.read(bytes)
            else:
                receive = None
            if printio:
                print(receive.decode())
            if return_data:
                return receive

    def _read_sent_data(self, numberOfBytes):
        receive = self._port.read(numberOfBytes)
        return receive

    def _bearer(self, APN): #myśle że chodzi w nazwie o definiowanie nośnej
        self._ATcmd()
        cmd = "AT+SABR=0,1" #nie wiem co do końca robi - do weryfikacji
        self._send_cmd(cmd)
        self._ATcmd()
        # przełączenie na transmisje GPRS
        cmd = 'AT+SAPBR=3,1, "CONTYPE", "GPRS"'
        self._send_cmd(cmd)
        #Accest point name - definiuje ścieżkę sieciową dla wszystkich połączeń z siecią komórkową danych
        cmd = 'AT+SAPBR=3,1, "APN", "{}'.format(APN)
        self._send_cmd(cmd)
        #otwiera zawa
        cmd = "AT+SAPBR=1,1"
        self._send_cmd(cmd)



