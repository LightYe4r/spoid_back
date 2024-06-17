from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('PC_Components')

class InsertDataAPIView(APIView):

    def post(self, request):
        data_to_insert = request.data  # POST 요청으로 넘어온 데이터를 가져옵니다.

        # 예시 데이터 유효성 검사
        if not isinstance(data_to_insert, dict):
            return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

        # DynamoDB에 데이터 삽입
        try:
            response = table.put_item(
                Item=data_to_insert
            )

            return Response({'message': 'Data inserted successfully', 'response': response}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilteredDataAPIView(APIView):

    def post(self, request):
        data = request.data
        categories = data.get('categories', [])
        last_evaluated_keys = data.get('last_evaluated_keys', {})
        limit = 10

        if not categories:
            return Response({'error': 'Categories are required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        results = {}
        new_last_evaluated_keys = {}
        try:
            for category in categories:
                query_kwargs = {
                    'KeyConditionExpression': "#category = :category",
                    'ExpressionAttributeNames': {
                        '#category': 'Category'
                    },
                    'ExpressionAttributeValues': {
                        ':category': category
                    },
                    'Limit': limit,
                    'ScanIndexForward': False  # 역순으로 정렬하여 최신 데이터부터 가져옵니다.
                }

                if last_evaluated_keys.get(category):
                    query_kwargs['ExclusiveStartKey'] = last_evaluated_keys[category]

                response = table.query(**query_kwargs)
                data = response.get('Items', [])
                results[category] = sorted(data, key=lambda x: x['ComponentID'], reverse=True)
                new_last_evaluated_keys[category] = response.get('LastEvaluatedKey', None)

            return Response({
                'data': results,
                'last_evaluated_keys': new_last_evaluated_keys
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DetailDataAPIView(APIView):

    def post(self, request):
        data = request.data
        category = data.get('Category')
        component_id = data.get('ComponentID')

        if not component_id:
            return Response({'error': 'Component ID is required parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = table.get_item(
                Key={
                    'Category': category,
                    'ComponentID': component_id
                }
            )

            item = response.get('Item', {})
            return Response({
                'data': item
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)