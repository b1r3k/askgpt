import spacy
import sys
from pprint import pprint

from transformers import GPT2TokenizerFast


class Chapter:
	def __init__(self, title: str):
		self.title = title
		self.sentences = []

	def add_sentence(self, sentence: list):
		self.sentences += sentence

	def __repr__(self):
		return f"Chapter({self.title!r}, {self.sentences!r})"

	def __str__(self):
		return f"{self.title}\n\n{' '.join(self.sentences)}"


def get_paragraphs_from_text(text):
	nlp = spacy.load("en_core_web_lg")
	doc = nlp(text)
	assert doc.has_annotation("SENT_START")

	paragraphs = []
	paragraph = []
	for sent in doc.sents:
		paragraph.append(sent.text)
		if sent.text.endswith('\r\n\n'):
			paragraphs.append(paragraph)
			paragraph = []
	return paragraphs


def get_chunks_from_paragraphs(text, max_chunk_tokens=4097):
	tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
	current_chunk = []
	for paragraph in get_paragraphs_from_text(text):
		paragraph_text = ' '.join(paragraph)
		potential_chunk = ' '.join(current_chunk + [paragraph_text])
		if len(tokenizer(potential_chunk).input_ids) < max_chunk_tokens:
			current_chunk.append(paragraph_text)
		else:
			yield ''.join(current_chunk)
			current_chunk = [paragraph_text]
	if len(current_chunk) > 0:
		yield ''.join(current_chunk)

