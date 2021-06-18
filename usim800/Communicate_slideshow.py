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

    def _reset_bytes_bufor(self):
        print("resetuje buffery")
        self._port.reset_input_buffer()
        self._port.reset_output_buffer()

    def _loop_send_cmd(self, cmd, t=1, bytes=1024, return_data=False, printio=False, get_decode_data=False,
                       read=True, check_error=False, i_wait_for=b'', how_many_iteration_test=5):
        number = 0
        while number < how_many_iteration_test:
            answer = self._send_cmd(cmd, t=t, bytes=bytes, return_data=return_data,
                        printio=printio, get_decode_data=get_decode_data, read=read, check_error=check_error)
            if answer.find(b'\r\nERROR\r\n') > -1:
                print("wystapil blad")
                print(answer)
                number = number + 1
                at_cmd="AT+TESTS"
                self._send_cmd(at_cmd, return_data=return_data)
                receive = self._port.read(bytes+100)
                print(receive)
            if i_wait_for!=b'' and answer.find(i_wait_for) == -1:
                print("ahoj")
                print(answer)
                number = number + 1
            else:
                return answer
            #print("resetuje buffery")
            #self._port.reset_input_buffer()
            #self._port.reset_output_buffer()
        return answer

    def _send_cmd(self, cmd, return_data, t=1.5, bytes=1024, printio=False
                  , get_decode_data=False, read=True, check_error=False, i_wait_for='+FTPGET: 1,1'
                  ):
        print(f"ahjo ! return_data: {return_data} ")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if not get_decode_data:
                receive = self._port.read(bytes)
                #print(f"DECODE_CMD_ANSWER : {receive}")
            else:
                receive = None
                print(f"DECODE_CMD_ANSWER: receive is None")
            if printio:
                print(receive.decode())
            #self._port.read(bytes)
            print(f"ahjo ! return_data: {return_data}")
            if return_data:
                print(f"RETURN_CMD: {receive}\n")
                if check_error == True:
                    if receive.find(b'ERROR\r\n') > -1:
                        raise Exception("odpowiedz serwera zawiera blad!")
                return receive

            return receive

    def _send_cmd(self, cmd, return_data=False, t=1.5, bytes=1024, printio=False
                  , get_decode_data=False, read=True, check_error=False, i_wait_for='+FTPGET: 1,1'
                  ):
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
                if check_error == True:
                    if receive.find(b'ERROR\r\n') > -1:
                        raise Exception("odpowiedz serwera zawiera blad!")
                return receive

            return receive

    def _send_cmd_and_save_answer_list_of_files(self, cmd, nameSaveFile, t=1, size=1024,
                                            read=True, return_data=True, printio=False,
                                            print_to_file=True):
        print(f"SIZE {size}")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if os.path.isfile(nameSaveFile):
                pass
            byte_number = 0
            bytes = self._port.read(size+100)
            if print_to_file:
                with open(nameSaveFile + '.log', 'wb+') as file:
                    file.write(bytes)
            if printio:
                print(bytes)
            if bytes.find(b'ERROR\r\n') > -1:
                print(bytes)
                return b'error'
            if bytes.find(b'FTPLIST: 2,0') > -1:
                print("brak bajtow do pobrania")
                return b'koniec'
            return bytes
        logging.debug("koniec _send_cmd_and_save_answer_list_of_files")

    def _send_cmd_and_save_answer_file(self, cmd, nameSaveFile, t=1, size=10000,
                                  read=True, return_data=True, printio=False,
                                  print_to_file=True):
        print(f"SIZE {size}")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        if read:
            time.sleep(t)
            if os.path.isfile(nameSaveFile):
                pass
            byte_number = 0
            bytes = self._port.read(size+100)
            if print_to_file:
                with open(nameSaveFile + '.log', 'wb+') as file:
                    file.write(bytes)
            if printio:
                print(bytes)
            if bytes.find(b'ERROR\r\n') > -1:
                print(bytes)
                return b'error'
            if bytes.find(b'FTPGET: 2,0') > -1:
                print("brak bajtow do pobrania")
                return b'koniec'
            return bytes
        logging.debug("koniec _send_cmd_and_save_answer_file")

    def _http_send_cmd_and_save_answer(self, cmd, t=1, size=10000
             , read=True, printio=False, nameSaveFile="default.txt"):
        cmd = self._setcmd(cmd)
        self._port.write(cmd.encode())
        find_start_line=False
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
                        if byte_number > 50 or byte == b'\n':
                            logging.debug(self.concatenate_list_data(data))
                            if b'\x89PNG\r\n' == self.concatenate_list_data(data):
                                logging.debug("wykrylem rozpoczecie pliku")
                                find_start_line = True
                            #OK\r\n - jest czescia komendy at
                            if find_start_line == True and self.concatenate_list_data(data) != b'OK\r\n':
                                #logging.debug("wklejam linie")
                                saveline = self.concatenate_list_data(data)
                                file.write(saveline)
                                #print(saveline)
                            data.clear()
                            byte_number = 0

        except Exception as e:
            print("przy zapisie pliku coś poszło nie tak")
            traceback.print_exc()
        logging.debug("koniec _send_cmd_and_save_answer")

    def _read_sent_data(self, cmd, packetOfBytes, sleep_to_read_bytes):
        #logging.debug("_read_send_data method")
        print("_read_sent_data")
        cmd = self._setcmd(cmd)
        print("KOMENDA: " + str(cmd))
        self._port.write(cmd.encode())
        time.sleep(sleep_to_read_bytes)
        receive = self._port.read(packetOfBytes) #numberOfBytes)
        #logging.debug(f"zapisane {receive}")
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
        self._send_cmd(cmd, return_data=False)
        cmd = "AT+SAPBR=2,1"
        ip_answer_bytes = self._send_cmd(cmd, return_data=True)
        logging.debug("przydzielanie IP")
        IP = self.parserIPNumber(ip_answer_bytes)
        return IP

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
