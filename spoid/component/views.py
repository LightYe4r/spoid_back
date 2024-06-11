from django.shortcuts import render
from pymongo import MongoClient
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
client = MongoClient("mongodb://localhost:27017/")
db = client['spoid']

def insert_data(request):
    data = {
        'name': request.POST['name'],
        'age': request.POST
    }
    db['data'].insert_one(data)
    return render(request, 'index.html')

class dataAPIView(APIView):
    def post(self, request):
        data = request.data
        db['data'].insert_one(data)
        return Response('Data inserted successfully')
    
    def get(self, request):
        data = db['data'].find()
        return Response(data)
    