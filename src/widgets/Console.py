import os
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QProcess
from widgets.Editor import Editor
from widgets.Messagebox import MessageBox


class Console(QWidget):
    errorSignal = pyqtSignal(str)
    outputSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.pressed = False
        self.font = QFont()
        self.dialog = MessageBox(self)
        # self.font.setFamily(editor["editorFont"])
        self.font.setFamily("Iosevka")
        self.font.setPointSize(12)
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        self.output = None
        self.setFocusPolicy(Qt.StrongFocus)
        self.error = None
        self.finished = False
        self.clicked = False

        self.process = QProcess()
        self.state = None
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.add()  # Add items to the layout

    def ispressed(self):
        return self.pressed

    def added(self):
        self.pressed = True

    def remove(self):
        self.parent.hideFileExecuter()
        self.clicked = True

    def hideTerminalClicked(self):
        return self.clicked

    def onReadyReadStandardError(self):
        try:
            self.error = self.process.readAllStandardError().data().decode()

            self.editor.appendPlainText(self.error)

            self.errorSignal.emit(self.error)
            if self.error == "":
                pass
            else:
                self.error = self.error.split(os.linesep)[-2]
                self.dialog.helpword = str(self.error)
                self.dialog.getHelp(self.parent.parent)
        except IndexError as E:
            print(E, " on line 70 in the file Console.py")

    def onReadyReadStandardOutput(self):
        try:
            self.result = self.process.readAllStandardOutput().data().decode()
        except UnicodeDecodeError as E:
            print(E, " on line 76 in the file Console.py")
        try:
            self.editor.appendPlainText(self.result.strip("\n"))
            self.state = self.process.state()
        except RuntimeError:
            pass

        self.outputSignal.emit(self.result)

    def ifFinished(self, exitCode, exitStatus):
        self.finished = True

    def add(self):
        """Executes a system command."""
        # clear previous text
        self.added()
        self.button = QPushButton("Hide terminal")
        self.button.setFont(QFont("Iosevka", 11))
        self.button.setStyleSheet("""
                height: 20;
                background-color: #212121;

                """)
        self.terminateButton = QPushButton("   Stop")
        self.terminateButton.setIcon(QIcon("resources/square.png"))
        self.terminateButton.setFont(QFont("Iosevka", 11))
        self.terminateButton.clicked.connect(self.terminate)
        self.button.setFixedWidth(120)
        self.h_layout = QHBoxLayout()
        self.editor = Editor(self)
        self.editor.setReadOnly(True)
        self.editor.setFont(self.font)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.terminateButton)
        self.button.clicked.connect(self.remove)

    def run(self, command, path):  # Takes in the command and the path of the file
        os.chdir(os.path.dirname(path))  # We need to change the path to the path where the file is being ran from
        self.editor.clear()
        if self.process.state() == 1 or self.process.state() == 2:
            self.process.kill()
            self.editor.setPlainText("Process already started, terminating")
        else:
            self.process.start(command)

    def terminate(self):
        if self.process.state() == 2:
            self.process.kill()
