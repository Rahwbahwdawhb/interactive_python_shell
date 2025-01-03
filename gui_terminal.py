from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QLineEdit, QLabel, QPlainTextEdit, QTextEdit,QListWidget,QListWidgetItem, QScrollArea
from PyQt6.QtGui import QColor, QFont,QTextCursor,QFontDatabase
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
        self.resize(800,400)
        main_layout=QVBoxLayout()

        self.terminal_window=QLabel()
        self.terminal_window.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.terminal_window.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.terminal_window.setStyleSheet("QLabel { background-color : black; color : white;}")
        self.terminal_scroll=QScrollArea()
        self.terminal_scroll.setWidget(self.terminal_window)
        self.terminal_scroll.setWidgetResizable(True)
        
        main_layout.addWidget(self.terminal_scroll)
        main_layout.setContentsMargins(0,0,0,0)

        self.te=PlainTextEdit()
        main_layout.addWidget(self.te)
        self.setLayout(main_layout)
        
        self.le=QLineEdit()
        self.le.returnPressed.connect(self.update)
        main_layout.addWidget(self.le)
    def add_text_to_terminal(self,text):
        current_prompt=self.terminal_window.text()
        if current_prompt:
            new_prompt=f"{current_prompt}\n\n{text}"
        else:
            new_prompt=text
        self.terminal_window.setText(new_prompt)
        self.terminal_scroll.verticalScrollBar().setValue(self.terminal_scroll.verticalScrollBar().maximum()+10)
        self.terminal_scroll.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        self.terminal_scroll.verticalScrollBar().setValue(self.terminal_scroll.verticalScrollBar().maximum())
    def update(self):
        self.add_text_to_terminal(self.le.text())

app=QApplication([])
app.setFont(QFont('Times New Roman'))
gui=GUI()
gui.show()
app.exec()
