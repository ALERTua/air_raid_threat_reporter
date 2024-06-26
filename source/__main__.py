# -*- coding: utf-8 -*-
import asyncio
from typing import List, Optional
from pathlib import Path
from global_logger import Log
from litellm import completion
from telethon import events, TelegramClient as TelegramClient_async
from telethon.types import User
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient as TelegramClient_sync

DOCKER = Path('/.dockerenv').exists()

try:
    from . import env
except:
    import env

LOG = Log.get_logger()


def ask_assistant(strings: List[str], api_base=env.LLM_API_BASE, model=env.LLM_MODEL) -> Optional[str]:
    messages = [{"content": _, "role": "user"} for _ in strings]
    # import litellm
    # litellm.set_verbose = True
    response = completion(
        model=model,
        messages=messages,
        api_base=api_base,
    )
    if response.choices:
        text_response = response.choices[0].model_extra.get('message', dict()).get('content', '')
        if text_response:
            text_response = text_response.strip().replace('<SYS>', '').replace('</SYS>', '')
            text_response = text_response.strip()
            LOG.debug(f"Assistant response: {text_response}")
        return text_response


async def setup_telethon(api_id, api_hash, phone_number, session_file='./session'):
    LOG.debug("Setting up Telethon")
    try:
        client = TelegramClient_sync(str(session_file), api_id, api_hash)
        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            if DOCKER:
                LOG.warning("User interaction is needed. "
                            "Please attach to the Docker container using 'docker attach container_name'"
                            " and provide the code you received in Telegram.")
            verification_code = input('Enter the code: ')
            try:
                await client.sign_in(phone_number, verification_code)
            except SessionPasswordNeededError:
                if DOCKER:
                    LOG.warning("User interaction is needed. "
                                "Please attach to the Docker container using 'docker attach container_name'"
                                " and provide the 2FA password.")
                two_step_verif_password = input('Two-step verification is enabled. Please enter your password: ')
                await client.sign_in(password=two_step_verif_password)

        return client

    except Exception as e:
        raise e


async def main():
    reader_session_path = env.DATA_PATH / 'session'
    client = await setup_telethon(env.TELEGRAM_API_ID, env.TELEGRAM_API_HASH,
                                  env.TELEGRAM_PHONE, reader_session_path)
    if not client:
        LOG.error("Error setting up Telethon.")
        return

    LOG.green("Telethon client set up successfully.")

    # noinspection PyTypeChecker
    reporter = None
    if env.TELEGRAM_BOT_API_TOKEN:
        client_reporter = TelegramClient_async('bot_session', env.TELEGRAM_API_ID, env.TELEGRAM_API_HASH)
        # noinspection PyUnresolvedReferences
        reporter = await client_reporter.start(bot_token=env.TELEGRAM_BOT_API_TOKEN)  # type: TelegramClient_async

    report_chat_id = env.REPORT_CHAT_ID
    report_chat = await client.get_entity(report_chat_id)
    LOG.debug(f"Report chat {report_chat_id}: {getattr(report_chat, 'title', getattr(report_chat, 'username'))}")

    LOG.green(f"Listening for messages in chats {env.TELEGRAM_CHAT_IDS}")

    @client.on(events.NewMessage(chats=env.TELEGRAM_CHAT_IDS))
    async def _(event):
        sender: User = await event.get_sender()
        message = event.message.text
        if reporter:
            reporter_me: User = await reporter.get_me()
            if sender.id == reporter_me.id:
                return

        if message.startswith('test'):
            message = message.replace('test ', '')
        elif len(message) < 30:
            LOG.debug(f"Message too short: {message}. Skipping")
            return
        else:
            me = await event.client.get_me()
            if sender == me:
                return

        author = getattr(sender, 'title', getattr(sender, 'username'))
        LOG.debug(f"Received message from {author}:\n{message}\n--------")
        assistant_response = ask_assistant([message])
        if assistant_response and 'yes' in assistant_response.lower()[:10]:
            if reporter:
                msg = f"{author}:\n{message}"
                reporter_chat = await reporter.get_entity(report_chat_id)
                await reporter.send_message(entity=reporter_chat, message=msg)
            else:
                await event.message.forward_to(entity=report_chat)

    await client.disconnected
    LOG.yellow("Client disconnected. Exiting")


def checks():
    assert env.DATA_PATH.exists(), "Please define DATA_PATH env variable"
    assert env.TELEGRAM_CHAT_IDS, "Please define TELEGRAM_CHAT_IDS env variable"
    assert env.TELEGRAM_PHONE, "Please define TELEGRAM_PHONE env variable"
    assert env.TELEGRAM_API_ID, "Please define TELEGRAM_API_ID env variable"
    assert env.TELEGRAM_API_HASH, "Please define TELEGRAM_API_HASH env variable"
    assert env.REPORT_CHAT_ID, "Please define REPORT_CHAT_ID env variable"
    assert env.LLM_API_BASE, "Please define LLM_API_BASE env variable"
    assert env.LLM_MODEL, "Please define LLM_MODEL env variable"


if __name__ == '__main__':
    checks()
    asyncio.run(main())
