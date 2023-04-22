# -*- coding:utf-8 -*-
"""
SiTCP RBCP pseudo server

Copyright (c) 2018, Bee Beans Technologies Co.,Ltd.
"""


from __future__ import print_function

import argparse
from contextlib import closing
import copy
from logging import getLogger, StreamHandler, INFO
import os
import select
import socket
import struct
import threading
import time
import traceback

from sitcpy import to_bytearray
import sitcpy
from sitcpy.cui import DataHandler, SessionThread, CuiServer, CommandHandler

LOGGER = getLogger(__name__)
HANDLER = StreamHandler()
HANDLER.setLevel(INFO)
LOGGER.setLevel(INFO)
LOGGER.addHandler(HANDLER)

class DataGenerator(DataHandler):
    """
    Data Generator for pseudo SiTCP device.
    SessionThreadGen(send created data to the session.)
        <---(inclusion relation)<--DataGenerator(create generation data)
    """

    def __init__(self):
        """
        Data Handler for binary(byte object)
        """
        super(DataGenerator, self).__init__()

        self._data_unit = 8
        self._count = 0
        self._data_unit_count = 2  # burst data_unit counts to generate
        self._locafile_index = 0
        self._local_file_path='./localfiles'
        self._locafile_list=[]
        self._packages=[]
        if os.path.exists(self._local_file_path):
            self._locafile_list = os.listdir(self._local_file_path)
            for file in self._locafile_list:
                fileName = self._local_file_path+'/'+file
                with open(fileName,'rb') as f_read:
                    for line in f_read.readlines():
                        self._packages.append(line.strip())
        print(str(len(self._locafile_list))+' local files found from '+self._local_file_path)
        print(str(len(self._packages))+' packages in total')
       
    def on_start(self, session):
        """
        Ignore send prompt
        """
        pass

    def on_data(self, session, byte_data):
        """
        Ignore received data
        """
        pass

    @property
    def data_unit_count(self):
        """
        This property is referenced from the SessionThreadGen class.
        The SessionThread class calls create_data (data_unit_count) with the return value.
        When data_unit_count is increased, burst data from this emulator is generated.
        Specify a multiple of data_unit. When data_unit = 8 and data_unit_count = 2 is returned,
        16 bytes of data are burst transferred.

        :rtype: int
        :return: data_unit_count of create_data.
        """
        return self._data_unit_count

    @data_unit_count.setter
    def data_unit_count(self, val):
        """
        Set the data_unit_count parameter. See data_unit_count property for details.

        :type val: int
        """
        self._data_unit_count = val

    def create_data(self, data_unit_count):
        """
        Create unit data

        :rtype: bytearray
        """
        data = bytearray(self._data_unit * data_unit_count)
        # print("DEBUG:create data count %d size %d" %
        #       (data_unit_count, self._data_unit * data_unit_count))
        for data_unit in range(0, data_unit_count - 1):
            count_bytes = struct.pack(">L", self._count)
            data[self._data_unit * data_unit] = 0xa5  # struct.pack("B", 0xa5)
            index = self._data_unit * data_unit + 4
            for count_byte in count_bytes:
                data[index] = count_byte
                index += 1
            self._count += 1
            if self._count == 0xffffffff:
                self._count = 0
        return data

    def create_data_gauss(self, data_unit_count):
        data = bytearray(self._data_unit * data_unit_count)
        for data_unit in range(0, data_unit_count - 1):
            count_bytes = struct.pack(">L", self._count)
            data[self._data_unit * data_unit] = 0xa5
            index = self._data_unit * data_unit + 4
            for count_byte in count_bytes:
                data[index] = count_byte
                index += 1
            self._count += 1
            if self._count == 0xffffffff:
                self._count = 0
        return data

    def read_local_data(self,data_unit_count):
        if len(self._locafile_list) == 0:
            return self.create_data(data_unit_count)

        data = self._packages[self._locafile_index]
        self._locafile_index += 1
        if(self._locafile_index >= len(self._packages)):
            self._locafile_index =0
        return data

class SessionThreadGen(SessionThread):

    def __init__(self, server, data_generator, sock, client_address, max_buff=1024 * 1024):

        super(SessionThreadGen, self).__init__(server, data_generator, sock, client_address, max_buff)

    def run(self):

        try:
            print("starting session from client " + str(self._client_address))
            self._data_handler.on_start(self)
            # self._sock.setblocking(False)
            sock_list = [self._sock]
            self._state.transit(sitcpy.THREAD_RUNNING)
            while self._state() == sitcpy.THREAD_RUNNING:
                data_count = self._data_handler.data_unit_count
                try:
                    readable, writable, _ = select.select(sock_list, sock_list, [], 0.1)
                    for sock in writable:
                        sock.send(self._data_handler.read_local_data(data_count))
                        time.sleep(0.1)
                    for sock in readable:
                        msg = sock.recv(1024)
                        hex_data = ''.join(['{:02x}'.format(b) for b in msg])
                        print("device received :", hex_data)

                except (OSError, socket.error) as exc:
                    LOGGER.debug("Exception at SessionThreadGen.run : %s" %
                                 str(exc))
                    LOGGER.debug("Pseudo Data Session Closed")
                    break

            self._state.transit(sitcpy.THREAD_STOPPING)
            del sock_list[:]
            self.close()
        finally:
            self._state.transit(sitcpy.THREAD_STOPPED)
