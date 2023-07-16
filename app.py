import json
import os

from dotenv import load_dotenv
import chainlit as cl
import requests

from langchain import PromptTemplate, LLMChain
from langchain.tools import Tool
from langchain.agents import initialize_agent

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")
from langchain.tools import DuckDuckGoSearchRun

load_dotenv()

is_first_question_asked = False
is_second_question_asked = False
is_third_question_asked = False

is_match_response_from_endpoint = False

first_question = "What's your zip code?"
second_question = "What is your current car insurance company?"
third_question = "What is your name?"
decline_message = "Thank you for your time! You're not suitable for the insurance quote!"
success_message = "Thank you for your time. We will email you with a insurance quote!"

first_question_answer = ''
second_question_answer = ''
third_question_answer = ''

prompt_template = """
 You are an AI insurance bot that will help users save money on your auto insurance.
 If the user provides a zip code that does not have 5 digits,
 respond with the exact message: - "Your answer is not valid".
 Otherwise, continue the conversation.
   {input}?
"""

search = DuckDuckGoSearchRun()
search_tool = Tool(name="search_tool", description = "search the net",func = search.run)

tools=[search_tool]

agent = initialize_agent(tools=tools, llm=llm,
                         agent='zero-shot-react-description',
                         verbose=True)


@cl.langchain_factory(use_async=True)
def main():
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))
    return chain


@cl.on_chat_start
async def main():
    greeting = f"""
    Hello, I am an AI insurance bot that will help you save money on your auto insurance. 
    Let's start. {first_question}
    """
    await cl.Message(content=greeting).send()


@cl.langchain_postprocess
async def postprocess(output: str):
    global is_first_question_asked
    global is_second_question_asked
    global is_third_question_asked

    global first_question_answer
    global second_question_answer
    global third_question_answer

    print(output)

    user_input = output['input']
    ai_response = output['text']

    if not is_first_question_asked:
        if not validate_ai_response(ai_response):
            await cl.Message(content=str(ai_response)).send()
            await cl.Message(content=str(first_question)).send()
        else:
            first_question_answer = user_input
            if not chech_fountain_header({"zip_code":  f"{user_input}"}):
                reset_global_variabes()
                await cl.Message(content=decline_message).send()
            else:
                return_message = second_question
                is_first_question_asked = True
                await cl.Message(content=return_message).send()
    elif not is_second_question_asked:
        if not validate_ai_response(ai_response):
            await cl.Message(content=str(ai_response)).send()
            await cl.Message(content=str(second_question)).send()
        else:
            second_question_answer = user_input
            if not chech_fountain_header({"zip_code":  f"{first_question_answer}", "current_insurance_company":  f"{user_input}"}):
                reset_global_variabes()
                await cl.Message(content=decline_message).send()
            else:
                return_message = third_question
                is_second_question_asked = True
                await cl.Message(content=return_message).send()
    elif not is_third_question_asked:
        if not validate_ai_response(ai_response):
            await cl.Message(content=str(ai_response)).send()
            await cl.Message(content=str(third_question)).send()
        else:
            third_question_answer = user_input
            if not chech_fountain_header({"zip_code":  f"{first_question_answer}", "current_insurance_company":  f"{second_question_answer}", "name":  f"{third_question_answer}"}):
                reset_global_variabes()
                await cl.Message(content=decline_message).send()
            else:
                is_third_question_asked = True
                await cl.Message(content=success_message).send()


def validate_ai_response(ai_response):

    if ai_response.__contains__("answer is not valid") or ai_response.__contains__("Invalid"):
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
