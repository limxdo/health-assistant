#!/usr/bin/env python3

import sys
import signal
from time import sleep
import json

from difflib import SequenceMatcher

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

CONFIG_FILE = "/etc/health_assistant/config.json"

running = True
conversation = None

try:
    def handler(signum, frame):
        global running
        running = False

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    # get API_KEY & AGENT_ID
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    API_KEY = config["API_KEY"]
    AGENT_ID = config["AGENT_ID"]

    # check if env vars not found
    if not API_KEY:
        print("fatal error: env 'ELEVENLABS_API_KEY' not found", file=sys.stderr)
        sys.exit(1)

    if not AGENT_ID:
        print("fatal error: env: 'ELEVENLABS_AGENT_ID' not found", file=sys.stderr)
        sys.exit(1)


    # client
    client = ElevenLabs(api_key=API_KEY)
    last_agent_response = ""

    # ignore echo
    def is_echo_from_agent(user_text):
        if not last_agent_response:
            return False

        clean_user_text = user_text.strip().lower()
        clean_agent_text = last_agent_response.strip().lower()
        if len(clean_user_text) < 8 or len(clean_agent_text) < 8:
            return False

        similarity = SequenceMatcher(None, clean_user_text, clean_agent_text).ratio()
        return similarity >= 0.55 or clean_user_text in clean_agent_text or clean_agent_text in clean_user_text

    def handle_user_transcript(text):
        if is_echo_from_agent(text):
            print("User transcript: echo detected")
        else:
            print(f"User transcript: {text}")


    def handle_agent_response(text):
        global last_agent_response
        last_agent_response = text
        print("Agent response:", text)


    print("Use your microphone to talk.")

    conversation = Conversation(
        client=client,
        agent_id=AGENT_ID,
        requires_auth=True,
        audio_interface=DefaultAudioInterface(),
        callback_user_transcript=handle_user_transcript,
        callback_agent_response=handle_agent_response,
    )

    # start session
    conversation.start_session()

    while running:
        # can do anything here (non-blocking)
        sleep(0.5)


    # session ending
    if conversation is not None:
        try:
            conversation.end_session()
        except Exception as e:
            print(f"error ending the session: {e}", file=sys.stderr)

except Exception as e:
    print(f"error: {e}", file=sys.stderr)

sys.exit(0)
