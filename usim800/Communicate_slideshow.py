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
        for element in list:
            result += element
        return result

    def _send_cmd_and_save_answer(self, cmd, t=1, size=10000, typ_pliku="bitowy",
                                  read=True, return_data=True, printio=False, nameSaveFile="default.txt", byte_line_start=b''):
        print(f"SIZE {size}")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        find_start_line = False
        text = b''
        try:
            if read:
                data = []
                if os.path.isfile(nameSaveFile):
                    print("uwaga nadpisuje obecny plik")
                with open(nameSaveFile, 'ab+') as file:
                    while True:
                        byte_number = 0
                        byte = self._port.read(1)
                        byte_number = byte_number + 1
                        if not byte:
                            break
                        data.append(byte)
                        #print(data)
                        if byte_number > 50 or byte == b'\n':
                            print("ahoj")
                            print(self.concatenate_list_data(data))
                            saveline = self.concatenate_list_data(data)

                            if True:#saveline != b'AT+FTPGET=2,1024\r\r\n' \
                                   #and saveline != b'+FTPGET: 2,1024\r\n' \
                                   #and saveline != b'OK\r\n' \
                                   #and saveline != b'AT+FTPGET=2,'+str.encode(str(size))+b'\r\r\n' \
                                   #and saveline != b'+FTPGET: 2,'+str.encode(str(size))+b'\r\n' \
                                   #and saveline != b'+FTPGET: 2,0\r\n':
                                #print("wklejam linie")
                                if typ_pliku=="tekstowy":
                                    print("tekstowy!")
                                    saveline=saveline.replace(b'\r\n', b'')
                                file.write(saveline)
                                print(saveline)
                            if saveline == b'+FTPGET: 2,0\r\n':
                                print("wystapil +FTPGET: 2,0")
                                return True
                            else:
                                print(f"nie wkleiłem: {saveline}")
                            data.clear()
                            byte_number = 0
                    return False

                    #print(bytes)
                    #lines = []
                    #lines = bytes.split(b'\n')
                    #pprint(lines)
                    #for number in range(len(lines)-1):
                    #    if lines[number] != b'AT+FTPGET=2,1024\r\r' \
                    #        and lines[number] != b'+FTPGET: 2,1024\r' \
                    #        and lines[number] != b'OK\r':
                    #        # and lines[number] != b'AT+FTPGET=2,'+str.encode(str(size))+b'\r\r' \
                    #        file.write(lines[number]+b'\n')

                        #elif lines[number] != b'+FTPGET: 2,0\r':
                        #    print(f"uwaga {lines[number]}")
                        #    and lines[number] != b'ERROR\r':
                        #    break
                        #else:
                        #    print(f"nie drukuje {lines[number]}")
                    #file.write(bytes)

                    #while True:
                    #    #print("z")
                    #    byte = self._port.read(1)
                    #    #print(byte)
                    #    byte_number = byte_number + 1
                    #    if not byte:
                    #        break
                    #    data.append(byte)
                    #    #print(data)
                    #    if byte_number > 50 or byte == b'\n':
                    #        print("ahoj")
                    #        print(self.concatenate_list_data(data))
                    #        if byte_line_start == self.concatenate_list_data(data):
                    #            print("wykrylem rozpoczecie pliku")
                    #            find_start_line = True
                    #        # OK\r\n - jest czescia komendy at
                    #        if find_start_line == True and self.concatenate_list_data(data) != b'OK\r\n':
                    #            print("wklejam linie")
                    #            saveline = self.concatenate_list_data(data)
                    #            file.write(saveline)
                    #            print(saveline)
                    #        data.clear()
                    #        byte_number = 0
                        #else:
                        #    print(f"RETURN_CMD: {data}\n")
                            #return data
                return data
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
