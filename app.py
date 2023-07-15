import json
import os

from dotenv import load_dotenv
import chainlit as cl
import requests

from langchain import PromptTemplate, LLMChain, OpenAI

from langchain.llms import LlamaCpp
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
loader = TextLoader("state_of_the_union.txt")
index = VectorstoreIndexCreator(embedding=embedding).from_loaders([loader])
#llm = ChatOpenAI(model="gpt-3.5-turbo")

n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
    model_path="/home/rafaelmarins/.cache/huggingface/hub/models--lmsys--vicuna-7b-v1.3/snapshots/30a07c35c99b04617243200163e77e6c569f7e5d/pytorch_model-00001-of-00002.bin",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    callback_manager=callback_manager,
    verbose=True,
)
#
# questions = [
#     "What is your LLM model",
#     "What is your AI Model"
# ]
#
# for query in questions:
#     print("Query:", query)
#     print("Answer:", index.query(query, llm=llm))


load_dotenv()

prompt_template = "{input}?"

is_first_question_asked = False
is_second_question_asked = False
is_third_question_asked = False

is_match_response_from_endpoint = False

first_question = "What's your zip code?"
second_question = "Do you work in tech? (yes/no)"
third_question = "Which company did you last work for? (google, facebook, openai, microsoft)"
decline_message = "Thank you for your time! You're not suitable for the position"
success_message = "Thank you for your time! You have been selected for the position"

first_question_answer = ''
second_question_answer = ''
third_question_answer = ''


@cl.langchain_factory(use_async=True)
def main():
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))
    return chain


@cl.langchain_postprocess
async def postprocess(output: str):
    global is_first_question_asked
    global is_second_question_asked
    global is_third_question_asked

    global first_question_answer
    global second_question_answer
    global third_question_answer

    user_input = output['input']
    ai_response = output['text']
    print(output)
    return_message = ''
    if not is_first_question_asked:
        return_message = first_question
        is_first_question_asked = True
        await cl.Message(content=return_message).send()
    elif not is_second_question_asked:
        first_question_answer = user_input
        if not chech_fountain_header({"zip_code":  f"{user_input}"}):
            reset_global_variabes()
            await cl.Message(content=decline_message).send()
        else:
            return_message = second_question
            is_second_question_asked = True
            await cl.Message(content=return_message).send()
    elif not is_third_question_asked:
        second_question_answer = user_input
        if not chech_fountain_header({"zip_code":  f"{first_question_answer}", "work_tech":  f"{user_input}"}):
            reset_global_variabes()
            await cl.Message(content=decline_message).send()
        else:
            return_message = third_question
            is_third_question_asked = True
            await cl.Message(content=return_message).send()
    elif is_third_question_asked:
        third_question_answer = user_input
        reset_global_variabes()
        if not chech_fountain_header({"zip_code":  f"{first_question_answer}", "work_tech":  f"{second_question_answer}", "company":  f"{third_question_answer}"}):
            await cl.Message(content=decline_message).send()
        else:
            await cl.Message(content=success_message).send()


def chech_fountain_header(body):
    print(body)

    response = requests.post("https://chatgpt.fountainheadme.com/api/screener", json=body)
    print(response.text)
    if response.text == '{"status":"match"}':
        return True
    elif response.text == '{"status":"dump"}':
        return False


def reset_global_variabes():
    global is_first_question_asked
    global is_second_question_asked
    global is_third_question_asked

    is_first_question_asked = False
    is_second_question_asked = False
    is_third_question_asked = False