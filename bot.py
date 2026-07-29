import os
import shutil
import zipfile
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def unzip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if document is None:
        return

    if not document.file_name.lower().endswith(".zip"):
        await update.message.reply_text("Please send a ZIP file.")
        return

    file = await document.get_file()

    zip_path = DOWNLOAD_DIR / document.file_name

    await file.download_to_drive(zip_path)

    extract_folder = DOWNLOAD_DIR / document.file_name.replace(".zip", "")

    extract_folder.mkdir(exist_ok=True)

    try:

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_folder)

        await update.message.reply_text("ZIP Extracted. Uploading files...")

        total = 0

        for root, dirs, files in os.walk(extract_folder):
            for f in files:
                path = os.path.join(root, f)

                with open(path, "rb") as fp:
                    await update.message.reply_document(fp)

                total += 1

        await update.message.reply_text(f"Done! {total} file(s) uploaded.")

    except Exception as e:

        await update.message.reply_text(str(e))

    finally:

        if zip_path.exists():
            zip_path.unlink()

        shutil.rmtree(extract_folder, ignore_errors=True)


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, unzip))

    print("Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()
