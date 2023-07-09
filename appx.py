from flask import Flask, request, json, Response
from pymongo import MongoClient
import sys
import random
app = Flask(__name__)

from bson import json_util

def parse_json(data):
    return json.loads(json_util.dumps(data))

class MongoAPI:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:5000/")  
      
        database = 'CoRiders'
        collection = 'People'
        cursor = self.client[database]
        self.collection = cursor[collection]
        # self.data = data


    def read(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output
    
    def readd(self,id):
        documents = self.collection.find_one({'id' : int(id)})
        output = [{item: documents[item] for item in documents if item != '_id'}]
        return output

    def write(self, data):
        new_document = data['Document']
       

        if len(new_document) == 3 and 'name' in new_document and 'email' in new_document and 'password' in new_document: 
            print(len(new_document),file=sys.stderr)
            random_number = random.randint(1, 100000)
            new_document["id"] = random_number
            print(new_document,file=sys.stderr)
            response = self.collection.insert_one(new_document)
            output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
            return output
        else :
            return {'Status' : 'Not Inserted Enter correct info'}

    def update(self, data):
        filt = data['Filter']
        print(filt,file=sys.stderr)
        updated_data = {"$set": data['DataToBeUpdated']}
        response = self.collection.update_one( filt,updated_data)
        print(filt,file=sys.stderr)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output

    def delete(self, data):
        filt = data['Filter']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output


@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "App is started"}),
                    status=200,
                    mimetype='application/json')



@app.route('/user', methods=['GET'])
def DBread():
    obj1 = MongoAPI()
    response = obj1.read()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')



@app.route('/users/<id>', methods=['GET'])
def DBreadd(id):
    
    # print(data,file=sys.stderr)
    obj1 = MongoAPI()
    response = obj1.readd(id)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/users', methods=['POST'])
def DBwrite():
    data = request.json
    if 'Document' not in data:
        return Response(response=json.dumps({"Error": "Please provide document information"}),status=400,mimetype='application/json')
    obj1 = MongoAPI()
    response = obj1.write(data)
    return Response(response=json.dumps(response), status=200, mimetype='application/json')



@app.route('/users/<id>', methods=['PUT'])
def DBupdate(id):
    data = request.json
    data['Filter'] = {'id' : int(id)}
    if 'Filter' not in data and  'DataToBeUpdated' not in data:
        return Response(response=json.dumps({"Error": "Please provide filter and data to be updated"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI()
    response = obj1.update(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')



@app.route('/users/<id>', methods=['DELETE'])
def DBdelete(id):
    data = request.json
    data['Filter'] = {'id' : int(id)}
    if 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide filter"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI()
    response = obj1.delete(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')




if __name__ == '__main__':
    mongo_obj = MongoAPI()
    app.run(debug=True, port=5001, host='0.0.0.0')