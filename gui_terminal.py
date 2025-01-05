from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QLineEdit, QLabel, QPlainTextEdit, QTextEdit,QListWidget,QListWidgetItem, QScrollArea
from PyQt6.QtGui import QColor, QFont,QTextCursor,QFontDatabase,QKeyEvent
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6 import QtWidgets

import sys
from traceback import format_exc
import tempfile
from interactive_run import interactive_handler

class PlainTextEdit(QPlainTextEdit):
    prompt_input_signal=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.prompt_input_history=[]
        self.prompt_input_display_counter=0
        self.indent='  '        
    def keyPressEvent(self, event):
        super(PlainTextEdit, self).keyPressEvent(event) #original key press handling
        #extra handling
        if QApplication.keyboardModifiers()==Qt.KeyboardModifier.ControlModifier:
            if event.key()==Qt.Key.Key_Return:
                current_prompt_input=self.toPlainText()
                self.prompt_input_signal.emit(current_prompt_input)
                self.prompt_input_history.append(current_prompt_input)
                self.prompt_input_display_counter=0
                self.setPlainText('')
            elif self.prompt_input_history and event.key()==Qt.Key.Key_Up:
                if abs(self.prompt_input_display_counter-1)<=len(self.prompt_input_history):
                    self.prompt_input_display_counter-=1
                self.set_input_prompt(self.prompt_input_history[self.prompt_input_display_counter])
            elif self.prompt_input_history and event.key()==Qt.Key.Key_Down:
                if self.prompt_input_display_counter+1<=0:
                    self.prompt_input_display_counter+=1
                if self.prompt_input_display_counter<=-1:
                    self.set_input_prompt(self.prompt_input_history[self.prompt_input_display_counter])
                elif self.prompt_input_display_counter==0:
                    self.setPlainText('')
        else:
            if event.key()==Qt.Key.Key_Return:
                current_prompt_input=self.toPlainText()                
                last_row=current_prompt_input.split('\n')[-2]
                N_indents=int((len(last_row)-len(last_row.lstrip()))/len(self.indent))+1
                if current_prompt_input[-2]==':':  
                    self.set_input_prompt(f"{current_prompt_input}{N_indents*self.indent}")
            elif event.key()==Qt.Key.Key_Backspace:
                try:
                    if self.toPlainText()[-len(self.indent)+1:]==self.indent[:-1]:
                        self.set_input_prompt(self.toPlainText()[:-(len(self.indent)-1)])
                except:
                    pass
    def set_input_prompt(self,input_prompt):
        self.setPlainText(input_prompt)
        cursor=self.textCursor()
        cursor.setPosition(len(input_prompt))
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
            self.terminal_scroll.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)
            
            main_layout.addWidget(self.terminal_scroll)
            main_layout.setContentsMargins(0,0,0,0)

            self.terminal_input=PlainTextEdit()
            main_layout.addWidget(self.terminal_input)
            self.setLayout(main_layout)
            
        def add_text_to_terminal(self,text):
            current_prompt_input=self.terminal_window.text()
            if current_prompt_input:
                new_prompt=f"{current_prompt_input}\n\n{text}"
            else:
                new_prompt=text
            self.terminal_window.setText(new_prompt)
        def scroll_to_bottom(self):
            self.terminal_scroll.verticalScrollBar().setValue(self.terminal_scroll.verticalScrollBar().maximum())

class frontend_backend_linker:
    def __init__(self,full_path_working_script):
        self.app=QApplication([])
        self.app.setFont(QFont('Times New Roman'))
        self.ih=interactive_handler(full_path_working_script)
        self.ih.off_limit_commands_dict={
            "interactive_handler":"interactive_handler is the class that governing the interactive session, its access is disabled.",
            "globals()":"Access to globals() is disabled."
            }
        self.gui=GUI()
        self.gui.terminal_input.prompt_input_signal.connect(self.execute_prompt_input)
    def execute_prompt_input(self, str_):
        off_limit_response_str=''
        for off_limit_str,response in self.ih.off_limit_commands_dict.items():
            if off_limit_str in str_:
                off_limit_response_str+=f"{response}\n"
        if off_limit_response_str:
            self.gui.add_text_to_terminal(f">{str_}\n{off_limit_response_str}")
        else:
            self.ih.input_str=str_
            self.ih.read_file()
            if self.ih.check!=self.ih.ref:
                self.ih.ref=self.ih.check
                self.ih.import_from_script_str()
            with tempfile.NamedTemporaryFile(mode='w+t', delete_on_close=False) as f:
                sys.stdout=f
                try:
                    self.ih.execute_input_str()
                except Exception as e:
                    f.write(format_exc(limit=None,chain=True))
                f.close()
                with open(f.name,'r') as f_:            
                    self.gui.add_text_to_terminal(f">{str_}\n{f_.read()}")
    def run(self):
        self.gui.show()
        self.app.exec()



if __name__=='__main__':
    fbl=frontend_backend_linker(r'C:\Users\Robban\Desktop\tt\f1.py')
    fbl.run()

#todo:
#*handle multiple print statements and multiple variable mentions
#*start from terminal
#*adjust GUI look/color