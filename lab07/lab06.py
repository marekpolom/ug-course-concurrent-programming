"""Lab06.

Usage:
  lab06.py -k <key>
  lab06.py (-v | --version)
  lab06.py (-h | --help)

Options:
  -h --help         Show this screen.
  -v --version      Show version.
  -k=<key>          Game key.

"""
import sysv_ipc, json, sys, os
import numpy as np

from typing import Any, List
from docopt import docopt

def key_check(key: str) -> bool:
    return key.isnumeric()

def is_board_full(board: np.ndarray) -> bool:
    return "" not in board

def check_board(board: np.ndarray, char: str) -> bool:
    n = board.shape[0]
    win_cond: List[str] = [char] * n

    rows: List[List[str]] = board[range(0, n), :].tolist()
    cols: List[List[str]] = np.transpose(board)[range(0, n), :].tolist()
    diags: List[List[str]] = [board.diagonal().tolist(), np.fliplr(board).diagonal().tolist()]

    if win_cond in rows or win_cond in cols or win_cond in diags:
        return True

    return False

def insert_char(row: int, col: int, board: np.ndarray, char: str) -> np.ndarray:
    if board[row, col] != "":
        raise Exception("Occupied")

    board[row, col] = char

    return board

def print_board(board):
    print("\n".join([" ".join([col or "-" for col in row]) for row in board]))

def read_mem(mem):
    s = mem.read()
    s = s.decode()
    i = s.find(NULL_CHAR)
    if i != -1:
        return s[:i]

def write_mem(mem, s):
    s += NULL_CHAR
    s = s.encode()
    mem.write(s)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Lab05 1.0')

    while True:
        if key_check(arguments['-k']):
            break
        else:
            print("Key must be of type INT")
            sys.exit()

    key: int = int(arguments['-k'])
    
    try:
        mem: Any = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        mem: Any = sysv_ipc.SharedMemory(key)
    
    try:
        sem: Any = sysv_ipc.Semaphore(key, sysv_ipc.IPC_CREX, 0o700, 1)
        first: bool = True
    except sysv_ipc.ExistentialError:
        sem: Any = sysv_ipc.Semaphore(key)
        first: bool = False

    self_char: str = "X" if first else "O"
    enemy_char: str = "O" if first else "X"

    NULL_CHAR = "\0"

    if first:
        print("You start!")
    else:
        print("Waiting for opponent to make a move...")

    game: bool = True

    board: np.ndarray

    if first:
        board = np.array([""] * 9).reshape(3, 3)
        write_mem(mem, json.dumps(board.tolist()))
    
    while game:
        sem.acquire()
        read = read_mem(mem)
        board = np.array(json.loads(read)).reshape(3, 3)

        if check_board(board, enemy_char):
            os.system("clear")
            print_board(board)
            print("You loose...")
            break
        elif is_board_full(board):
            os.system("clear")
            print_board(board)
            print("Tie!")
            break
        
        os.system("clear")
        
        print_board(board)
        
        move = True
        
        while move:
            while True:
                try:
                    row = int(input("Row: "))
                    if row in range(1, 4):
                        break
                    else:
                        print("Input digit from 1 to 3")
                except:
                    print("Input digit from 1 to 3")
            while True:
                try:
                    col = int(input("Column: "))
                    if col in range(1, 4):
                        break
                    else:
                        print("Input digit from 1 to 3")
                except:
                    print("Input digit from 1 to 3")
            try:
                board = insert_char(row - 1, col - 1, board, self_char)
                break
            except:
                print("Choosen tile is already occupied!")
    
        board_json = json.dumps(board.tolist())

        if check_board(board, self_char):
            print("You win!")
            write_mem(mem, board_json)
            move = False
            game = False
            sem.release()
            break
        elif is_board_full(board):
            print("Tie!")
            write_mem(mem, board_json)
            move = False
            game = False
            sem.release()
            break
        else:
            write_mem(mem, board_json)

        os.system("clear")
        print_board(board)
        print("Waiting for opponent to make a move...")
        sem.release()
    
    try:
        sem.remove()
        mem.remove()
    except:
        pass