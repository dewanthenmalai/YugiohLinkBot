# YugiohLinkBot
YugiohLinkBot is a Reddit bot which creates comments displaying Yugioh card information when requested (Yugioh is a collectable card game). YugiohLinkBot can be found [here](https://www.reddit.com/user/YGOLinkBot).

## Technical info
YGOLB is written in Python for use with Python 3.8. There's a requirements.txt if you want to test it out yourself, but you'll need to create Config.py with your own information. Please don't just run it right out of the box - you'll end up replying in all the same places the live bot does. If you do want to test it out yourself, you can link it to r/testingground4bots.

## How it works
YGOLB uses PRAW (a Python library) to interface with Reddit through the /u/YGOLinkBot account. It will then look through the new 50 or so comments once every minute or so, looking for the appropriate symbols. Once it's found one, it takes what's between the symbols and searches for it on various databases. If it finds it it makes a comment.

## Future work
- Use Yugipedia API to request data instead of scraping and parsing HTML
- Add card pricing information
- Add archetype linking?
