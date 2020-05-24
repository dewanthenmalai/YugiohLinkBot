from YugiohLinkBot import YugiohLinkBot
from ErrorMailer import SendErrorMail
import traceback
import Config

bot = YugiohLinkBot(Config.subredditlist)

try:
    while(1):
        bot.run()
except Exception as e:
    print("Shutting down bot: " + str(e))
    SendErrorMail(e, traceback.format_exc())
    try:
        raise e
    except KeyboardInterrupt:
        exit(0)
