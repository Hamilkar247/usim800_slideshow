import logging
import os
import traceback

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
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if not get_decode_data:
                receive = self._port.read(bytes)
                logging.debug(f"DECODE_CMD_ANSWER: {receive}")

            else:
                receive = None
                logging.debug(f"DECODE_CMD_ANSWER: receive is None")
            if printio:
                print(receive.decode())
            if return_data:
                logging.debug(f"RETURN_CMD: {receive}")
                return receive

    def concatenate_list_data(self, list):
        result = b''
        for element in list:
            result += element
        return result

    def _send_cmd_and_save_answer(self, cmd, t=1, size=10000
             , read=True, printio=False, nameSaveFile="default.txt"):
        cmd = self._setcmd(cmd)
        self._port.write(cmd.encode())
        try:
            if read:
                self.size=size
                data=[]
                if os.path.isfile(nameSaveFile):
                    print("uwaga nadpisuje obecny plik")
                with open(nameSaveFile, 'wb') as file:
                    linia = 0
                    byte_number = 0
                    while True:
                        byte = self._port.read(1)
                        byte_number = byte_number+1
                        if not byte:
                            break
                        data.append(byte)
                        if byte_number > 10:
                            linia=linia+1
                            saveline = self.concatenate_list_data(data)
                            file.write(saveline)
                            print(saveline)
                            data.clear()
                            byte_number = 0

        except Exception as e:
            print("przy zapisie pliku coś poszło nie tak")
            traceback.print_exc()
        logging.debug("koniec _send_cmd_and_save_answer")

    def _read_sent_data(self, numberOfBytes):
        logging.debug("_read_send_data method")
        receive = self._port.read(numberOfBytes)
        logging.debug(f"zapisane {receive}")
        return receive

    def _bearer(self, APN):  # myśle że chodzi w nazwie o definiowanie nośnej
        logging.debug(f"APN:{APN}")
        self._ATcmd()
        cmd = f'AT+SAPBR=3,1,"APN","{APN}"'
        self._send_cmd(cmd)
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

        stringIP=data
        logging.debug(f"{stringIP.split()}")
        logging.debug(f"{stringIP.split()[2]}")
        stringIP = stringIP.split()[2]
        p = re.compile('"(.*)"')
        print(p.findall(stringIP)[0])
        stringIP=p.findall(stringIP)[0]
        print(stringIP)
        return stringIP.decode()

    def parserIPNumber(self, bytes):
        logging.debug("parserIPNumber method")
        logging.debug(f"start data {bytes}")
        logging.debug(bytes.split())
        answerWithIP = bytes.split()[2]
        logging.debug(f"odpowiedz z czescia zawierajaca ip: {answerWithIP}")
        ip = answerWithIP.split("\"".encode())[1]  # encode daje to samo co b"\""
        decode_ip=ip.decode()
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
