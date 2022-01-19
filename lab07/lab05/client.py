"""Lab05.

Usage:
  client.py -w <word>
  client.py (-v | --version)
  client.py (-h | --help)

Options:
  -h --help         Show this screen.
  -v --version      Show version.
  -w=<word>         Word.

"""
from docopt import docopt
from ipcqueue import sysvmq
import os

def client(word):
    inQ = sysvmq.Queue(1)
    outQ = sysvmq.Queue(2)

    msg: str = word

    pid = os.getpid()
    msg = f"{pid},{msg}"

    inQ.put(msg)

    return outQ.get(msg_type=pid)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Lab05 1.0')

    translated = client(arguments['-w'])

    print(f"Słowo: {arguments['-w']}, przetłumaczone zostało na: {translated}")
