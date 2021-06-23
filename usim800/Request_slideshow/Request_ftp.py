import os
import re
import sys
import traceback
from pprint import pprint

from gpiozero import LED

from usim800_slideshow.usim800.Communicate_slideshow import communicate_slideshow
import logging
import time


class request_ftp(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reset_pin = None
        self._time_packet_ftp = None
        self._status_code = None
        self._ftp_server_ip = None
        self._ftp_port = None
        self._ftp_mode = None  # 0 - aktywny, 1 - pasywny
        self._ftp_nickname = None
        self._ftp_pass = None
        self._ftp_get_name_file = None
        self._ftp_get_path_file = None
        self._ftp_put_name_file = None
        self._ftp_put_path_file = None
        self._ftp_text_to_post = []
        self._sleep_to_read_bytes = None
        self._APN = None
        self._status_code = None
        self._numberOfBytes = None
        self._IP = None
        self._file_bytes = b''

    def init(self):
        pass

    def utf8len(self, s):
        return len(s.encode('utf-8'))

    def set_reset_pin(self, reset_pin):
        self._reset_pin = reset_pin

    def set_time_packet_ftp(self, time_packet_ftp):
        self._time_packet_ftp = time_packet_ftp

    def polaczenie_z_siecia_i_nadania_ip(self):
        try:
            return self._bearer(self._APN)
        except Exception as e:
            print(f"przy przydzielaniu IP urządzeniu wystpił błąd {e}")
            return None

    def czyIpJestNadane_jesliNiePrzydziel(self):
        cmd = "AT"
        self._send_cmd(cmd, return_data=True, t=1)
        cmd = "AT+SAPBR=2,1"
        ip_answer = b''
        ip_answer = self._send_cmd(cmd, return_data=True, t=1)
        if ip_answer.find(b'0.0.0.0') > -1:
            print("ip_answer.find(b'0.0.0.0')")
            self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        if ip_answer.find(b'ERROR\r\n') > -1:
            print("ip_answer.find(b'ERROR\r\n') > -1")
            self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        if ip_answer == b'':
            print("ip_answer == b''")
            self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        if ip_answer is None:
            print("ip_answer is None")
            self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        else:
            IP = re.sub(b'AT\+SAPBR=2,1\r\r\n\+SAPBR: 1,1,\"', b'', ip_answer)
            IP = re.sub(b'\"\r\n\r\nOK\r\n', b'', IP)
            print(IP)
            self._IP = IP

    def reset_sim800(self):
        print(f" ustawiony pin resetu {self._reset_pin}")
        if self._reset_pin != "brak":
            logging.debug(f"resetuje SIM800L, reset pin {self._reset_pin}")
            print(f"resetuje SIM800L, reset pin {self._reset_pin}")
            #PIN GPIO4 na raspberry pi zero
            gpio4 = LED(self._reset_pin)
            gpio4.on()
            print("3,3V")
            logging.debug(f"3,3V")
            time.sleep(2)
            gpio4.off()
            print("0V")
            logging.debug(f"0V")
            time.sleep(2)
            cmd = 'AT'
            return_data=self._send_cmd(cmd, return_data=True, t=1)
            logging.debug(return_data)
            cmd = 'AT'
            return_data=self._send_cmd(cmd, return_data=True, t=1)
            logging.debug(return_data)
        else:
            logging.debug("nie ma ustawionego pinu do resetu")

    def getFilesMetadata(self, APN, server_ip,
                         port, mode, get_path_file,
                         nickname, password):
        self.reset_sim800()
        logging.debug("getFilesMetadata")
        self.init()
        self._ftp_server_ip = server_ip
        self._ftp_port = port
        self._ftp_mode = mode
        self._ftp_get_path_file = get_path_file
        self._ftp_nickname = nickname
        self._ftp_pass = password
        self._APN = APN

        # nadanie IP
        self.czyIpJestNadane_jesliNiePrzydziel()

        self._reset_bytes_bufor()
        # inicjalizacja polaczenia FTP
        try:
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPORT=21"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPGETPATH={self._ftp_get_path_file}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPSCONT"  # zapisuje ustawiona konfiguracje
            self._loop_send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()
            return b'error'

        try:
            # nadanie IP
            self.czyIpJestNadane_jesliNiePrzydziel()
            cmd = f"AT+FTPLIST=1"
            self._loop_send_cmd(cmd, return_data=True, how_many_iteration_test=5, t=5, i_wait_for=b'+FTPLIST: 1,1')
            number = 0
            list_of_files = b''
            packet_of_bytes = b''
            size_of_bytes_in_packet = 1024
            while packet_of_bytes != b'koniec' and packet_of_bytes != b'error':
                cmd = f"AT+FTPLIST=2,{size_of_bytes_in_packet}"
                print(f"wczytano liczbe bajtow {size_of_bytes_in_packet}")
                packet_of_bytes = self._send_cmd_and_save_answer_list_of_files(cmd, t=self._time_packet_ftp, size=size_of_bytes_in_packet,
                                                    nameSaveFile="ftp_list", return_data=True, read=True,
                                                    printio=False, print_to_file=True)
                packet_of_bytes = re.sub(b'AT\+FTPLIST=2,\d+\r\r\n\+FTPLIST: 2,\d+\r\n', b'', packet_of_bytes)
                packet_of_bytes = re.sub(b'\r\nOK\r\n', b'', packet_of_bytes)
                if packet_of_bytes != b'koniec' and packet_of_bytes != b'error':
                    list_of_files = list_of_files + packet_of_bytes
                if packet_of_bytes == b'error':
                    raise Exception("wystapil blad przy pobieraniu danych!")
                number = number + 1
                print(f"numer pobranej paczki {number} - ftp_list z {self._ftp_get_path_file}")

        except Exception as e:
            print(f"przy probie sprawdzanie metadanych plików na serwerze FTP wystąpił błąd ")
            print(f"{e}")
            traceback.print_exc()
            return b'error'
        self._reset_bytes_bufor()
        logging.debug("koniec getFilesMetadata")
        return list_of_files

    def getFile(self, APN, server_ip, port, mode,
                get_name_file, get_path_file, nickname, password):
        self.reset_sim800()
        logging.debug("jest w getFile")
        self.init()
        self._ftp_server_ip = server_ip
        self._ftp_port = port
        self._ftp_mode = mode
        self._ftp_nickname = nickname
        self._ftp_pass = password
        self._ftp_get_name_file = get_name_file
        self._ftp_get_path_file = get_path_file
        self._APN = APN

        # nadanie IP
        self.czyIpJestNadane_jesliNiePrzydziel()


        self._reset_bytes_bufor()
        print(f"{self._IP}")
        # inicjalizacja polaczenia FTP
        try:
            cmd = 'AT'
            self._send_cmd(cmd, return_data=True)
            cmd = 'AT+FTPREST=?'
            self._send_cmd(cmd, return_data=True)
            #cmd = 'AT+FTPCID=1'
            #self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK', how_many_iteration_test=5)
            cmd = f"AT+FTPPORT=21"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK', how_many_iteration_test=5)
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            # print(f"ahjo ftpgetname {self._ftp_get_name_file}")
            cmd = f"AT+FTPGETNAME={self._ftp_get_name_file}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPGETPATH={self._ftp_get_path_file}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPSCONT"  # zapisuje ustawiona konfiguracje
            self._loop_send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()
            return b'error'

        try:
            self.czyIpJestNadane_jesliNiePrzydziel()
            cmd = f"AT+FTPSCONT?"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPGET=1"
            self._loop_send_cmd(cmd, get_decode_data=False, return_data=True, t=3, i_wait_for=b'+FTPGET: 1,1')
            print("ahoj")
            number = 0
            file_bytes = b''
            packet_of_bytes = b''
            size_of_bytes_in_packet = 1024
            while packet_of_bytes != b'koniec' and packet_of_bytes != b'error':  # and number < 5):  #      print(f"liczba bitow:{liczba_bitow}")
                cmd = f'AT+FTPGET=2,{size_of_bytes_in_packet}'
                print(f"wczytano liczbe bajtów: {size_of_bytes_in_packet}")
                print(f"czas oczekiwania na każdy pakiet i baudrate: t:{self._time_packet_ftp}")
                packet_of_bytes = self._send_cmd_and_save_answer_file(cmd, t=self._time_packet_ftp,
                    size=size_of_bytes_in_packet, nameSaveFile=self._ftp_get_name_file,
                    return_data=True, read=True, printio=False, print_to_file=True)
                packet_of_bytes = re.sub(b'AT\+FTPGET=2,\d+\r\r\n\+FTPGET: 2,\d+\r\n', b'', packet_of_bytes)
                packet_of_bytes = re.sub(b'\r\nOK\r\n', b'', packet_of_bytes)
                if packet_of_bytes != b'koniec' and packet_of_bytes != b'error':
                    file_bytes = file_bytes + packet_of_bytes
                if packet_of_bytes == b'error':
                    raise Exception("wystapil blad przy pobieraniu danych!")
                number = number + 1
                print(f"numer pobranej paczki {number} - nazwa pliku {self._ftp_get_name_file}")

        except Exception as e:
            print("Niestety - nie udało się pobrać pliku z serwera ftp")
            print(f"{e}")
            traceback.print_exc()
            return b'error'
        logging.debug("koniec ftp - getFile")
        self._reset_bytes_bufor()
        return file_bytes

    def parserFTPEXTGET_file(self):
        try:
            time.sleep(1)
            cmd = f'AT+FTPEXTGET=2,"{self._ftp_get_name_file}"'
            answerAT = self._send_cmd(cmd, return_data=True, t=4)
            time.sleep(2)
            self._status_code = b''
            self._numberOfBytes = b''
            # przykladowa odpowiedz AT  - +FTPEXTGET: 2,204387
            # status_and_number = answerAT.split(b'+')
            print("AHOJ!")
            print(answerAT)
        except Exception as e:
            print(f"wystapil blad w parserFTPEXTGET_file - treść {e}")
            traceback.print_exc()
        logging.debug("koniec parser parserFTPEXTGET_file")

    def postFile(self, APN, server_ip, port, mode, put_name_file, put_path_file,
                 get_name_file, get_path_file,
                 nickname, password, text_to_post):
        self.reset_sim800()
        logging.debug("jestem w postFile")
        self._ftp_server_ip = server_ip
        self._ftp_port = port
        self._ftp_mode = mode
        self._ftp_nickname = nickname
        self._ftp_pass = password
        self._ftp_put_name_file = put_name_file
        self._ftp_get_name_file = get_name_file
        self._ftp_put_path_file = put_path_file
        self._ftp_get_path_file = get_path_file
        self._ftp_text_to_post = text_to_post
        self._APN = APN

        # nadanie IP
        self.czyIpJestNadane_jesliNiePrzydziel()

        try:
            cmd = 'AT'
            self._send_cmd(cmd, return_data=True)
            # inicjalizacja polaczenia FTP
            cmd = 'AT+FTPCID=1'
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPORT=21"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPUTNAME={self._ftp_put_name_file}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPPUTPATH={self._ftp_put_path_file}"
            self._loop_send_cmd(cmd, return_data=True, i_wait_for=b'OK')
            cmd = f"AT+FTPSCONT"
            self._send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()

        # nadanie IP
        self.czyIpJestNadane_jesliNiePrzydziel()

        try:
            cmd = f"AT+FTPPUT=1"
            ftpput_1 = self._loop_send_cmd(cmd, return_data=True, t=3, i_wait_for=b'+FTPPUT: 1,1,1360')  # musimy odczekać do FTP 1,1,1360
            print(f"{ftpput_1}")
            print("text_to_post: ")
            pprint(self._ftp_text_to_post)
            for packet in self._ftp_text_to_post:
                print(packet)

            number = 0
            for packet in self._ftp_text_to_post:
                print("petla while")
                number = number + 1
                print(number)
                cmd = f"AT+FTPPUT=2,{self.utf8len(packet)}"
                self._send_cmd(cmd, return_data=True, t=3)
                print("print pierwsze 1024 bytes")
                self._send_cmd(str(packet), return_data=True, t=3)
            cmd = f"AT+FTPPUT=2,0"
            self._send_cmd(cmd, return_data=True)
        except Exception as e:
            print("Niestety - nie udało się wysłać plik na serwer ftp")
            print(f"{e}")
            traceback.print_exc()
            return b'error'
        logging.debug("koniec post-owania pliku na serwer ftp")
        self._reset_bytes_bufor()