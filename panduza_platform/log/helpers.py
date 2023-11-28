import re
from colorama import Fore, Back, Style


def level_highlighter(message, patterns):
    h = message
    for pat, style in patterns.items():
        h = h.replace(pat, style + pat + Style.RESET_ALL)
    return h

def re_highlighter(message, patterns, debug=""):
    h = message

    for pat, style in patterns:
        matches=(re.findall(pat, h))
        if matches:
            # print(pat, ">>>>", matches)
            for m in matches:
                h = h.replace(m, debug + style + m + Style.RESET_ALL)
    return h

def highlighter(message, patterns, debug=""):
    h = message
    for pat, style in patterns.items():
        h = h.replace(pat, debug + style + pat + Style.RESET_ALL)
    return h


    