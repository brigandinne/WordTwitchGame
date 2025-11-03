"""
WordTwitch Fullscreen - Pygame overlay + Twitch chat listener
Dark neon visual style with calm lofi background music
"""
import pygame
import random
import os
import json
import threading
from twitchio.ext import commands

# -------------- CONFIG --------------
WIDTH, HEIGHT = 1280, 720
FPS = 60
FONT_NAME = "arial"
WORDS = ["python", "stream", "twitch", "overlay", "chat", "neon", "music", "guess", "game"]
LOFI_MUSIC = "lofi.wav"  # Fixed path for build
LEADERBOARD_FILE = "leaderboard.json"
CHANNEL_NAME = "GuessTheWordGame"

# Safe environment variable load
TOKEN = os.getenv("TWITCH_TOKEN", "dummy_token")
if TOKEN == "dummy_token":
    print("⚠️  No TWITCH_TOKEN found — using dummy token so build won't fail.")

# ------------------------------------

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GuessTheWordGame")
font = pygame.font.SysFont(FONT_NAME, 60)
clock = pygame.time.Clock()

# Load music safely
if os.path.exists(LOFI_MUSIC):
    pygame.mixer.music.load(LOFI_MUSIC)
    pygame.mixer.music.play(-1)
else:
    print(f"⚠️  Music file '{LOFI_MUSIC}' not found, skipping music load.")

# Persistent leaderboard
if os.path.exists(LEADERBOARD_FILE):
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
else:
    leaderboard = {}

current_word = random.choice(WORDS)
masked = current_word[0] + "_" * (len(current_word) - 1)
winner = None

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix="!", initial_channels=[CHANNEL_NAME])

    async def event_message(self, message):
        global current_word, masked, winner
        if message.echo:
            return
        guess = message.content.strip().lower()
        user = message.author.name

        if guess == current_word:
            leaderboard[user] = leaderboard.get(user, 0) + (3 if message.author.is_subscriber else 1)
            winner = user
            save_leaderboard()
            current_word = random.choice(WORDS)
            masked = current_word[0] + "_" * (len(current_word) - 1)
            await message.channel.send(f"🎉 {user} guessed it! The word was '{guess}'. Next word incoming!")
        elif guess.startswith("!leaderboard"):
            top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
            text = ", ".join([f"{u}: {s}" for u, s in top]) or "No scores yet!"
            await message.channel.send(f"🏆 Leaderboard: {text}")

def run_twitch_bot():
    bot = TwitchBot()
    bot.run()

threading.Thread(target=run_twitch_bot, daemon=True).start()

# -------------- MAIN LOOP --------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 30))
    word_surface = font.render(masked, True, (0, 255, 180))
    screen.blit(word_surface, (WIDTH // 2 - word_surface.get_width() // 2, HEIGHT // 2))
    title_surface = font.render("GuessTheWordGame", True, (255, 0, 180))
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))

    if winner:
        win_text = font.render(f"{winner} guessed it!", True, (255, 255, 255))
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT - 100))
        winner = None

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
