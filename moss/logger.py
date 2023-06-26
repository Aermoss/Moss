import moss, ctypes, sys, datetime

def set_text_attr(color):
    if sys.platform == "win32":
        console_handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32. SetConsoleTextAttribute(console_handle, color)

    else:
        if color == 7:
            print("\u001b[0m", end = "", flush = True)

        elif color == 13:
            print("\u001b[31;1m", end = "", flush = True)

        elif color == 12:
            print("\u001b[31m", end = "", flush = True)

        else:
            ...

INFO = 0
WARNING = 1
ERROR = 2
FATAL_ERROR = 3
NONE = 3

class Logger:
    def __init__(self):
        self.text = ""
        self.level = INFO

    def log(self, level, msg):
        self.text += datetime.datetime.now().strftime("[%m/%d/%Y-%H:%M:%S]") + f": moss: %s: %s" % ({INFO: "info", WARNING: "warning", ERROR: "error", FATAL_ERROR: "fatal error"}[level], msg) + "\n"
        
        if self.level <= level:
            set_text_attr(7)
            print("moss: ", end = "", flush = True)
            set_text_attr({INFO: 10, WARNING: 13, ERROR: 12, FATAL_ERROR: 12}[level])
            print("%s: " % {INFO: "info", WARNING: "warning", ERROR: "error", FATAL_ERROR: "fatal error"}[level], end = "", flush = True)
            set_text_attr({INFO: 7, WARNING: 13, ERROR: 12, FATAL_ERROR: 12}[level])
            print(msg, end = "\n", flush = True)
            set_text_attr(7)

    def get(self):
        return self.text

    def save(self, filePath):
        with open(filePath, "w") as file:
            file.write(self.text)