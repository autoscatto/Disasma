from PyQt4 import QtGui, QtCore, QtWebKit
import sys, os
import resources

os.chdir(os.path.dirname(__file__))
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if not path in sys.path:
    sys.path.insert(1, path)
del path

from util import *

class MainSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        format = QtGui.QTextCharFormat()
        format.setForeground(QtCore.Qt.darkMagenta)

        pattern = "(eax|ax|ah|al|ebx|bx|bh|bl|ecx|cx|ch|cl|edx|dx|dh|dl|"
        pattern += "esp|sp|ebp|bp|esi|si|edi|di|cs|ds|ss|es|fs|gs|rax|rbx|"
        pattern += "rcx|rdx|rsi|rdi|rbp|rsp|rflags|rip)"

        re = QtCore.QRegExp(pattern)
        index = re.indexIn(text, 0)
        while index >= 0:
            length = re.matchedLength()
            self.setFormat(index, length, format)
            index = re.indexIn(text, index+length)

        format.setForeground(QtCore.Qt.blue)
        pattern = '([0-9a-fA-F]{8})'# ([^ ]*) +'

        re = QtCore.QRegExp(pattern)
        index = re.indexIn(text, 0)
        while index >= 0:
            #index =
            length = re.matchedLength()
            self.setFormat(index, length, format)
            index = re.indexIn(text, index+length)

        format.setForeground(QtCore.Qt.darkGreen)
        pattern = 'Section.*:'

        re = QtCore.QRegExp(pattern)
        index = re.indexIn(text, 0)
        while index >= 0:
            length = re.matchedLength()
            self.setFormat(index, length, format)
            index = re.indexIn(text, index+length)

'''
class TextWidget(QtGui.QTextEdit):
    def __init__(self, mainWindow):
        super(TextWidget, self).__init__(mainWindow)
        self.setFont(QtGui.QFont('Courier', 9))

    def printRaw(self, toPrint):
        self.setPlainText(toPrint)
'''
import threading
class ANALyzer(QtCore.QThread):
    contentChanged = QtCore.pyqtSignal()

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process

    def run(self):
        process = self.process
        self.stuff = '<html><head><link rel="stylesheet" href="style.css" type="text/css" /></head><body>'
        self.stuff += '<div class="content">'
        self.stuff += ''.join( \
            '<div class="sect_row" onclick="sv.show(%d)"><div class="section">0x%08x-0x%08x: %s section</div></div><br/>' % \
            (r[0], r[0], r[1], s.name) for (r, s) in process.sections.items())
        self.stuff += '</div></body></html>'
        # self.stuff = "<h1>te a me mi puppi la fava</h1>"
        self.contentChanged.emit()

class SectionViewer(QtCore.QObject):
    contentReady = QtCore.pyqtSignal()

    def __init__(self, proc):
        QtCore.QObject.__init__(self)
        self.proc = proc

    @QtCore.pyqtSlot(int)
    def show(self, addr):
        self.stuff = self.proc.sections[addr].getHTML()
        self.contentReady.emit()

class MainView(QtGui.QMainWindow):
    def __init__(self):
        super(MainView, self).__init__()
        self.initUI()

    def showLoading(self):
        self.webView.setHtml('<h1>Loading...</h1>', QtCore.QUrl('qrc:/'))

    def showHtml(self):
        stuff = self.anal.stuff
        self.webView.setHtml(stuff, QtCore.QUrl('qrc:/'))
        self.webView.page().mainFrame().addToJavaScriptWindowObject("sv", self.sectView);

    def showView(self):
        stuff = self.sectView.stuff
        self.webView.setHtml(stuff, QtCore.QUrl('qrc:/'))

    def openStuff(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', '', 'Files (*)')
        #toPrint = loader.SPUTA_FUORI_IL_ROSPO(fileName)
        #self.textWidget.printRaw(toPrint)

        self.showLoading()

        self.process = loader.SPUTA_FUORI_IL_MOSTO(fileName)

        self.anal = ANALyzer(self.process)
        self.anal.contentChanged.connect(self.showHtml)
        self.anal.start()

        self.sectView = SectionViewer(self.process)
        self.sectView.contentReady.connect(self.showView)

        #html = loader.SPUTA_FUORI_IL_BOSCO(fileName)
        #self.webView.setHtml(html, QtCore.QUrl('qrc:/'))

    def initUI(self):
        openAction = QtGui.QAction(\
            QtGui.QIcon(':icons/open.png'), 'Open', self)

        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openStuff)

        self.toolbar = self.addToolBar('Stuff')
        self.toolbar.addAction(openAction)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QTDisassa!')
        self.show()
        #self.showMaximized()

        self.webView = QtWebKit.QWebView(self)
        self.setCentralWidget(self.webView)

def main():

    app = QtGui.QApplication(sys.argv)
    mainView = MainView()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()