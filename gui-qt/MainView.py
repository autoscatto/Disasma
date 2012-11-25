from PyQt4 import QtGui, QtCore, QtWebKit
import sys, os
import resources

os.chdir(os.path.dirname(__file__))
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not path in sys.path:
    sys.path.insert(1, path)
del path

from util import *
from process import *

class ANALyzer(QtCore.QObject):
    contentChanged = QtCore.pyqtSignal()

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process
    
    def setMemoryView(self, vmv):
        self.vmv = vmv

    def show(self):
        process = self.process
        preinizzio = '<!DOCTYPE HTML>\n'
        inizzio = '<html><head>' + \
                  '<link rel="stylesheet" type="text/css" href="style.css"/>\n' + \
                  '</head><body>'
        self.stuff = preinizzio+inizzio
        self.stuff += self.vmv.getHTML()
        self.stuff += '<div class="content">'
        self.stuff += ''.join( \
            '<div class="sect_row" onclick="sv.setAddr(%d)"><div class="section">0x%08x-0x%08x: %s section</div></div><br/>\n' % \
            (r[0], r[0], r[1], s.name) for (r, s) in process.sections.items())
        self.stuff += '</div></body></html>'
        # self.stuff = "<h1>te a me mi puppi la fava</h1>"
        self.contentChanged.emit()

class SectionViewer(QtCore.QObject):
    contentReady = QtCore.pyqtSignal()

    def __init__(self, proc, addr = 0):
        QtCore.QObject.__init__(self)
        self.proc = proc
        self.sect = None
        if addr != 0:
            self.sect = self.proc.sections[addr]

    def setMemoryView(self, vmv):
        self.vmv = vmv

    @QtCore.pyqtSlot(str, int, int)
    def viewAs(self, mode, start, end):
        fragType = fragment.CodeFragment if mode == 'code' else fragment.DataFragment
        self.sect.addFragment(fragType, start, end)        
        self.show()

    @QtCore.pyqtSlot(int)
    def setAddr(self, addr):
        self.sect = self.proc.sections[addr]
        self.show()

    # @QtCore.pyqtSlot(int)
    def show(self):
        out = []
        out.append('<!DOCTYPE HTML>\n')
        out.append('<html>\n')
        out.append('  <head>\n')
        out.append('    <link rel="stylesheet" href="style.css" />\n')
        out.append('  </head>\n')
        out.append('  <body>\n')
        out.append('    <div class="content">\n')
        
        out.append(self.vmv.getHTML())
        out.append(self.sect.getHTML())

        # end content
        out.append('</body>\n')
        out.append('</html>')

        self.stuff = ''.join(out)
        self.contentReady.emit()


class VirtualMemoryView(object):
    def __init__(self, process):
        tmp = []

        self.min = -1
        self.max = -1
        self.sizes = []
        self.pixelWidth = 600.0
        last = -1

        for (interval, section) in process.sections.items():
            # just to avoid elf .strtab and .symtab, clearly it 
            # has to be fixed
            if self.min == -1 and interval[0] > 2000:
                self.min = interval[0]
            self.max = interval[1]

            if last != -1:
                if last != interval[0] and last > 2000:
                    tmp.append(('gap', interval[0]-last, interval[0]))

            last = interval[1]

            if interval[0] > 2000:
                tmp.append((section.name, interval[1]-interval[0], interval[0]))

        rangetot = self.max-self.min
        for (name, size, start) in tmp:
            self.sizes.append((name, int((float(size)/float(rangetot))*self.pixelWidth), start))

    def getHTML(self):
        ret = ''
        colors = { \
            'data' : '#3333bb', \
            'text' : '#bb3333', \
            'gap'  : '#111111'  \
        }

        i = 0
        ret += '<div id="virtual-memory">\n'
        for (name, size, start) in self.sizes:
            onclick = "sv.setAddr(%d)" % start
            if name == '.text' or ('__TEXT' in name):
                x = 'text'
            elif name == 'gap':
                x = 'gap'
                onclick = ""
            else:
                x = 'data'

            ret += '<div onclick="%s" class="vmview" style="background-color: %s; width: %spx;"></div>\n' % \
                    (onclick, colors[x], size)
            i += 1
        ret += '</div>\n'
        ret += '<div style="height: 50px; display: block; clear: both"></div>\n'
        return ret


class MainView(QtGui.QMainWindow):
    def __init__(self):
        super(MainView, self).__init__()
        self.initUI()

    def showLoading(self):
        self.webView.setHtml('<h1>Loading...</h1>', QtCore.QUrl('qrc:/'))

    def showHtml(self):
        stuff = self.anal.stuff
        self.webView.setHtml(stuff, QtCore.QUrl('qrc:/'))
        self.webView.page().mainFrame().addToJavaScriptWindowObject("sv", self.sectView)

    def showView(self):
        stuff = self.sectView.stuff
        self.webView.setHtml(stuff, QtCore.QUrl('qrc:/'))
        self.webView.page().mainFrame().addToJavaScriptWindowObject("sv", self.sectView)

    def showBackground(self):
        self.webView.setHtml('<html><head><link rel="stylesheet" href="style.css"/></head><body></body></html>', \
            QtCore.QUrl('qrc:/'))

    def viewSections(self):
        self.anal.show()

    def openStuff(self):
        fileName = QtGui.QFileDialog.getOpenFileName( \
            self, 'Open File', '', 'Files (*)')

        if fileName:
            self.showLoading()

            self.process = loader.SPUTA_FUORI_IL_MOSTO(fileName)
            self.virtualMemoryView = VirtualMemoryView(self.process)

            self.anal = ANALyzer(self.process)
            self.anal.setMemoryView(self.virtualMemoryView)
            self.anal.contentChanged.connect(self.showHtml)

            self.sectView = SectionViewer(self.process)
            self.sectView.setMemoryView(self.virtualMemoryView)
            self.sectView.contentReady.connect(self.showView)

            self.viewSections()

    def cpuStatus(self):
        if self.cpustatus.isHidden():
            self.cpustatus.show()
        else:
            self.cpustatus.hide()

    def _actions(self):
        ret = [ \
            ('Open', ':icons/open.png', 'Ctrl+O', self.openStuff), \
            (None, None, None, None), \
            ('View Sections', ':icons/sections.png', 'Ctrl+Alt+S', self.viewSections), \
            ('View CPU status', ':icons/cpu.png', 'Ctrl+Q', self.cpuStatus) \
        ]

        return ret

    def _setupToolbar(self, toolbar):
        alist = self._actions()
        for (name, icon, shortcut, triggered) in alist:
            if name == None:
                toolbar.addSeparator()
            else:
                a = QtGui.QAction(QtGui.QIcon(icon), name, self)
                a.setShortcut(shortcut)
                a.triggered.connect(triggered)
                toolbar.addAction(a)

    def initUI(self):
        self.toolbar = self.addToolBar('Stuff')
        self._setupToolbar(self.toolbar)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QTDisassa!')
        #self.showMaximized()

        self.webView = QtWebKit.QWebView(self)
        self.setCentralWidget(self.webView)

        self.cpustatus = QtGui.QDockWidget("CPU Status", self)
        self.cpustatus.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.cpustatus)
        self.cpustatus.hide()

        self.showBackground()
        self.show()

def main():

    app = QtGui.QApplication(sys.argv)
    mainView = MainView()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()