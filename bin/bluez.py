#!/usr/bin/python
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

Bluetooth detection

Implements
==========
Class bluetooth

@author: Sébastien Gallet <sgallet@gmail.com>
@copyright: (C) 2007-2012 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplconnector import Listener
from domogik.xpl.common.plugin import XplPlugin
from domogik_packages.plugin_bluez.lib.bluez import BluezAPI
import traceback

class Bluez(XplPlugin):
    '''
    Manage
    '''
    def __init__(self):
        """
        Create the bluez plugin.
        """
        XplPlugin.__init__(self, name = 'bluez')
        if not self.check_configured():
            self.force_leave()
            return
        devices = self.get_device_list(quit_if_no_device = True)
        devs = {}
        for dev in devices:
            mac = self.get_parameter_for_feature(dev, 'xpl_stats', 'get_availability', 'device') 
            devs[mac] = {'status': 0, 'hyster': 0}

        delay_scan = int(self.get_config("scan-delay"))
        delay_error = int(self.get_config("error-delay"))
        hysteresis = int(self.get_config("hysteresis"))
        self._bluez = BluezAPI(self.log, self.myxpl, self.get_stop(), \
                    devs, delay_scan, \
                    delay_error, hysteresis)
        self.add_stop_cb(self._bluez.stop_adaptator)
        # notify ready
        self.ready()

if __name__ == "__main__":
    Bluez()
