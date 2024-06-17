from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('Components')

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
                pk_prefix = f'{category}#'  # 각 카테고리에 해당하는 PK prefix

                # 모든 항목을 불러오는 scan 사용
                scan_kwargs = {
                    'FilterExpression': "begins_with(#pk, :pk_prefix)",
                    'ExpressionAttributeNames': {
                        '#pk': 'Type#ComponentID'
                    },
                    'ExpressionAttributeValues': {
                        ':pk_prefix': pk_prefix
                    },
                    'Limit': limit
                }

                if last_evaluated_keys.get(category):
                    scan_kwargs['ExclusiveStartKey'] = last_evaluated_keys[category]

                response = table.scan(**scan_kwargs)
                data = response.get('Items', [])
                # DATE를 기준으로 정렬하여 최신 데이터부터 가져옵니다.
                sorted_data = sorted(data, key=lambda x: x['DATE'], reverse=True)
                results[category] = sorted_data[:limit]
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
        pk = data.get('PK')
        sk = data.get('SK')

        if not pk or not sk:
            return Response({'error': 'PK and SK are required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = table.get_item(
                Key={
                    'PK': pk,
                    'SK': sk
                }
            )

            item = response.get('Item', {})
            return Response({
                'data': item
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
