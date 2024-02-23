import json
import boto3


def lambda_handler(event, context):
    print(f">>>>>>>>>>>> ${event}")

    # Bedrock version check
    boto3_version = boto3.__version__
    print(f">>>>>>>>>>>> boto3 version: {boto3_version}")

    try:
        if event["requestContext"]["http"]["method"] == "GET":
            return done(None, "'/' path로 GET 요청을 하셨군요.")

        # Bedrock runtime
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime", region_name="us-east-1"
        )

        request_body = json.loads(event.get("body"))
        prompt = (
            request_body.get("prompt")
            if "prompt" in request_body
            else "Amazon Bedrock이 뭐야? 3문장 이내로 답변해"
        )
        print(f">>>>>>>>>>>> prompt: {prompt}")

        # Anthropic의 Claude 모델 사용
        # 한국어를 비교적 잘 지원
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html
        body = json.dumps(
            {
                "prompt": f"\n\nHuman:{prompt}\n\nAssistant:",
                "temperature": 0,
                "top_p": 0.01,
                "max_tokens_to_sample": 1000,
            }
        )

        # buffered
        response = bedrock_runtime.invoke_model(
            body=body, modelId="anthropic.claude-v2"
        )
        response_body = json.loads(response.get("body").read())
        model_response = response_body["completion"]
        print(f">>>>>>>>>>>> model output: {model_response}")
        return done(None, {"output": model_response})
    except Exception as e:
        return done(e, "Error occured!")


def done(err, res):
    if err:
        print(f"!!!!!!!!!!!!{err}")

    return {
        "statusCode": "400" if err else "200",
        # 한글 깨짐을 방지하기 위해 ensure_ascii 옵션 추가
        "body": json.dumps(res, ensure_ascii=False),
        "headers": {"Content-Type": "application/json"},
    }