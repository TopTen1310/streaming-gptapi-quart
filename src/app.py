import asyncio
import logging
import os
import json

from dotenv import load_dotenv
from quart import Quart, jsonify, request, Response, make_response
from quart.helpers import stream_with_context

from log import init_logging

load_dotenv()
init_logging()
logger = logging.getLogger(__name__)

app = Quart(__name__)

from datetime import date

import openai


@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    await openai.create_session(loop)


@app.after_serving
async def shutdown():
    await openai.teardown()


# For healthchecks
@app.route("/")
def index():
    return "ok"


@app.route("/chat", methods=["POST"])
async def get_response_stream():
    body = await request.get_json()
    messages = body["messages"]
    model = body["model"]
    temperature = body["temperature"]
    top_p = body["top_p"]
    max_tokens = body["max_tokens"]
    frequency_penalty = body["frequency_penalty"]
    presence_penalty = body["presence_penalty"]

    response = await make_response(openai.get_chat_completion_stream(
        messages, 
        model,
        temperature,
        top_p,
        max_tokens,
        frequency_penalty,
        presence_penalty
    ))
    response.timeout = None  # No timeout for this route

    return response