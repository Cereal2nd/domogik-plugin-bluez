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

    def __init__(self, log, myxpl, stop, devices, delay_sensor, delay_stat, delay_scan, delay_error, hysteresis):
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
        self._delay_sensor = delay_sensor
        self._delay_stat = delay_stat
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
            print self._devices
            print bluetooth.discover_devices()
            self._stop.wait(30)

    def basic_listener(self, message):
        """
        Listen to bluez.basic messages.
        @param message : The XPL message received.

        bluez.basic
           {
            action=start|stop|status
            device=<name of the bluez plugin "instance">
            ...
           }
        """
        self.log.debug("basic_listener : Start ...")
        actions = {
            'stop': lambda x, d, m: self._action_stop(x, d),
            'start': lambda x, d, m: self._action_start(x, d),
            'status': lambda x, d, m: self._action_status(x, d),
        }
        device = None
        if 'device' in message.data:
            device = message.data['device']
        if device != None and device == self._device_name:
            try:
                action = None
                if 'action' in message.data:
                    action = message.data['action']
                self.log.debug("basic_listener : action %s received for device %s" % (action, device))
                actions[action](self.myxpl, device, message)
            except:
                self.log.error("action _ %s _ unknown." % (action))
                error = "Exception : %s" %  \
                         (traceback.format_exc())
                self.log.debug("basic_listener : "+error)
        else:
            self.log.warning("basic_listener : action %s received for unknown device %s" % (action, device))

    def _action_status(self, myxpl, device):
        """
        Status of the bluez plugin.
        @param myxpl : The xpl sender to use.
        @param device : The "plugin" device.

        timer.basic
           {
            action=status
            ...
           }
        """
        self.log.debug("action_status : Start ...")
        mess = XplMessage()
        mess.set_type("xpl-trig")
        mess.set_schema("bluez.basic")
        mess.add_data({"device" : device})
        mess.add_data({"status" : self._state})
        myxpl.send(mess)
        self.log.debug("action_status : Done :)")

    def _action_stop(self, myxpl, device):
        """
        Stop the bluetooth detection
        @param myxpl : The xpl sender to use.
        @param device : The "plugin" device.
        """
        self.log.debug("_action_stop : Start ...")
        self.stop_adaptator()
        mess = XplMessage()
        mess.set_type("xpl-trig")
        mess.set_schema("bluez.basic")
        mess.add_data({"device" : device})
        mess.add_data({"status" : self._state})
        myxpl.send(mess)
        self.log.debug("_action_stop : Done :)")

    def _action_start(self, myxpl, device):
        """
        Start the bluetooth detection
        @param myxpl : The xpl sender to use.
        @param device : The "plugin" device.
        """
        self.log.debug("_action_start : Start ...")
        self.start_adaptator()
        mess = XplMessage()
        mess.set_type("xpl-trig")
        mess.set_schema("bluez.basic")
        mess.add_data({"device" : device})
        mess.add_data({"status" : self._state})
        myxpl.send(mess)
        self.log.debug("_action_start : Done :)")

    def _trig_detect(self, xpltype, addr, status):
        """
        Send a message with the status of the "phone" device.
        @param xpltype : The xpltype of the message to send.
        @param addr : the mac address of the bluetooth device.
        @param status : the status of the bluetooth device.
        """
        self.log.debug("_trig_detect : Start ...")
        self._targets[addr]["status"] = status
        mess = XplMessage()
        mess.set_type(xpltype)
        mess.set_schema("sensor.basic")
        mess.add_data({"bluez" : self._device_name})
        mess.add_data({"device" : self._targets[addr]["name"]})
        mess.add_data({"type" :  "ping"})
        mess.add_data({"current" : status})
        self.myxpl.send(mess)
        self.log.debug("_trig_detect : Done :)")

