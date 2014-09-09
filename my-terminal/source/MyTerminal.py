#!/usr/bin/env python

import os
import sys

ORIGCWD = os.getcwd()

# Check we have simple basics like Gtk+ and a valid $DISPLAY
try:
    import pygtk
    pygtk.require ("2.0")
    # pylint: disable-msg=W0611
    import gtk, pango, gobject

    if gtk.gdk.display_get_default() == None:
        print('You need to run terminator in an X environment. ' \
              'Make sure $DISPLAY is properly set')
        sys.exit(1)

except ImportError:
    print('You need to install the python bindings for ' \
           'gobject, gtk and pango to run Terminator.')
    sys.exit(1)

import terminatorlib.optionparse
from terminatorlib.terminator import Terminator
from terminatorlib.factory import Factory
from terminatorlib.version import APP_NAME, APP_VERSION
from terminatorlib.util import dbg, err

if __name__ == '__main__':
    dbus_service = None

    dbg ("%s starting up, version %s" % (APP_NAME, APP_VERSION))
  
    OPTIONS = terminatorlib.optionparse.parse_options()

    # Attempt to import our dbus server. If one exists already we will just
    # connect to that and ask for a new window. If not, we will create one and
    # continue. Failure to import dbus, or the global config option "dbus"
    # being False will cause us to continue without the dbus server and open a
    # window.
    try:
        if OPTIONS.nodbus:
            dbg('dbus disabled by command line')
            raise ImportError
        from terminatorlib import ipc
        try:
            dbus_service = ipc.DBusService()
        except ipc.DBusException:
            dbg('Unable to become master process, requesting a new window')
            ipc.new_window(OPTIONS.layout)
            sys.exit()
    except ImportError:
        dbg('dbus not imported')
        pass

    MAKER = Factory()
    TERMINATOR = Terminator()
    TERMINATOR.set_origcwd(ORIGCWD)
    TERMINATOR.set_dbus_data(dbus_service)
    TERMINATOR.reconfigure()
    try:
        dbg('Creating a terminal with layout: %s' % OPTIONS.layout)
        TERMINATOR.create_layout(OPTIONS.layout)
    except (KeyError,ValueError), ex:
        err('layout creation failed, creating a window ("%s")' % ex)
        TERMINATOR.new_window()
    TERMINATOR.layout_done()

    if OPTIONS.debug > 2:
        import terminatorlib.debugserver as debugserver
        # pylint: disable-msg=W0611
        import threading

        gtk.gdk.threads_init()
        (DEBUGTHREAD, DEBUGSVR) = debugserver.spawn(locals())
        TERMINATOR.debug_address = DEBUGSVR.server_address

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

