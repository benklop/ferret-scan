# -*- coding: utf-8 -*-
# This file is part of the Horus Project

from __future__ import absolute_import
__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import threading

from ferret import Singleton
from ferret.util import profile
from ferret.engine.driver.board import Board
from ferret.engine.driver.camera_usb import Camera_usb

import logging
logger = logging.getLogger(__name__)

@Singleton
class Driver(object):

    """Driver class. For managing scanner hw"""

    def __init__(self):
        self.board = Board(self)
        self.camera = self._create_camera()
        self.is_connected = False
        self.unplugged = False

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._after_callback = None

    def _create_camera(self):
        mode = profile.settings.get('scanner_mode', 'Ciclop laser')
        if mode == 'Ferret structured light':
            from ferret.engine.driver.camera_ferret import Camera_ferret
            return Camera_ferret(self)
        return Camera_usb(self)

    def _is_ferret(self):
        return profile.settings.get('scanner_mode', 'Ciclop laser') == 'Ferret structured light'

    def connect(self):
        self.__init__()
        if self._before_callback is not None:
            self._before_callback()
        threading.Thread(target=self._connect).start()

    def _connect(self):
        exception = None
        self.is_connected = False
        try:
            self.camera.connect()
            if self._is_ferret() and profile.settings.get('ferret_turntable_optional', True):
                try:
                    self.board.connect()
                except Exception as board_err:
                    logger.warning('Turntable board not connected: {0}'.format(board_err))
            else:
                self.board.connect()
        except Exception as e:
            exception = e
            logger.error('Failed to connect: '+ str(e))
        else:
            self.is_connected = True
        finally:
            if exception is None:
                self.unplugged = False
                response = (True, self.is_connected)
            else:
                response = (False, exception)
                self.disconnect()
            if self._after_callback is not None:
                self._after_callback(response)

    def disconnect(self):
        self.is_connected = False
        self.camera.disconnect()
        self.board.disconnect()

    def set_callbacks(self, before, after):
        self._before_callback = before
        self._after_callback = after


driver = Driver()
