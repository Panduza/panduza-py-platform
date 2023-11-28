import re
import logging
from colorama import Fore, Back, Style

from .helpers import level_highlighter, re_highlighter, highlighter

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


level_patterns = {
    "DEBUG": Fore.WHITE + Style.DIM,
    "INFO": Fore.BLUE + Style.NORMAL,
    "WARN": Fore.YELLOW + Style.BRIGHT,
    "ERROR": Fore.RED + Style.BRIGHT,
    "CRITICAL": Back.RED + Style.BRIGHT,
}

re_patterns = [
    # [ re.compile(r'[\s,{+](-?[0-9.]+)'), Fore.CYAN], # numbers
    [ re.compile(r'[\s,]+(\d.+)[\s,]+'), Fore.CYAN], # numbers
    [ re.compile(r'[\s,{}]+(\'.*?\')'), Fore.YELLOW], # strings
    [ re.compile(r'[\s,{}]+(\".*?\")'), Fore.YELLOW], # strings
    [ re.compile(r'[\s=]+(%.*?%)'), Fore.BLUE], # topics
]

patterns = {
    "started!": Fore.GREEN,
    "MSG_IN": Fore.MAGENTA,
    "MSG_OUT": Fore.CYAN,
}


BACKS = [Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE]


class DriverFormatter(logging.Formatter):

    NextBackId=0

    def __init__(self):
        super().__init__()
        self.back_id = DriverFormatter.NextBackId
        self.back = BACKS[self.back_id]
        DriverFormatter.NextBackId = (DriverFormatter.NextBackId+1)%len(BACKS)


    def formatMessage(self, record):

        # print(record.__dict__)
        # print(self.back_id)

        debug=""
        if record.levelname == "DEBUG":
            debug=Style.DIM

        hmsg = record.message
        hmsg = re_highlighter(hmsg, re_patterns, debug)
        hmsg = highlighter(hmsg, patterns, debug)

        t_name = "Main"
        if record.threadName != "MainThread":
            t_name = record.threadName

        output = "" + Style.RESET_ALL
        output += t_name.ljust(5, ' ')
        output += "| "
        output += level_highlighter(record.levelname.ljust(8, ' '), level_patterns)
        output += "| "
        output += Style.BRIGHT + self.back + record.name + Style.RESET_ALL + " "
        output += debug + hmsg

        return output


# =============================================================================

def driver_logger(driver_name):
    """Logger for platform drivers
    """

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(DriverFormatter())

    __logger = logging.getLogger(driver_name)
    __logger.setLevel(logging.DEBUG)
    __logger.addHandler(ch)

    return __logger


