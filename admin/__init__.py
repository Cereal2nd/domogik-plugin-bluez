# -*- coding: utf-8 -*-

### common imports
from flask import Blueprint, abort
from domogik.common.utils import get_packages_directory
from domogik.admin.application import render_template
from domogik.admin.views.clients import get_client_detail
from jinja2 import TemplateNotFound

### package specific imports
import subprocess



### package specific functions
def list_bt_devices():
    try:
	bt = subprocess.Popen(["hcitool", "scan"], stdout=subprocess.PIPE)
        output = bt.communicate()[0]
        if isinstance(bt, str):
            output = unicode(output, 'utf-8')
        return output
    except:
	output = unicode('Error with BT detection', 'utf-8')



### common tasks
package = "plugin_bluez"
template_dir = "{0}/{1}/admin/templates".format(get_packages_directory(), package)
static_dir = "{0}/{1}/admin/static".format(get_packages_directory(), package)

plugin_bluez_adm = Blueprint(package, __name__,
                        template_folder = template_dir,
                        static_folder = static_dir)

@plugin_bluez_adm.route('/<client_id>')
def index(client_id):
    detail = get_client_detail(client_id)
    try:
        return render_template('plugin_bluez.html',
            clientid = client_id,
            client_detail = detail,
            mactive="clients",
            active = 'advanced',
            bt = list_bt_devices())

    except TemplateNotFound:
        abort(404)

