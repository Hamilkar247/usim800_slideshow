import sys
import traceback

from usim800_slideshow.usim800.Communicate_slideshow import communicate_slideshow
import logging
import time


class request_ftp(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_code = None
        self._ftp_server_ip = None
        self._ftp_port = None
        self._ftp_mode = None #0 - aktywny, 1 - pasywny
        self._ftp_nickname = None
        self._ftp_pass = None
        self._ftp_get_name_file = None
        self._ftp_get_path_file = None
        self._ftp_put_name_file = None
        self._ftp_put_path_file = None
        self._ftp_text_to_post = None
        self._sleep_to_read_bytes = None
        self._extensionFile = None
        self._startFileLine= None
        self._png_startFile=b'\x89PNG\r\n'
        self._json_startFile=b'{\n'
        self._APN = None
        self._status_code = None
        self._numberOfBytes = None
        self._IP = None

    def init(self):
        pass

    def utf8len(self, s):
        return len(s.encode('utf-8'))

    def polaczenie_z_siecia_i_nadania_ip(self):
        try:
            return self._bearer(self._APN)
        except Exception as e:
            print(f"przy przydzielaniu IP urządzeniu wystpił błąd {e}")
            return None

    def getFilesMetadata(self, APN, server_ip,
                         port, mode, put_path_file,
                         nickname, password):
        logging.debug("getFilesMetadata")
        self._ftp_server_ip = server_ip
        self._ftp_port = port
        self._ftp_mode = mode
        self._ftp_put_path_file = put_path_file
        self._ftp_nickname = nickname
        self._ftp_pass = password
        self._APN = APN

        #nadanie IP
        self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        if self._IP is None or self._IP == b'':
            return False
        # inicjalizacja polaczenia FTP

        try:
            cmd = 'AT+FTPCID=1'
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPORT=21"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPUTPATH={self._ftp_put_path_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSCONT"  # zapisuje ustawiona konfiguracje
            self._send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()

        try:
            #cmd = f"AT+FTPLIST=2,0"
            #####inicjalizacja pobrania listy metadanych plikow
            cmd = f"AT+FTPLIST=1"
            self._send_cmd(cmd, return_data=True, t=3)
            cmd = f"AT+FTPLIST=2,1024"
            files_metadane=self._send_cmd(cmd, return_data=True, t=1)
            #print(files_metadane)
            return files_metadane
        except Exception as e:
            print(f"przy probie sprawdzanie metadanych plików na serwerze FTP wystąpił błąd ")
            traceback.print_exc()

    def getFile(self, APN, server_ip, port, mode,
                numberOfBytes,
                extension, sleep_to_read_bytes,
                get_name_file, get_path_file, nickname, password):
        logging.debug("jest w getFile")
        self.init()
        self._extensionFile = extension
        self._numberOfBytes = numberOfBytes
        if self._extensionFile == "png":
            self._startFileLine = self._png_startFile
        elif self._extensionFile == "json":
            self._startFileLine = self._json_startFile
        self._sleep_to_read_bytes = sleep_to_read_bytes
        self._ftp_server_ip = server_ip
        self._ftp_port = port
        self._ftp_mode = mode
        self._ftp_nickname = nickname
        self._ftp_pass = password
        self._ftp_get_name_file = get_name_file
        self._ftp_get_path_file = get_path_file
        self._APN = APN

        #nadanie IP
        self._IP = self.polaczenie_z_siecia_i_nadania_ip()
        if self._IP is None or self._IP == b'':
            return False

        # inicjalizacja polaczenia FTP
        try:
            cmd = 'AT+FTPCID=1'
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPORT=21"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPGETNAME={self._ftp_get_name_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPGETPATH={self._ftp_get_path_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSCONT"  #zapisuje ustawiona konfiguracje
            self._send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()

        try:
            cmd = "AT+SAPBR=2,1"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSCONT?"
            self._send_cmd(cmd, return_data=True)
            #cmd = f"AT+FTPQUIT"
            #self._send_cmd(cmd, return_data=True, t=1)
            cmd = f"AT+FTPGET=1"
            ahoj=self._send_cmd(cmd, get_decode_data=False, return_data=True, t=self._sleep_to_read_bytes)
            #print(ahoj)
            #self.parserFTPEXTGET_file()
            cmd = f'AT+FTPGET=2,{self._numberOfBytes}'
            print(f"numberOfBytes: {numberOfBytes} {self._numberOfBytes}")
            self._send_cmd_and_save_answer(cmd, size=self._numberOfBytes,
                                           nameSaveFile=self._ftp_get_name_file, return_data=True,
                                           byte_line_start=self._startFileLine, read=True)
            #cmd = f'AT+FTPGET=3,100'
            #self._send_cmd(cmd, return_data=True)

        except Exception as e:
            print("Niestety - nie udało się pobrać pliku z serwera ftp")
            print(f"{e}")
            return False
        logging.debug("koniec pliku")
        return True

    def parserFTPEXTGET_file(self):
        try:
            time.sleep(1)
            cmd = f'AT+FTPEXTGET=2,"{self._ftp_get_name_file}"'
            answerAT = self._send_cmd(cmd, return_data=True, t=4)
            time.sleep(2)
            self._status_code = b''
            self._numberOfBytes = b''
            #przykladowa odpowiedz AT  - +FTPEXTGET: 2,204387
            #status_and_number = answerAT.split(b'+')
            print("AHOJ!")
            print(answerAT)
        except Exception as e:
            print(f"wystapil blad w parserFTPEXTGET_file - treść {e}")
            traceback.print_exc()
        logging.debug("koniec parser parserFTPEXTGET_file")

    def postFile(self, APN, server_ip, port, mode, put_name_file, put_path_file,
                 get_name_file, get_path_file,
                 nickname, password, text_to_post):
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

        try:
            self._IP = self._bearer(self._APN)
        except Exception as e:
            print(f"przy przydzielaniu IP urządzeniu wystpił błąd {e}")
            #traceback.print_exc()

        try:
        #inicjalizacja polaczenia FTP
            cmd = 'AT+FTPCID=1'
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSERV={self._ftp_server_ip}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPORT=21"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPUN={self._ftp_nickname}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPW={self._ftp_pass}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPUTNAME={self._ftp_put_name_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPPUTPATH={self._ftp_put_path_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPGETNAME={self._ftp_get_name_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPGETPATH={self._ftp_get_path_file}"
            self._send_cmd(cmd, return_data=True)
            cmd = f"AT+FTPSCONT"
            self._send_cmd(cmd, return_data=True)
        except Exception as e:
            print(f"przy podlaczaniu do FTP wystapil blad {e}")
            traceback.print_exc()

        cmd = f"AT+FTPPUT=1"
        ftpput_1=self._send_cmd(cmd, return_data=True, t=3) #musimy odczekać do FTP 1,1,1360

        print("text_to_post: " + self._ftp_text_to_post)
        print(f"{ftpput_1}")
        print(f"rozmiar w bajtach: {self.utf8len(self._ftp_text_to_post)}")
        cmd = f"AT+FTPPUT=2,{self.utf8len(self._ftp_text_to_post)}"
        self._send_cmd(cmd, return_data=True, t=4)
        self._send_cmd(self._ftp_text_to_post, return_data=True)
        cmd = f"AT+FTPPUT=2,0"
        self._send_cmd(cmd, return_data=True)

        #cmd = f"AT+SAPBR=2,1"
        #self._send_cmd(cmd, return_data=True)
        #cmd = f"AT+FTPSCONT?"
        #self._send_cmd(cmd, return_data=True)

        ##### pobierz zawartosc pliku
        #cmd = f"AT+FTPGET=1"
        #self._send_cmd(cmd, return_data=True, t=3)
        #cmd = f"AT+FTPGET=2,1024"
        #self._send_cmd(cmd, return_data=True, t=3)

        ##### ls na plikach na serwerze
        #cmd = f"AT+FTPLIST=1"
        #self._send_cmd(cmd, return_data=True, t=3)
        #cmd = f"AT+FTPLIST=2,1024"
        #self._send_cmd(cmd, return_data=True, t=6)
        #self._send
        #if ftpput_1 == b"+FTPPUT: 1,1,1360":
        #    print(f"{ftpput_1} - oczekuje na przeslanie wiadomosci")
        #else:


