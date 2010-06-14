
#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui
import sys
import os
import sqlite3 as sqlite

# this is needed for me to use unpickle objects
sys.path.append(os.path.join(os.getcwd(), 'Generic'))

from Generic.application        import Application
from Interface.cadwindow_mdi    import CadWindowMdi


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    w=CadWindowMdi()
    w.show()
    sys.exit(app.exec_())
    
    