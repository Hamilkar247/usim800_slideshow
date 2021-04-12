import serial
import time
import re
import json
import logging

class communicate:
    cmd_list = []

    def __init__(self, port):
        self._port = port

    def _setcmd(self, cmd, end='\r\n'):
        end = '\r\n'

        return (cmd + end)
    def _readtill(self,till="OK"):
        rcv = self._port.read(14816)
        rcvd = rcv.decode()
        while "OK" not in rcvd: 
            rcvd += rcv.decode()
            rcv = self._port.read(14816)
        return rcvd
    def _ATcmd(self):
        self._port.write(self._setcmd("AT").encode())
        rcv = self._port.read(14816)

    def _send_cmd(self, cmd, t=1, bytes=14816, return_data=False, 
                printio=False, get_decode_data=False,read=True):
        cmd = self._setcmd(cmd)
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if not get_decode_data:
                rcv = self._port.read(bytes)
            else:
                rcv = None

            if printio:
                print(rcv.decode())
            
            if return_data:
                return rcv

    def _read_sent_data(self, numberOfBytes):
        rcv = self._port.read(numberOfBytes)

        return rcv

    def _bearer(self,APN):
        self._ATcmd()
        cmd = "AT +SAPBR=0,1"
        self._send_cmd(cmd)
        self._ATcmd()
        cmd = 'AT + SAPBR=3,1,"CONTYPE","GPRS"'
        self._send_cmd(cmd)
        cmd = 'AT + SAPBR=3,1,"APN","{}"'.format(APN)
        self._send_cmd(cmd)
        cmd = "AT + SAPBR=1,1"
        self._send_cmd(cmd)
        cmd = "AT + SAPBR=2,1"
        data = self._send_cmd(cmd,return_data=True)
        try :
           IP = data.decode().split()[4].split(",")[-1].replace('"','')
        except:
            IP = None
        return IP

    def _getdata(self, data_to_decode=[], string_to_decode=None, till=b'\n', count=2, counter=0):
        logging.debug(f"Communicate.py - _getdata")
        rcv = self._port.read(1)
        #logging.debug(f"rcv:{rcv}")
        if rcv == till:
         #   logging.debug(f"rcv==till --> {rcv}")
            counter += 1
         #   logging.debug(f"counter {counter}, count {count}")
            if counter == count:
                data_to_decode.append(rcv)
                return b"".join(data_to_decode)
            else:
                data_to_decode.append(rcv)
                return self._getdata(data_to_decode, string_to_decode, till, count, counter)
        else:
         #   logging.debug("rcv!=till")
            data_to_decode.append(rcv)
            return self._getdata(data_to_decode, string_to_decode, till, count, counter)

    def _getdataFile(self, data_to_decode=[], string_to_decode=None, till=b'\n', count=2, counter=0):
        logging.debug(f"Communicate.py - _getdataFile")
        rcv = self._port.read(1)
        logging.debug(f"rcv:{rcv}")
        if rcv == till:
            logging.debug(f"rcv==till --> {rcv}")
            counter += 1
            logging.debug(f"counter {counter}, count {count}")
            if counter == count:
                data_to_decode.append(rcv)
                return b"".join(data_to_decode)
            else:
                data_to_decode.append(rcv)
                return self._getdata(data_to_decode, string_to_decode, till, count, counter)
        else:
            logging.debug("rcv!=till")
            data_to_decode.append(rcv)
            return self._getdata(data_to_decode, string_to_decode, till, count, counter)
