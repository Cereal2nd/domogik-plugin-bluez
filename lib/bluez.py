# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============
Bluetooth detection.

Implements
==========
class BluezAPI

@author: Sébastien Gallet <sgallet@gmail.com>
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import traceback
from domogik.xpl.common.xplmessage import XplMessage
import bluetooth
import threading

class BluezAPI:
    """
    bluez API.
    Encapsulate the access to the bluetooth equipment
    """

    def __init__(self, log, myxpl, stop, devices, delay_scan, delay_error, hysteresis):
        """
        Constructor
        @param log : the logger to use
        @param config : the config to use
        @param myxpl : the xpl sender to use
        @param stop : the stop method of the plugin thread

        """
        self.log = log
        self.myxpl = myxpl
        self._stop = stop

        self._devices = devices
        self._scan_delay = delay_scan
        self._error_delay = delay_error
        self._hysteresis = hysteresis
        
        self.scanThread = threading.Thread(None,
                        self._scan,
                        "scan",
                        (),
                        {})
        self.scanThread.start()
        self.log.info("Bluetooth detector activated.")

    def stop_adaptator(self):
        """
        Stop the thread listening to the bluetooth adaptator.
        """
        self.log.info("Bluetooth detector deactivated.")
        if self.scanThread:
            self.scanThread.join()
        self.scanThread = None

    def _scan(self):
        """
        Encapsulate the call to the callback function.
        Catch exception and test thread stop.
        """
        while not self._stop.isSet():
            self.log.info("Scanning")
            self.log.debug(self._devices)
            try:
                found = bluetooth.discover_devices()
                for dev in self._devices:
                    if dev in found and self._devices[dev]['status'] == 0:
                        # toggle from not seen to seen
                        data = {}
                        data['current'] = 1
                        data['device'] = dev
                        self._send_xpl('sensor.basic', data)
                        self._devices[dev]['hyster'] = 0
                        self._devices[dev]['status'] = 1
                        self.log.info("dev {0} moved from away to seen".format(dev))
                    elif dev not in found and self._devices[dev]['status'] == 0 and self._devices[dev]['hyster'] == self._hysteresis:
                        data = {}
                        data['current'] = 0
                        data['device'] = dev
                        self._send_xpl('sensor.basic', data)
                        self.log.info("dev {0} moved from seen to away".format(dev))
                    elif dev not in found and self._devices[dev]['hyster'] < self._hysteresis:
                        # not seen and previous not seen, but hysteresis not reached
                        self._devices[dev]['hyster'] += 1
                        self._devices[dev]['status'] = 0
                self._stop.wait(self._scan_delay)
            except Exception as exp:
                self.log.info("Error happend waiting for {0} seconds".format(self._error_delay))
                self.log.debug(exp)
                self._stop.wait(self._error_delay)

    def _send_xpl(self, schema, data):
        """ Send xPL message on network
        """
        self.log.info("Sending => schema:%s, data:%s" % (schema, data))
        data['type'] = 'bluez'
        msg = XplMessage()
        msg.set_type("xpl-trig")
        msg.set_schema(schema)
        for key in data:
            msg.add_data({key : data[key]})
        self.myxpl.send(msg)
