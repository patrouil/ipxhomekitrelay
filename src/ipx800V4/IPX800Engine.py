import re
# using theading locks (not async).
import threading
import queue

import logging
import time
import http.client
import json


class IPX800Engine:
    DEFAULT_INTERVAL = 250  # milisec between HTTP call.

    """ ipx  singleton """
    _instance = None

    _family_patterns = {
        re.compile(r"^THL.*"): 'XTHL',
        re.compile(r"^ENO.*"): 'XENO',
        re.compile(r"^VR.*"): 'VR',
        re.compile(r"^C\d"): 'C',
        re.compile(r"^R\d"): 'R',
        re.compile(r"^VI\d"): 'VI',
        re.compile(r'^VO\d'): 'VO',
        re.compile(r'^D\d'): 'D',
        re.compile(r'^A\d'): 'A',
        re.compile(r'^VA\d'): 'VA',
        re.compile(r'^PW\d'): 'PW'
    }

    def __init__(self):
        if not self._is_ready:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.apiKey = None
            self.port = None
            self.host = None
            self.reader = None
            self.writer = None
            self.cmd_queue = None
            self._queryInterval = IPX800Engine.DEFAULT_INTERVAL
            self._observers = None  # { ID : []  } list of methods by device codes
            self.values = {}
            # list of a devices familly to request to the IPX exp : 'R', 'V0', 'THL' ...
            self.entryCodes = []
            # a cache dict to make a correspondance to a device code to its familly.
            # cache used to avoid regex execution.
            self.device_to_familly = {}
            self.cmd_queue = queue.LifoQueue(maxsize=50)
            # a locker to access the above paramters.
            self.values_lock = threading.Lock()
        # end
        self._is_ready = True  # to avoid multiples init.

    # end

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_ready = False
        # end if
        return cls._instance

    # end singleton

    @property
    def is_running(self) -> bool:
        return self.reader is not None

    # end isRunning

    def _notify_value_change(self, new_dict: dict, old_dict: dict) -> None:
        for acc in self._observers:
            for k in acc.listenedDevices():
                newval = new_dict.get(k, None)
                oldval = old_dict.get(k, None)
                if (newval is not None) and (newval != oldval):
                    acc.valueChangedListener(k, newval, oldval)
                # end if
            # end for
        # end for

    # end

    def _notify_status_change(self) -> None:
        for l in self._observers:
            l.ipxStatusChangedListener(self.is_running)
        # end for

    # end

    @staticmethod
    def _read_ipx() -> None:
        ipx = IPX800Engine()
        for familly in ipx.entryCodes:
            time.sleep(ipx._queryInterval / 1000)  # wait a delay between HTTP calls. DO not overload IPX.
            u = '/api/xdevices.json?key=' + ipx.apiKey + '&Get=' + familly
            try:
                httpClient = http.client.HTTPConnection(ipx.host, ipx.port, timeout=3)
                # here should not be none otherwise an exception is raised
                assert (httpClient is not None)
                httpClient.request('GET', u)
                resp = httpClient.getresponse()
                if resp.status == 200:
                    body = resp.read()
                    new_dict = json.loads(body)
                    ipx._notify_value_change(new_dict, ipx.values)
                    with ipx.values_lock:
                        ipx.values = ipx.values | new_dict  # merge values.
                    # logger.debug(body)
                else:
                    ipx.logger.error("_read_ipx : %d : %s", resp.status, resp.reason)
                # end if
                resp.close()
                httpClient.close()
            except http.client.HTTPException as err:
                # @TODO detect client loss then reset httpClient value
                ipx.logger.error("_read_ipx : an http error occurred : %s", err)
            except Exception as ex:
                ipx.logger.error("_read_ipx : a generic error occurred %s", ex)
        # end for

    # end _read_ipx

    @staticmethod
    def _write_cmd() -> None:
        ipx = IPX800Engine()
        while ipx.is_running:
            try:
                c = ipx.cmd_queue.get(timeout=5)
                u = '/api/xdevices.json?key=' + ipx.apiKey + '&' + c
                ipx.logger.debug('_write_cmd: %s', u)
                httpClient = http.client.HTTPConnection(ipx.host, ipx.port, timeout=3)
                # here should not be none otherwise an exception is raised
                assert (httpClient is not None)
                httpClient.request('GET', u)
                resp = httpClient.getresponse()
                if resp.status == 200:
                    body = resp.read()
                    statusMsg = json.loads(body)
                    if statusMsg.get('status') != 'Success':
                        ipx.logger.error("_write_cmd : command %s is invalid check configuration", c)

                # logger.debug(body)
                else:
                    ipx.logger.error("_write_cmd : %d : %s", resp.status, resp.reason)
                # end if  # add a setting queue to avoid multiple HTTP request  # end for
                resp.close()
                httpClient.close()
                ipx.cmd_queue.task_done()

            except http.client.HTTPException as _:
                # @TODO detect client loss then reset httpClient value
                ipx.logger.error("_write_cmd : an http error occurred")
            except queue.Empty as _:
                ipx.logger.debug("_write_cmd : empty command queue")
            except Exception as e:
                ipx.logger.error("_write_cmd : a generic error occurred : %s", e)

        # end while
        pass

    # end write cmd

    @staticmethod
    def reader_loop() -> None:
        ipx = IPX800Engine()
        ipx.logger.info("start of IPX reader")
        while ipx.is_running:
            ipx.logger.debug("reading IPX ...")
            # reset dict values
            ipx._read_ipx()
            ipx.logger.debug("values are %d", len(ipx.values))
        # end while
        ipx.logger.info("end of IPX reader")

    # end readerLoop

    @staticmethod
    def writer_loop() -> None:
        ipx = IPX800Engine()
        ipx.logger.info("start of IPX writer")
        ipx._write_cmd()
        ipx.logger.info("end of IPX writer")

    # end write loop

    @staticmethod
    def dummy_loop() -> None:
        ipx = IPX800Engine()

        while IPX800Engine().is_running:
            time.sleep(ipx._queryInterval)

            IPX800Engine.values = {"R01": 1}
        # end while
        ipx.logger.info("end of IPX reader")

    # end readerLoop

    def _enable_accessories(self):
        for a in self._observers:
            a.setCommandCallback(self.push_command)
            a.ipxStatusChangedListener(self.is_running)
            # at the end put in read list
            for d in a.listenedDevices():
                self._add_entry_code(d)
        # end for

    # e,nd

    def _add_entry_code(self, device_name: str) -> None:
        if self.device_to_familly.get(device_name) is not None:
            # already in list
            return

        for (k, v) in self._family_patterns.items():
            m = k.match(device_name)
            if m is None:
                continue
            with self.values_lock:
                self.entryCodes.append(v)
                self.device_to_familly[device_name] = v
            return  # end with
        # end for
        self.logger.error("add_entry_code: %s is an invalid device", device_name)

    # end method

    def start(self, host=None, port=None, apiKey=None, interval=DEFAULT_INTERVAL) -> None:
        self.host = host
        self.port = port
        self.apiKey = apiKey

        IPX800Engine._queryInterval = interval
        self._enable_accessories()

        self.reader = threading.Thread(target=self.reader_loop)
        self.reader.start()
        self.writer = threading.Thread(target=self.writer_loop)
        self.writer.start()

        self._notify_status_change()

    # end

    def stop(self) -> None:
        r = self.reader
        self.reader = None
        r.join()
        r = self.writer
        self.writer = None
        r.join()

    # end

    def is_available(self) -> bool:
        with self.values_lock:
            v = (self.values is not None) and (self.values.get('status', None) == 'Success')
        return v

    @staticmethod
    def push_command(cmd: str) -> None:
        IPX800Engine().cmd_queue.put(cmd)

    # end push

    '''
    method be be called once before starting the IPX Interface.
    reset observers list.
    '''

    def register_accessory(self, ipx_acc_set: []) -> None:
        self._observers = ipx_acc_set
    # end

# end of class
