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

class MainView(QtGui.QMainWindow):

    def __init__(self):
        super(MainView, self).__init__()
        self.initUI()

    def openStuff(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', '', 'Files (*.*)')
        #toPrint = loader.SPUTA_FUORI_IL_ROSPO(fileName)
        #self.textWidget.printRaw(toPrint)
        html = loader.SPUTA_FUORI_IL_BOSCO(fileName)        
        self.webView.setHtml(html, QtCore.QUrl('qrc:/'))

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
        
        self.webView = QtWebKit.QWebView(self)
        self.setCentralWidget(self.webView)

def main():
    
    app = QtGui.QApplication(sys.argv)
    mainView = MainView()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()