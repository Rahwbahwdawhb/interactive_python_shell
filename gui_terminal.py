from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QLineEdit, QLabel, QPlainTextEdit
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets


class PlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.prompt_history=[]
        self.prompt_display_counter=0
        self.indent='  '
    def keyPressEvent(self, event):
        super(PlainTextEdit, self).keyPressEvent(event)
        self.additionalKeyPressEvent(event)
    def additionalKeyPressEvent(self,event):
        if QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
            if event.key()==Qt.Key.Key_Return:
                current_prompt=self.toPlainText()
                self.prompt_history.append(current_prompt)
                self.prompt_display_counter=0
                self.setPlainText('')
            elif self.prompt_history and event.key()==Qt.Key.Key_Up:
                if abs(self.prompt_display_counter-1)<=len(self.prompt_history):
                    self.prompt_display_counter-=1
                self.set_new_prompt(self.prompt_history[self.prompt_display_counter])
            elif self.prompt_history and event.key()==Qt.Key.Key_Down:
                if self.prompt_display_counter+1<=0:
                    self.prompt_display_counter+=1
                if self.prompt_display_counter<=-1:
                    self.set_new_prompt(self.prompt_history[self.prompt_display_counter])
                elif self.prompt_display_counter==0:
                    self.setPlainText('')
        else:
            if event.key()==Qt.Key.Key_Return:
                current_prompt=self.toPlainText()
                last_row=current_prompt.split('\n')[-2]
                N_indents=int((len(last_row)-len(last_row.lstrip()))/len(self.indent))+1
                if current_prompt[-2]==':':  
                    self.set_new_prompt(f"{current_prompt}{N_indents*self.indent}")
            elif event.key()==Qt.Key.Key_Backspace:
                try:
                    if self.toPlainText()[-len(self.indent)+1:]==self.indent[:-1]:
                        self.set_new_prompt(self.toPlainText()[:-(len(self.indent)-1)])
                except:
                    pass
    def set_new_prompt(self,new_prompt):
        self.setPlainText(new_prompt)
        cursor=self.textCursor()
        cursor.setPosition(len(new_prompt))
        self.setTextCursor(cursor)
class GUI(QWidget):
    def __init__(self):
        super().__init__()
        main_layout=QVBoxLayout()
        self.le=QLineEdit()
        main_layout.addWidget(self.le)

        self.te=PlainTextEdit()
        main_layout.addWidget(self.te)
        self.setLayout(main_layout)

        self.le.returnPressed.connect(self.update)
    def update(self):
        print(self.le.text())

app=QApplication([])
app.setFont(QFont('Times New Roman'))
gui=GUI()
gui.show()
app.exec()