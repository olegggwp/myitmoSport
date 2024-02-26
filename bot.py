import json
from telegram.ext import Updater, CommandHandler, CallbackContext
import sport
from telegram import Update

def make_slot_text(slot):
    text = f"Date: {slot['date']}\n"
    text += f"Section: {slot['section_name']}\n"
    text += f"Teacher: {slot['teacher_fio']}\n"
    text += f"Level: {slot['lesson_level_name']}\n"
    text += f"Available: {slot['available']}\n"
    text += f"Time: {slot['time_slot_start']} - {slot['time_slot_end']}\n"
    text += f"type name: {slot['type_name']}\n\n"
    return text

writeOnStart = True
def main():
    # get TOKEN and CHAT_ID from file
    with open("config.json", "r") as file:
        config = json.load(file)
        TOKEN, CHAT_ID = config["TOKEN"], config["CHAT_ID"]

    seenSlots = set()
    users = set()


    def load_users():
        global users
        with open("users.json", "r") as file:
            x = json.load(file)
            users = set(x)

    def save_users():
        global users
        with open("users.json", "w") as file:
            json.dump(list(users), file)

    def check_slots(context: CallbackContext) -> None:
        global writeOnStart
        slots = sport.get_slots()
        if slots:
            finalText = ""
            for slot in slots:
                if slot['id'] not in seenSlots:
                    seenSlots.add(slot['id'])
                    finalText += make_slot_text(slot)
            if finalText:
                for user in users:
                    context.bot.send_message(chat_id=user, text=finalText)
                context.bot.send_message(chat_id=CHAT_ID, text=finalText)
            elif writeOnStart:
                writeOnStart = False
                for user in users:
                    context.bot.send_message(chat_id=user, text="Nothing Yet but bot is started")
                context.bot.send_message(chat_id=CHAT_ID, text="Nothing Yet but bot is started")
    
    def start(update: Update, context: CallbackContext) -> None:
        load_users()
        update.message.reply_text(
            f'Your chat_id is {update.effective_chat.id}')
        users.add(update.effective_chat.id)
        save_users()

    updater = Updater(TOKEN, use_context=True)
    load_users()

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    # Schedule the check_slots function to run every 10 seconds
    updater.job_queue.run_repeating(check_slots, interval=10, first=0)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
