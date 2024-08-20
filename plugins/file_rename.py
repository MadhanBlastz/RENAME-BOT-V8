import os
import asyncio
from PIL import Image
from your_database_module import db  # Replace with actual import
from your_helper_module import add_prefix_suffix, progress_for_pyrogram, humanbytes, convert, createParser, extractMetadata  # Replace with actual imports

async def doc(bot, update):

    # Creating necessary directories
    download_dir = os.path.expanduser("~/downloads/media")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")

    # Extracting necessary information
    prefix = await db.get_prefix(update.message.chat.id)
    suffix = await db.get_suffix(update.message.chat.id)
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1]

    try:
        # Adding prefix and suffix
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await update.message.edit(f"⚠️ Something went wrong can't able to set Prefix or Suffix ☹️ \n\n -> contact : @PCADMINOFFICIALBOT \nError: {e}")

    file_path = os.path.join(download_dir, new_filename)
    metadata_path = f"Metadata/{new_filename}"
    file = update.message.reply_to_message

    ms = await update.message.edit(" ** 🚀 𝗧𝗿𝘆𝗶𝗻𝗴 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 🚀 ** ")
    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("\n **🔥 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙 𝙎𝙩𝙖𝙧𝙩𝙚𝙙 🔥**", ms, time.time()))
    except Exception as e:
        return await ms.edit(e)

    _bool_metadata = await db.get_metadata(update.message.chat.id)

    if (_bool_metadata):
        metadata = await db.get_metadata_code(update.message.chat.id)
        if metadata:

            await ms.edit("I Fᴏᴜɴᴅ Yᴏᴜʀ Mᴇᴛᴀᴅᴀᴛᴀ\n\n__**Pʟᴇᴀsᴇ Wᴀɪᴛ...**__\n**Aᴅᴅɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ Tᴏ Fɪʟᴇ....**")
            cmd = f"""ffmpeg -i "{path}" {metadata} "{metadata_path}" """

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            er = stderr.decode()

            try:
                if er:
                    return await ms.edit(str(er) + "\n\n**Error**")
            except BaseException:
                pass
        await ms.edit("**Metadata added to the file successfully ✅**\n\n⚠️ __**Please wait...**__\n\n**🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**")
    else:
        await ms.edit(" ** 🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨 ** ")

    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
    except:
        pass

    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(
                media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇʏᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")
    else:
        caption = f"**{new_filename}**"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb)
        else:
            ph_path = await bot.download_media(media.thumbs[0].file_id)

        # Open the image file
        with Image.open(ph_path) as img:
            # Convert the image to RGB format and save it back to the same file
            img.convert("RGB").save(ph_path)
        
            # Resize the image
            resized_img = img.resize((320, 320))
            
            # Save the resized image in JPEG format
            resized_img.save(ph_path, "JPEG")

    type = update.data.split("_")[1]

    if media.file_size > 2000 * 1024 * 1024:
        try:
            if type == "document":
                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(" **🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨** ", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            elif type == "video":
                filw = await app.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(" **🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

            elif type == "audio":
                filw = await app.send_audio(
                    update.message.chat.id,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(" **🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**", ms, time.time()))

                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                await bot.delete_messages(from_chat, mg_id)

        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    else:
        try:
            if type == "document":
                await bot.send_document(
                    update.message.chat.id,
                    document=metadata_path if _bool_metadata else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("**🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**", ms, time.time()))
            elif type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(" **🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**", ms, time.time()))
            elif type == "audio":
                await bot.send_audio(
                    update.message.chat.id,
                    audio=metadata_path if _bool_metadata else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(" **🚨 𝐓𝐫𝐲 𝐓𝐨 𝐔𝐩𝐥𝐨𝐚𝐝 🚨**", ms, time.time()))
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            if metadata_path:
                os.remove(metadata_path)
            if path:
                os.remove(path)
            return await ms.edit(f" Eʀʀᴏʀ {e}")

    await ms.delete()


