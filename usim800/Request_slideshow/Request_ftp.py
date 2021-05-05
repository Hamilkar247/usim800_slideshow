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
        self._APN = None

    def init(self):
        pass

    def utf8len(self, s):
        return len(s.encode('utf-8'))

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


