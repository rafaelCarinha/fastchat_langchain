import json
import os

from dotenv import load_dotenv
import chainlit as cl
import requests

from langchain import PromptTemplate, LLMChain

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")

load_dotenv()

prompt_template = """
name: Assistant
greeting: Hello, I am an AI insurance bot that will help you save money on your auto
  insurance. Let's start. What is your zip code?
{input}?
"""

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


# @cl.on_chat_start
# async def main():
#     greeting = """
#     Hello, I am an AI insurance bot that will help you save money on your auto
#     insurance. Let's start. What is your zip code?
#     """
#     await cl.AskUserMessage(content=greeting, timeout=10).send()


@cl.on_chat_start
def main():
    await cl.AskUserMessage(content="Hello, I am an AI insurance bot that will help you save money on your auto insurance. Let's start. What is your zip code?", timeout=10).send()


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
    #if validate_ai_response(ai_response):
    #await cl.Message(content=ai_response).send()

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


def validate_ai_response(ai_response):

    if ai_response.__contains__("is not a valid zip code"):
        return False
    else:
        return True


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
