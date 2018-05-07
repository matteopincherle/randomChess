#! /usr/bin/python3

import chess
from multiprocessing import Queue
from select import select
import sys
import threading
from threading import Thread
import random
import time

logfile = 'log.dat'

def l(msg):
	global logfile
	fh = open(logfile, 'a')
	fh.write('%s %s\n' % (time.asctime(), msg))
	fh.close()

def set_l(file_):
	global logfile
	logfile = file_

class Board(chess.Board, object):
    def __init__(self, f=chess.STARTING_FEN, c=False):
        self._moves = []
        super(Board, self).__init__(f, c)

    def _get_move_list(self):
        return list(self.legal_moves)

    def get_move_list(self):
        if not self._moves:
            self._moves.append(self._get_move_list())
        return self._moves[-1]

    def push(self, m):
        me = self.piece_at(m.from_square)
        super(Board, self).push(m)
        self._moves.append(self._get_move_list())

    def pop(self):
        del self._moves[-1]
        return super(Board, self).pop()

class stdin_reader(threading.Thread):
    q = Queue()
    def run(self):
        l('stdin thread started')
        while True:
            line = sys.stdin.readline()
            self.q.put(line)
        l('stdin thread terminating')

    def get(self, to = None):
        try:
            if not to:
                return self.q.get()
            return self.q.get(True, to)
        except:
            return None

def send(str_):
    print(str_)
    l('OUT: %s' % str_)
    sys.stdout.flush()

def main():
	sr = stdin_reader()
	sr.daemon = True
	sr.start()
	board = Board()
	while True:
		line = sr.get()
		if line == None:
			break
		line = line.rstrip('\n')
		if len(line) == 0:
			continue
		l('IN: %s' % line)
		parts = line.split(' ')
		send('PARTS:')
		send(parts[0])
		if parts[0] == 'uci':
			send('id name RandomChess')
			send('id author Matteo Pincherle')
			send('uciok')
		elif parts[0] == 'isready':
			send('readyok')
		elif parts[0] == 'ucinewgame':
			board = Board()
		elif parts[0] == 'position':
			is_moves = False
			nr = 1
			while nr < len(parts):
				if is_moves:
					board.push_uci(parts[nr])
				elif parts[nr] ==  'fen':
					board = Board(' '.join(parts[nr + 1:]))
					break
				elif parts[nr] == 'startpos':
					board = Board()
				elif parts[nr] == 'moves':
					is_moves = True
				else:
					l('unknown: %s' % parts[nr])
				nr += 1
		elif parts[0] == 'go':
			moves = list(board.legal_moves)
			idx = random.randint(0, len(moves) - 1)
			if not board.is_legal(moves[idx]):
				l('FAIL')
			result = moves[idx]
			if result:
				send('bestmove %s' % result.uci())
				board.push(result)
		elif parts[0] == 'quit':
			break
		elif parts[0] == 'fen':
			send('%s' % board.fen())
			sys.stdout.flush()
if len(sys.argv) == 2:
    set_l(sys.argv[1])

main()
