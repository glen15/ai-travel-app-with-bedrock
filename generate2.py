import json
import boto3
import os
import base64
import random
import requests
from database import insert_travel_plan


def invoke_model(prompt, model_id, max_tokens=1024):
    body = json.dumps(
        {
            "prompt": prompt,
            "temperature": 0,
            "top_p": 0.01,
            "max_tokens_to_sample": max_tokens,
        }
    )
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1"
    )
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    return json.loads(response.get("body").read())["completion"]


def kor_to_eng(text):
    prompt = f"\n\nHuman:Translate '{text}' into English\n\nAssistant:"
    lambda_url = (
        "https://7qbhssw74q5rj54igax7phwo2i0rpmpu.lambda-url.ap-northeast-2.on.aws/"
    )
    response = requests.post(lambda_url, json=prompt)
    response_data = response.json()
    ai_result = response_data["message"]
    print(f"번역결과{ai_result}")

    return ai_result


def generate_plan(place, duration, purpose):
    prompt = f"\n\nSystem:You are an expert in creating travel plans\n\nHuman:Create a travel plan for {purpose} during {duration} in {place} Make sure to speak in Korean\n\nAssistant:"
    insert_travel_plan(place, duration, purpose)
    lambda_url = (
        "https://7qbhssw74q5rj54igax7phwo2i0rpmpu.lambda-url.ap-northeast-2.on.aws/"
    )
    response = requests.post(lambda_url, json=prompt)
    response_data = response.json()
    ai_result = response_data["message"]
    print(f"계획 : {ai_result}")

    return ai_result


def generate_image(place):
    seed = random.randint(0, 2147483647)
    text = kor_to_eng(
        f"{place}를 대표하는 상징의 이미지를 포함한 여행 포스터를 생성해라"
    )
    prompt = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": text},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "quality": "standard",
            "cfgScale": 7.5,
            "height": 512,
            "width": 512,
            "seed": seed,
        },
    }
    lambda_url = (
        "https://3blatsqw4hzdvhjlxwc3k7yvri0euoqq.lambda-url.ap-northeast-2.on.aws/"
    )
    response = requests.post(lambda_url, json=prompt)
    response_data = response.json()
    base64_image_data = response_data["image"]

    output_folder = "generated_images"
    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, f"image.png")
    with open(file_path, "wb") as file:
        file.write(base64.b64decode(base64_image_data))
    return file_path


def bedrock_chat(ai_result, prompt):
    prompt = (
        f"System:{ai_result}에 기반해서 질문에 대답해라\n\nHuman:{prompt}\n\nAssistant:"
    )
    lambda_url = (
        "https://7qbhssw74q5rj54igax7phwo2i0rpmpu.lambda-url.ap-northeast-2.on.aws/"
    )
    response = requests.post(lambda_url, json=prompt)
    response_data = response.json()
    ai_result = response_data["message"]
    print(f"대화 : {ai_result}")
    return ai_result
