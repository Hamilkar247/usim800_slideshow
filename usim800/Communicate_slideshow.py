import logging
import os
import traceback
from pprint import pprint

import serial
import time
import re


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
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if not get_decode_data:
                receive = self._port.read(bytes)
                print(f"DECODE_CMD_ANSWER: {receive}")

            else:
                receive = None
                print(f"DECODE_CMD_ANSWER: receive is None")
            if printio:
                print(receive.decode())
            if return_data:
                print(f"RETURN_CMD: {receive}\n")
                return receive

    def concatenate_list_data(self, list):
        result = b''
        liczba_elementow=len(list)
        number = 0
        for element in list:
            if number < liczba_elementow-1 and element != b'':
                result += element + b''
            else:
                result += element + b''
            number = number + 1
        return result

    def split_data(self, s):
        data = []
        data2 = []
        data.extend(s.split(b'\r\r\n'))
        print("data - \r\r\n")
        pprint(data)
        for element in data:
            data2.extend(element.split(b'\r\n'))
        print("data2 \r\n")
        pprint(data2)
        return data2

    def delete_redundant_line(self, list, nameSaveFile):
        data=[]
        for element in list:
            #if element.find(b'\x89PNG'):
            #    data.append(element+b"\r\n")
            if element.find(b'FTPGET') == -1 and element.find(b'OK') == -1 and element != b'':
                data.append(element+b"")
                #print(data)
            else:
                pass
                #print("nie wklejam:")
                #print(f"element.find(b'FTPGET') > -1 {element.find(b'FTPGET')>-1}")
                #print(f"element.find(b'OK')>-1  {element.find(b'OK')>-1}")
                #print(f"moze pusty string? {element != b''}")
                #print(element)
        #print("koncowa tablica")
        #pprint(data)
        with open(nameSaveFile, 'ab+') as file:
            file.write(self.concatenate_list_data(data))

    def _send_cmd_and_save_answer(self, cmd, t=1, size=10000, typ_pliku="bitowy",
                                  read=True, return_data=True, printio=False, nameSaveFile="default.txt", byte_line_start=b''):
        print(f"SIZE {size}")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        find_start_line = False
        text = b''
        #try:
        if read:
            to_file = []
            data = []
            if os.path.isfile(nameSaveFile):
                pass
                #print("uwaga nadpisuje obecny plik")
            #with open(nameSaveFile, 'ab+') as file:

            byte_number = 0
            bytes = self._port.read(size+100)
            print(bytes)
            if bytes.find(b'ERROR\r\n') > -1:
                print(bytes)
                return True #raise Exception("wystapil blad w pobranej ramce")
            if bytes.find(b'FTPGET: 2,0') > -1:
                print("brak bajtow do pobrania")
                return True
            bytes = re.sub(b'AT\+FTPGET=2,\d+\r\r\n\+FTPGET: 2,\d+\r\n', b'', bytes)
            bytes=bytes.replace(b'\r\nOK\r\n', b'')
            with open(nameSaveFile, 'ab+') as file:
                file.write(bytes)
            return False
            #sy = sx.replace(b'\r\nOK\r\n', b'')

            #lines = self.split_data(bytes)
            #print(bytes)
            #pprint(lines)
            #self.delete_redundant_line(lines, nameSaveFile)

        #except Exception as e:
        #    print("przy zapisie pliku coś poszło nie tak")
        #    traceback.print_exc()
        logging.debug("koniec _send_cmd_and_save_answer")
        #return data

    def _read_sent_data(self, numberOfBytes):
        logging.debug("_read_send_data method")
        receive = self._port.read(numberOfBytes)
        logging.debug(f"zapisane {receive}")
        return receive

    def _bearer(self, APN):  # myśle że chodzi w nazwie o definiowanie nośnej
        logging.debug(f"APN:{APN}")
        self._ATcmd()

        cmd = f'AT+SAPBR=3,1,"Contype","GPRS"'
        self._send_cmd(cmd, return_data=True)
        cmd = f'AT+SAPBR=3,1,"USER","{APN}"'
        self._send_cmd(cmd, return_data=True)
        cmd = f'AT+SAPBR=3,1,"PWD","{APN}"'
        self._send_cmd(cmd, return_data=True)
        cmd = f'AT+SAPBR=3,1,"APN","{APN}"'
        self._send_cmd(cmd, return_data=True)
        cmd = "AT+SAPBR=1,1"
        self._send_cmd(cmd)
        cmd = "AT+SAPBR=2,1"
        ip_answer_bytes = self._send_cmd(cmd, return_data=True)
        logging.debug("przydzielanie IP")
        IP = self.parserIPNumber(ip_answer_bytes)
        return IP

    def takeIP(self, data):
        logging.debug("takeIP method")
        logging.debug(f"start data {data}")

        stringIP = data
        logging.debug(f"{stringIP.split()}")
        logging.debug(f"{stringIP.split()[2]}")
        stringIP = stringIP.split()[2]
        p = re.compile('"(.*)"')
        print(p.findall(stringIP)[0])
        stringIP = p.findall(stringIP)[0]
        print(stringIP)
        return stringIP.decode()

    def parserIPNumber(self, bytes):
        logging.debug("parserIPNumber method")
        logging.debug(f"start data {bytes}")
        logging.debug(bytes.split())
        answerWithIP = bytes.split()[2]
        logging.debug(f"odpowiedz z czescia zawierajaca ip: {answerWithIP}")
        ip = answerWithIP.split("\"".encode())[1]  # encode daje to samo co b"\""
        decode_ip = ip.decode()
        logging.debug(f"zdekodowane ip (string) {decode_ip}")
        logging.debug(f"klasa {type(decode_ip)}")
        return decode_ip

    def _getdata(self, data_to_decode=[], string_to_decode=None, till=b'\n', count=2, counter=0):
        logging.debug(f"Communicate_slideshow.py - _getdata")
        receive = self._port.read(1)
        # logging.debug(f"receive:{rcv}")
        if receive == till:
            # logging.debug(f"receive==till --> {receive}"}
            counter += 1
            if counter == count:
                data_to_decode.append(receive)
                return b"".join(data_to_decode)
            else:
                data_to_decode.append(receive)
                return self._getdata(data_to_decode, string_to_decode, till, count, counter)
        else:
            # logging.debug("receive!=till")
            data_to_decode.append(receive)
            return self._getdata(data_to_decode, string_to_decode, till, count, counter)
