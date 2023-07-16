import json
import os

from dotenv import load_dotenv
import chainlit as cl
import requests

from langchain import PromptTemplate, LLMChain

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")

load_dotenv()

is_first_question_asked = False
is_second_question_asked = False
is_third_question_asked = False

questions_dict = {
    1: "Are you currently insured?",
    2: "Have you had insurance coverage for at least the last 12 months?",
    3: "What is your current car insurance company?",
    4: "What's your zip code?",
    5: "Is your drivers license currently in good standing?",
    6: "Have you had 1 or more DUI’s in the last 7 years?",
    7: "Do you own your home?",
}

questions_attribute_dict = {
    1: "currently_insured",
    2: "insurance_coverage_12_months",
    3: "current_car_insurance_company",
    4: "zip_code",
    5: "drivers_license_in_good_standing?",
    6: "had_duis",
    7: "own_your_home",
}

questions_answer_dict = {
    1: "",
    2: "",
    3: "",
    4: "",
    5: "",
    6: "",
    7: "",
}

decline_message = "Thank you for your time! You're not suitable for the insurance quote!"
success_message = "Thank you for your time. We will email you with a insurance quote!"

prompt_template = """
 You are an AI insurance bot that will help users save money on your auto insurance.
 If the user provides a non-logical answer,
 respond with the exact message: - "Your answer is not valid".
 Otherwise, continue the conversation.
   {input}?
"""


@cl.langchain_factory(use_async=True)
def main():
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))
    return chain


@cl.on_chat_start
async def main():
    greeting = f"""
    Hello, I am an AI insurance bot that will help you save money on your auto insurance. 
    Let's start. 
    {questions_dict[1]}
    """
    await cl.Message(content=greeting).send()


@cl.langchain_postprocess
async def postprocess(output: str):

    print(output)

    user_input = output['input']
    ai_response = output['text']

    if len(questions_answer_dict[1]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 1,
                                                 {f"{questions_attribute_dict[1]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[2]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 2,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[3]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 3,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{questions_answer_dict[2]}",
                                                  f"{questions_attribute_dict[3]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[4]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 4,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{questions_answer_dict[2]}",
                                                  f"{questions_attribute_dict[3]}": f"{questions_answer_dict[3]}",
                                                  f"{questions_attribute_dict[4]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[5]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 5,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{questions_answer_dict[2]}",
                                                  f"{questions_attribute_dict[3]}": f"{questions_answer_dict[3]}",
                                                  f"{questions_attribute_dict[4]}": f"{questions_answer_dict[4]}",
                                                  f"{questions_attribute_dict[5]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[6]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 6,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{questions_answer_dict[2]}",
                                                  f"{questions_attribute_dict[3]}": f"{questions_answer_dict[3]}",
                                                  f"{questions_attribute_dict[4]}": f"{questions_answer_dict[4]}",
                                                  f"{questions_attribute_dict[5]}": f"{questions_answer_dict[5]}",
                                                  f"{questions_attribute_dict[6]}": f"{user_input}"},
                                                 False
                                                 )
    elif len(questions_answer_dict[7]) == 0:
        await validate_ai_response_and_check_api(ai_response,
                                                 user_input,
                                                 7,
                                                 {f"{questions_attribute_dict[1]}": f"{questions_answer_dict[1]}",
                                                  f"{questions_attribute_dict[2]}": f"{questions_answer_dict[2]}",
                                                  f"{questions_attribute_dict[3]}": f"{questions_answer_dict[3]}",
                                                  f"{questions_attribute_dict[4]}": f"{questions_answer_dict[4]}",
                                                  f"{questions_attribute_dict[5]}": f"{questions_answer_dict[5]}",
                                                  f"{questions_attribute_dict[6]}": f"{questions_answer_dict[6]}",
                                                  f"{questions_attribute_dict[7]}": f"{user_input}"},
                                                 True)


async def validate_ai_response_and_check_api(ai_response, user_input, question_index, api_json_body, last_message):
    global questions_answer_dict
    if not validate_ai_response(ai_response):
        await cl.Message(content=str(ai_response)).send()
        await cl.Message(content=str(questions_dict[question_index])).send()
    else:
        questions_answer_dict[question_index] = user_input
        if not check_fountain_header(api_json_body):
            reset_global_variabes()
            await cl.Message(content=decline_message).send()
        else:
            if not last_message:
                return_message = questions_dict[question_index+1]
                await cl.Message(content=return_message).send()
            else:
                await cl.Message(content=success_message).send()


def validate_ai_response(ai_response):

    if ai_response.__contains__("answer is not valid") or ai_response.__contains__("Invalid"):
        return False
    else:
        return True


def check_fountain_header(body):
    print(body)

    response = requests.post("https://chatgpt.fountainheadme.com/api/screener", json=body)
    print(response.text)
    return True
    # TODO uncomment the following code when the API is ready and not returning random results
    # if response.text == '{"status":"match"}':
    #     return True
    # elif response.text == '{"status":"dump"}':
    #     return False


def reset_global_variabes():
    global is_first_question_asked
    global is_second_question_asked
    global is_third_question_asked

    is_first_question_asked = False
    is_second_question_asked = False
    is_third_question_asked = False

