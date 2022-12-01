import os
import sys
import logging
from pprint import pprint
import argparse
import math

import openai
from transformers import GPT2TokenizerFast

from .chunking import get_chunks_from_paragraphs

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# initialize logger with output set to standard error
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)


def gpt_complete(prompt, *,
                 engine="text-davinci-002",
                 temperature=0.3,
                 max_tokens=256,
                 top_p=0.9,
                 frequency_penalty=0,
                 presence_penalty=0,
                 stop=["```output"]):
    completion = openai.Completion.create(prompt=prompt,
                                          engine=engine, temperature=temperature,
                                          max_tokens=max_tokens,
                                          top_p=top_p,
                                          frequency_penalty=frequency_penalty,
                                          presence_penalty=presence_penalty,
                                          stop=stop)
    for idx, completion_choice in enumerate(completion.choices):
        return completion_choice.text.strip()


def main():
    args_parser = argparse.ArgumentParser(description="GPT CLI")
    args_parser.add_argument('--max-tokens', default=256, type=int, help="Max tokens per request response")
    args_parser.add_argument('--summarize', action='store_true', help="Use summarization template & split if necessary")
    args_parser.add_argument('--compression-multiplier', default=0, type=int,
                             help="Ratio between input size and output size controls granularity of summary")

    args = args_parser.parse_args()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        logger.error("Please set OPENAI_API_KEY environment variable")
        sys.exit(1)
    if args.summarize:
        logger.debug('Using summarization template')

    if args.compression_multiplier > 16:
        logger.error("Compression multiplier too large, max is 16")
        sys.exit(1)

    if args.compression_multiplier == 0:
        compression_multiplier = math.floor(4097 / args.max_tokens)
    else:
        compression_multiplier = args.compression_multiplier

    prompt = sys.stdin.readlines()
    text = '\n'.join(prompt)
    text_token_size = len(tokenizer(text)['input_ids'])
    logger.debug(f"** Input text token size: {text_token_size}")

    prepend = ""
    prepend_token_size = 0
    if args.summarize:
        prepend = "Write a concise summary of the following text:\n\n"
        prepend_token_size = len(tokenizer(prepend)['input_ids'])
    max_chunk_size = (compression_multiplier * args.max_tokens) - args.max_tokens * 2 - prepend_token_size * 2
    full_response = []
    for idx, chunk in enumerate(get_chunks_from_paragraphs(text, max_chunk_size)):
        if idx > 0:
            question = f"""
            Given summary of previous text, write a concise summary of the following 
            text:
            {chunk}
            
            Summary of previous text:
            {response}
            """
        else:
            question = prepend + chunk
        question = question.strip()
        logger.debug('Prompt: %s\n***\n', question)
        response = gpt_complete(question, engine="text-davinci-003", max_tokens=args.max_tokens)
        full_response.append(response)
    full_response_text = '\n'.join(full_response)
    full_response_token_size = len(tokenizer(full_response_text)['input_ids'])
    print(full_response_text)
    logger.debug(f"** Output text token size: {full_response_token_size}")
    logger.info("** Compression: {:.2f}%".format(100 * (1 - full_response_token_size / text_token_size)))
