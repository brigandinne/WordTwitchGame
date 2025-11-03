WordTwitch Fullscreen - README
==============================

This package runs a full-screen Twitch-integrated word guessing game. The overlay is designed to be the entire stream canvas.

Requirements:
- Python 3.11
- pip install twitchio pygame

Files included:
- wordtwitch_fullscreen.py  : main program
- words.txt                 : sample word list (add your own)
- .env                      : template for Twitch credentials
- start.wav, correct.wav    : basic sound effects (generated)
- lofi.mp3                  : placeholder (silent) - replace with your own lofi track
- scores.json               : will be created when someone scores

How to run (development):
1. Fill .env with real TWITCH_TOKEN, TWITCH_NICK and TWITCH_CHANNEL.
2. Install dependencies: pip install twitchio pygame
3. Run: python wordtwitch_fullscreen.py
4. The program opens full-screen. Press ESC to quit, SPACE to force new round (for testing).

How to build an .exe:
- pip install pyinstaller
- pyinstaller --onefile --name WordTwitchFull --console wordtwitch_fullscreen.py
- The built exe will be in dist/WordTwitchFull.exe

Notes:
- Replace lofi.mp3 with a proper lofi music file (MP3/OGG) in the same folder.
- The app saves scores to scores.json for persistence.
