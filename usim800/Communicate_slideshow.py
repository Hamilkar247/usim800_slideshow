import logging


class communicate:
    cmd_list = []

    def __init__(self, port):
        self._port = port

    def _setcmd(self, cmd, end='\r\n'):
        end = '\r\n'
        return (cmd + end)
