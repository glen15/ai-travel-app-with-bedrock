import json
import logging
import boto3
import os

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 액세스 정보
aws_access_key_id = os.environ.get("ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("SECRET_ACCESS_KEY")


def lambda_handler(event, context):
    # event 변수에서 요청의 본문을 추출하고, 문자열을 JSON 객체로 파싱
    body_str = event.get("body")
    # 요청 본문의 인코딩 문제를 해결하기 위해, 문자열을 JSON 객체로 파싱
    body = json.loads(body_str)
    logger.info("Received request body: %s", body)
    print(body)

    # Bedrock 클라이언트 생성 시 AWS 자격 증명 포함
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    response = bedrock.invoke_model(
        modelId="amazon.titan-image-generator-v1", body=json.dumps(body)
    )
    base64_image_data = json.loads(response["body"].read())["images"][0]
    print("이미지 생성 완료")

    # # 예시 응답
    return {"statusCode": 200, "body": json.dumps({"image": base64_image_data})}
