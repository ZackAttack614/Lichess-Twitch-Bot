import chess
import chess.pgn
import requests
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import time

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--headless')

browser = webdriver.Chrome(options=chrome_options)

current_legal_moves = list()
last_check_time = 0

def filter_move_suggestions(user: str, message_text: str) -> bool:
  global current_legal_moves
  global last_check_time
  global browser

  if time() - last_check_time < 5:
    for move in current_legal_moves:
      if move.lower() in message_text.lower().split():
        return True
    return False

  response = requests.get(f'https://lichess.org/api/users/status?ids={user}')
  if not response.json()[0].get('playing', False):
    return False

  response = requests.get(f'https://lichess.org/api/user/{user}/current-game')
  pgn = io.StringIO(response.text)
  game = chess.pgn.read_game(pgn)
  url = game.headers.get('Site')
  browser.get(url)

  board = game.board()
  for move in browser.find_elements_by_tag_name('u8t'):
    board.push_san(move.text)

  current_legal_moves = [board.variation_san([move]).split('.')[-1].strip().lower() for move in board.legal_moves]
  last_check_time = time()

  for move in current_legal_moves:
    if move in message_text.lower().split():
      return True

  return False

filter_move_suggestions('zackattack614', 'o-o')