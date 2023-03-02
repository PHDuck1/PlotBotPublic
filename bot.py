import matplotlib.pyplot as plt
import numpy as np
import io
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '5719504378:AAGAT5cMC6-DqzE2UY2tBADKZFew9KRMYEA'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hey, send me r1 and r2 separated by the space"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def plot_point(update, context):
    try:
        # Extract the two numbers from the message text
        r1, r2 = map(float, update.message.text.split())
        
        f1s = [round(0.1*i, 2) for i in range(1, 10)]
        f2s = [round(1-f1, 2) for f1 in f1s]

        approxFs = [round((r1*f1**2 + f1*f2) / (r1*f1**2 + 2*f1*f2 + r2*f2**2), 4)
                    for f1, f2 in zip(f1s, f2s)]

        f1s_ext = [0.01*i for i in range(100)]
        f2s_ext = [1-f1 for f1 in f1s_ext]

        Fs = [round((r1*f1**2 + f1*f2) / (r1*f1**2 + 2*f1*f2 + r2*f2**2), 4)
            for f1, f2 in zip(f1s_ext, f2s_ext)]
        
        plt.plot(f1s, approxFs, 'o', label=f'F:\n{r1=}\n{r2=}')

        polynom = np.poly1d(np.polyfit(f1s_ext, Fs, 3))

        plt.plot(f1s_ext, polynom(f1s_ext), label=f'approx F')

        plt.plot((0, 1), (0, 1), '--', label='r1=r2=1')

        if r1 < 1 and r2 < 1:
            eq = polynom - np.poly1d([1, 0])
            root = [r for r in eq.roots if 0.01 < r < 0.99][0]
            plt.plot(root, polynom(root), 'o', color='purple', label=f'перетин {round(polynom(root), 2)}')
            plt.vlines(root, 0, polynom(root), color='purple')

        plt.grid(True)
        plt.ylim(0, 1)
        plt.xlim(0, 1)
        plt.title(f'Залежність складу полімеру від складу мономерної суміші\nF:{approxFs}')
        plt.xlabel('f1')
        plt.ylabel('F')
        plt.legend()
        
        # Save the figure to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        # Send the image to the user
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buffer)
    except:
        # If something goes wrong, send an error message
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that. Send me two numbers separated by a space.")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plot_point))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
    