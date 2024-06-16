# 예시: views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3

class InsertDataAPIView(APIView):

    def post(self, request):
        data_to_insert = request.data  # POST 요청으로 넘어온 데이터를 가져옵니다.

        # 예시 데이터 유효성 검사
        if not isinstance(data_to_insert, dict):
            return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

        # DynamoDB에 데이터 삽입
        try:
            dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
            table = dynamodb.Table('PC_Components')

            response = table.put_item(
                Item=data_to_insert
            )

            return Response({'message': 'Data inserted successfully', 'response': response}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
