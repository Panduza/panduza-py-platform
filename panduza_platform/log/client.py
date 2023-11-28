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


FORES = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]


class ClientFormatter(logging.Formatter):

    NextBackId=0

    def __init__(self):
        super().__init__()
        self.fore_id = ClientFormatter.NextBackId
        self.fore = FORES[self.fore_id]
        ClientFormatter.NextBackId = (ClientFormatter.NextBackId+1)%len(FORES)


    def formatMessage(self, record):

        # print(record.__dict__)
        # print(self.fore_id)

        debug=""
        if record.levelname == "DEBUG":
            debug=Style.DIM

        hmsg = record.message
        hmsg = re_highlighter(hmsg, re_patterns, debug)
        hmsg = highlighter(hmsg, patterns, debug)

        t_name = "Main"
        if record.threadName != "MainThread":
            t_name = record.threadName

        output = ""
        output += t_name.ljust(5, ' ')
        output += "| "
        output += level_highlighter(record.levelname.ljust(8, ' '), level_patterns)
        output += "| "
        output += self.fore + record.name + Style.RESET_ALL + " > "
        output += debug + hmsg

        return output


# =============================================================================

def client_logger(client_name):
    """Logger for platform clients
    """

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ClientFormatter())

    __logger = logging.getLogger(client_name)
    __logger.setLevel(logging.DEBUG)
    __logger.addHandler(ch)

    return __logger
