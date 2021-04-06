from usim800.Communicate_slideshow import communicate_slideshow
import logging


class request_slideshow(communicate_slideshow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status_code = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None

    def init(self):
        self._status_code = None
        self._json = None
        self._text = None
        self._content = None
        self._url = None
        self._IP = None
