"""
wordtwitch_wos_style.py
Words-on-Stream style Twitch-integrated game (simple local version)
Requires: pygame, twitchio
Place words.txt in repo root.
"""
import os
import random
import json
import time
import threading
import pygame
from twitchio.ext import commands

# -------- CONFIG ----------
WIDTH, HEIGHT = 1280, 720
FPS = 30
ROUND_SECONDS = 60
MIN_WORD_LENGTH = 3
WORDS_FILE = "words.txt"           # must exist
LEADERBOARD_FILE = "leaderboard.json"
CHANNEL = os.getenv("TWITCH_CHANNEL", "GuessTheWordGame")
TOKEN = os.getenv("TWITCH_TOKEN", "dummy_token")  # set in .env or GH secrets
NICK = os.getenv("TWITCH_NICK", "botname")
LETTER_POOL_SIZE = 9               # how many letters to show each round
FAKE_LETTERS = 1                   # number of fake letters (0 = disabled)
# --------------------------

# load dictionary
if not os.path.exists(WORDS_FILE):
    print(f"ERROR: '{WORDS_FILE}' not found. Place a word list in the repo root.")
    WORD_SET = set()
else:
    with open(WORDS_FILE, "r", encoding="utf8") as f:
        WORD_SET = set(w.strip().lower() for w in f if w.strip())

# leaderboard persistence
if os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "r", encoding="utf8") as f:
        leaderboard = json.load(f)
else:
    leaderboard = {}

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w", encoding="utf8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

def can_form(word, pool_letters):
    pool = list(pool_letters)
    for ch in word:
        if ch in pool:
            pool.remove(ch)
        else:
            return False
    return True

def make_letter_pool(dictionary, size=LETTER_POOL_SIZE, fake=0):
    candidates = [w for w in dictionary if len(w) >= 5 and len(w) <= 12]
    if not candidates:
        letters = [random.choice('etaoinshrdlcumwfgypbvkjxqz') for _ in range(size)]
        return letters
    seed = random.choice(candidates)
    letters = list(seed)
    while len(letters) < size:
        letters.append(random.choice('etaoinshrdlcumwfgypbvkjxqz'))
    for _ in range(fake):
        letters[random.randrange(len(letters))] = random.choice('zxqj')
    random.shuffle(letters)
    return letters

# Game state
current_pool = make_letter_pool(WORD_SET)
current_valid = set()
round_end_time = None
round_active = False
round_lock = threading.Lock()

# Pygame UI setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WordTwitch - WOS Style")
font_big = pygame.font.SysFont("Arial", 96)
font_med = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# Twitch bot
class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix="!", initial_channels=[CHANNEL])

    async def event_ready(self):
        print(f"Bot connected to {CHANNEL}")

    async def event_message(self, message):
        global round_active, current_valid
        if message.echo:
            return
        content = message.content.strip().lower()
        user = message.author.name

        # Host/mod commands
        if content.startswith("!start") and message.author.is_mod:
            start_round()
            await message.channel.send("Round started! Form words from the letters on screen.")
            return
        if content.startswith("!stop") and message.author.is_mod:
            stop_round()
            await message.channel.send("Round stopped by mod.")
            return
        if content.startswith("!leaderboard"):
            top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
            text = ", ".join(f"{u}: {s}" for u, s in top) or "No scores yet"
            await message.channel.send("Leaderboard: " + text)
            return

        with round_lock:
            if round_active and len(content) >= MIN_WORD_LENGTH and content.isalpha():
                if content in WORD_SET and can_form(content, current_pool) and content not in current_valid:
                    pts = len(content)
                    if len(content) >= 6: pts += 1
                    if len(content) >= 8: pts += 2
                    leaderboard[user] = leaderboard.get(user, 0) + pts
                    current_valid.add(content)
                    save_leaderboard()
                    await message.channel.send(f"✅ {user} found '{content}' (+{pts} pts)")

def run_bot():
    bot = TwitchBot()
    bot.run()

def start_round():
    global current_pool, round_end_time, round_active, current_valid
    with round_lock:
        current_pool = make_letter_pool(WORD_SET, LETTER_POOL_SIZE, FAKE_LETTERS)
        current_valid = set()
        round_end_time = time.time() + ROUND_SECONDS
        round_active = True
        print("Round started, pool:", "".join(current_pool))

def stop_round():
    global round_active
    with round_lock:
        round_active = False

if TOKEN != "dummy_token":
    threading.Thread(target=run_bot, daemon=True).start()
else:
    print("TWITCH_TOKEN missing or dummy -> Bot not started. Use local testing or set environment variable.")

start_round()

recent_msgs = []
def push_recent(msg):
    recent_msgs.insert(0, msg)
    if len(recent_msgs) > 6:
        recent_msgs.pop()

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            if ev.key == pygame.K_SPACE:
                start_round()

    screen.fill((10, 10, 25))
    title = font_med.render("WordTwitch — WOS-style Round", True, (200, 200, 255))
    screen.blit(title, (20, 10))

    pool_text = " ".join(current_pool)
    pool_surface = font_big.render(pool_text, True, (255, 255, 255))
    pool_rect = pool_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    screen.blit(pool_surface, pool_rect)

    if round_active and round_end_time:
        secs = max(0, int(round_end_time - time.time()))
        timer = font_med.render(f"Time: {secs}s", True, (255, 220, 120))
        screen.blit(timer, (WIDTH - 220, 20))
        if secs == 0:
            with round_lock:
                round_active = False
                push_recent("Round ended.")
    else:
        timer = font_med.render("Round inactive (press SPACE or !start)", True, (180,180,180))
        screen.blit(timer, (WIDTH - 420, 20))

    y = 120
    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:6]
    header = font_med.render("Leaderboard", True, (200,200,255))
    screen.blit(header, (20, 80))
    for u, s in top:
        t = font_small.render(f"{u}: {s}", True, (230,230,230))
        screen.blit(t, (20, y))
        y += 28

    rx = WIDTH - 420
    ry = 120
    recent_h = font_med.render("Recent", True, (200,200,255))
    screen.blit(recent_h, (rx, ry - 30))
    for i, m in enumerate(recent_msgs[:6]):
        t = font_small.render(m, True, (220,220,220))
        screen.blit(t, (rx, ry + i * 26))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
