#!/usr/bin/python3

padLength = 30
padChar = "."

def info(message, item=None):
    out = message
    if not item is None:
        out = out + " "
        out = out.ljust(padLength, padChar)
        out = out + ": "
        out = out + str(item)
    print(out)


