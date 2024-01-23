# -*- coding: utf-8 -*-
import asyncio
from typing import List, Optional

from global_logger import Log
from litellm import completion
from telethon import events
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient

from . import env

LOG = Log.get_logger()


def ask_assistant(strings: List[str], api_base=env.LLM_API_BASE, model=env.LLM_MODEL) -> Optional[str]:
    messages = [{"content": _, "role": "user"} for _ in strings]
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
    try:
        client = TelegramClient(str(session_file), api_id, api_hash)
        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            verification_code = input('Enter the code: ')
            try:
                await client.sign_in(phone_number, verification_code)
            except SessionPasswordNeededError:
                two_step_verif_password = input('Two-step verification is enabled. Please enter your password: ')
                await client.sign_in(password=two_step_verif_password)

        return client

    except Exception as e:
        raise e


async def main():
    LOG.verbose = True
    session_path = env.DATA_PATH / 'session'
    client = await setup_telethon(env.TELEGRAM_API_ID, env.TELEGRAM_API_HASH,
                                  env.TELEGRAM_PHONE, session_path)
    if not client:
        LOG.error("Error setting up the client.")
        return

    LOG.green("Telethon client set up successfully.")
    report_chat_id = env.REPORT_CHAT_ID
    report_chat = await client.get_entity(report_chat_id)
    LOG.debug(f"Report chat {report_chat_id}: {getattr(report_chat, 'title', getattr(report_chat, 'username'))}")

    LOG.green(f"Listening for messages in chats {env.TELEGRAM_CHAT_IDS}")

    @client.on(events.NewMessage(chats=env.TELEGRAM_CHAT_IDS))
    async def _(event):
        sender = await event.get_sender()
        message = event.message.text
        LOG.debug(f"Received message from {sender.title}:\n{message}\n--------")
        assistant_response = ask_assistant([message])
        if assistant_response and 'yes' in assistant_response.lower()[:10]:
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
