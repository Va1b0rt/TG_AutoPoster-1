import pyrogram.errors
from loguru import logger as log
from pyrogram.types import InputMediaPhoto

from TG_AutoPoster.tools import split


class PostSender:
    caption_link: str

    def __init__(self, bot, post, chat_id, disable_notification=False, disable_web_page_preview=True, add_link = False):
        self.bot = bot
        self.post = post
        self.chat_id = chat_id
        self.text = split(self.post.text)
        self.fill_in_caption_link(add_link)

        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview

    def fill_in_caption_link(self, add_link: bool) -> None:
        if add_link:
            self.caption_link = '\n<a href="https://t.me/dbas_music_bot">🔊Музыка | Новинки </a>'
        else:
            self.caption_link = ""

    @log.catch()
    def send_post(self):
        try:
            self.send_media()
            if hasattr(self.post, "docs") and len(self.post.docs) != 0:
                self.send_documents()
            if hasattr(self.post, "tracks") and len(self.post.tracks) != 0:
                self.send_music()
            if hasattr(self.post, "poll") and self.post.poll:
                self.send_poll()
        except (pyrogram.errors.ChatIdInvalid, pyrogram.errors.PeerIdInvalid):
            log.exception(
                "Чат {} не был найден. Возможно, ID чата (канала) указан неверно или бот отсутствует в нём.".format(
                    self.chat_id
                )
            )
            log.opt(exception=True).debug("Error stacktrace added to the log message")
        except pyrogram.errors.InternalServerError:
            log.exception("Telegram испытывает проблемы. Попробуйте позднее.")
            log.opt(exception=True).debug("Error stacktrace added to the log message")
        except pyrogram.errors.RPCError as error:
            log.exception("Telegram Error: {}", error)
            log.opt(exception=True).debug("Error stacktrace added to the log message")

    def send_media(self):
        if self.post.media:
            if len(self.post.media) == 1:
                if len(self.post.text) > 1024:
                    self.send_splitted_message(self.bot, self.text, self.chat_id)
                    self.bot.send_message(
                        self.chat_id,
                        self.text[-1], disable_web_page_preview=self.disable_web_page_preview,
                        disable_notification=self.disable_notification,
                    )
                    if isinstance(self.post.media[0], InputMediaPhoto):
                        self.bot.send_photo(
                            self.chat_id,
                            self.post.media[0]["media"],
                            reply_markup=self.post.reply_markup,
                            disable_notification=self.disable_notification,
                        )
                    else:
                        self.bot.send_video(
                            self.chat_id,
                            self.post.media[0]["media"],
                            reply_markup=self.post.reply_markup,
                            disable_notification=self.disable_notification,
                        )
                else:
                    if isinstance(self.post.media[0], InputMediaPhoto):
                        self.bot.send_photo(
                            self.chat_id,
                            self.post.media[0]["media"],
                            reply_markup=self.post.reply_markup,
                            caption=self.text[-1],
                            disable_notification=self.disable_notification,
                        )
                    else:
                        self.bot.send_video(
                            self.chat_id,
                            self.post.media[0]["media"],
                            caption=self.text[-1],
                            reply_markup=self.post.reply_markup,
                            disable_notification=self.disable_notification,
                        )
            else:
                log.info("Отправка текста")
                if len(self.post.text) > 1024:
                    self.send_splitted_message(self.bot, self.text, self.chat_id)
                    self.bot.send_message(
                        self.chat_id,
                        self.text[-1],
                        reply_markup=self.post.reply_markup,
                        disable_web_page_preview=self.disable_web_page_preview,
                        disable_notification=self.disable_notification,
                    )
                    self.bot.send_media_group(
                        self.chat_id, self.post.media,
                        disable_notification=self.disable_notification
                    )
                else:
                    self.post.media[0]["caption"] = self.post.text
                    self.bot.send_media_group(
                        self.chat_id, self.post.media, disable_notification=self.disable_notification
                    )
        elif self.post.text and not self.post.docs:
            self.send_splitted_message(self.bot, self.text, self.chat_id)
            self.bot.send_message(
                self.chat_id,
                self.text[-1],
                reply_markup=self.post.reply_markup,
                disable_web_page_preview=self.disable_web_page_preview,
                disable_notification=self.disable_notification,
            )

    def send_documents(self):
        log.info("Отправка прочих вложений")
        for i, doc in enumerate(self.post.docs):
            log.debug("Sending document {}", doc)
            if i == 0:
                if not self.post.media:
                    if len(self.post.text) < 1024:
                        self.bot.send_document(
                            self.chat_id,
                            document=doc,
                            caption=self.text[-1],
                            reply_markup=self.post.reply_markup,
                            disable_notification=self.disable_notification,
                        )
                    else:
                        self.send_splitted_message(self.bot, self.text, self.chat_id)

                        self.bot.send_message(
                            self.chat_id,
                            self.text[-1],
                            reply_markup=self.post.reply_markup,
                            disable_web_page_preview=self.disable_web_page_preview,
                            disable_notification=self.disable_notification,
                        )

                        self.bot.send_document(
                            self.chat_id, document=doc, disable_notification=self.disable_notification,
                        )
                else:
                    self.bot.send_document(
                        self.chat_id, document=doc, disable_notification=self.disable_notification,
                    )
            else:
                self.bot.send_document(
                    self.chat_id, document=doc, disable_notification=self.disable_notification,
                )

    def send_music(self):
        log.info("Отправка аудио")
        for audio, artist, title in self.post.tracks:
            log.debug("Sending audio {}", audio)
            self.bot.send_audio(
                self.chat_id, audio, disable_notification=self.disable_notification,
                performer="🗣" + artist, title=title, caption=self.caption_link
            )

    def send_poll(self):
        log.info("Отправка опроса")
        self.bot.send_poll(self.chat_id, **self.post.poll, disable_notification=self.disable_notification)

    def send_splitted_message(self, bot, text, chat_id):
        log.debug("Sending splitted message")
        for i in range(len(text) - 1):
            bot.send_message(chat_id, text[i], disable_notification=self.disable_notification)
