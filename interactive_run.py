from importlib.util import spec_from_loader,module_from_spec
from traceback import print_exc
from sys import argv
from os.path import dirname,basename,join
from os import _exit

#run through command line as: python f2.py path\to\script.py
#to read script.py and go to an interactive python shell that has access to everything defined in script.py
#enter any python command and press enter, a check of wether script.py has been changed will be issued
#if any changes have been saved, script.py will be reloaded and the command will be issued with to the updated environment

#class containing all variables and functions used to run the interactive session
class interactive_handler:
    def __init__(self,work_script_path):
        self.folder_name=dirname(work_script_path)
        self.work_script_name=basename(work_script_path).split('.')[0]
        self.read_file_name=join(self.folder_name,f"{self.work_script_name}.py")
        self.non_custom_dict_entries={'__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__'}        
        self.read_file() #generate self.check
        self.ref=self.check
        self.return_str=''
        self.base_globals={key:value for key,value in globals().items()}
        self.import_from_script_str()
        self.off_limit_commands_dict={
            "__interactive_handler":"__interactive_handler is designated to handle the interactive session, please don't use it in any commands!",
            "globals()":"Access to globals() is disabled."
            }
    def read_file(self):
        with open(self.read_file_name,'r') as f:
            temp=f.read()
            self.check=temp.split('__interactive_handler stop')[0]
            if "'__interactive_handler stop" in temp or '"__interactive_handler stop' in temp:
                self.check=self.check[:-1]
    def read_user_input(self):
        self.input_str=input('> ')
    def import_from_script_str(self,input_str=None):
        if not input_str:
            spec=spec_from_loader(self.work_script_name,loader=None)
            self.module=module_from_spec(spec)
            exec(self.check, self.module.__dict__)
            for key in list(globals().keys()):
                if key not in self.base_globals and globals()[key]!=self:
                    del globals()[key]
        else:
            spec=spec_from_loader('temp',loader=None)
            self.module=module_from_spec(spec)
            exec(input_str, self.module.__dict__)        
        for thing in dir(self.module):
            if thing not in self.non_custom_dict_entries:
                globals()[thing]=eval(f"self.module.{thing}")
    def execute_input_str(self):
        display_return_str_bool=True
        if 'def' in self.input_str or 'class' in self.input_str:
            display_return_str_bool=False
            self.import_from_script_str(self.input_str)
        elif '=' in self.input_str:
            display_return_str_bool=False
            input_str_len=len(self.input_str.split('=')[0])
            for check_index in [input_str_len-1,input_str_len+1]:
               if self.input_str[check_index] in {'=','<','>','!'}:
                   display_return_str_bool=True
                   break
            if not display_return_str_bool:
                key=self.input_str.split('=')[0]
                value=self.input_str[len(key)+1:]
                globals()[key]=eval(value)
        if display_return_str_bool:
            if self.input_str=='exit()':
                _exit(1)
            else:
                self.return_str=eval(self.input_str)
                if self.return_str!=None:
                    print(self.return_str)
    def user_interaction(self):
        self.read_user_input()        
        off_limit_response_str=''
        for off_limit_str,response in self.off_limit_commands_dict.items():
            if off_limit_str in self.input_str:
                off_limit_response_str+=f"{response}\n"
        if off_limit_response_str:
            print(' ')
            print(off_limit_response_str)
        else:
            self.read_file()
            if self.check!=self.ref:
                self.ref=self.check
                self.import_from_script_str()
            self.execute_input_str()

if __name__=="__main__":    
    try:
        __interactive_handler=interactive_handler(r'C:\Users\Robban\Desktop\tt\f1.py')
        # __interactive_handler=interactive_handler(argv[1])
        del interactive_handler #remove the class definition after creation to avoid interference
        while True:
            try:
                __interactive_handler.user_interaction()
            except Exception as e:
                print_exc()
    except:
        print_exc()