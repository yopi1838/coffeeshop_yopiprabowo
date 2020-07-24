import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()
## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def return_drinks():
    try:
        #Coded by self at 2020/07/15 0:28 JST
        drinks_list = Drink.query.all()
        drinks = [drink.short() for drink in drinks_list]
        if drinks_list is None:
            abort(404)
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    #Created by self at 2020/07/15 22:22
    drinks = Drink.query.all() #show all drinks
    long_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": long_drinks
    }), 200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    #Created by self with help regarding json.dumps from https://knowledge.udacity.com/questions/69391
    body = request.get_json() #get input from user
    if body is None:
        abort(404)
    title = body.get('title', None) #name of the drink
    recipe = body.get('recipe', None) #recipe 
    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe)) 
        #encode the recipe into json format using json.dump
        new_drink.insert()
        drinks = [new_drink.long()] #take the long data representation
        return jsonify({
            'success': True,
            'drinks': drinks
        }),200
    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(jwt, drink_id):
    '''
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    #Coded by self at 2020/07/15 23:30
    try:
        edit_drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        body = request.get_json()
        edit_drink.title = body.get('title', None)
        recipe = json.dumps(body.get('recipe', None))
        if recipe is None:
            edit_drink.update()
        else:
            edit_drink.recipe = recipe
            edit_drink.update()
        drink = [edit_drink.long()]
        return jsonify({
            'success': True,
            'drinks': drink
        }), 200
    except Exception:
        abort(400)
    
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    try:
        delete_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if delete_drink is None:
            abort(404)
        delete_drink.delete()
        return jsonify({
            'success':True,
            'delete': drink_id
        })
    except:
        abort(422)
## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

@app.errorhandler(500)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
#Created with help from https://knowledge.udacity.com/questions/204223
@app.errorhandler(AuthError)
def authorization_error(e):
    error_tag = e.error
    error_statuscode = e.status_code
    return jsonify({
        'success': False,
        'error': error_statuscode,
        'message': error_tag['description']
    }), error_statuscode

    """
    manager's TOken:
    eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVQa3JDX3ZhV2duOWhacUhfNDlpWCJ9.eyJpc3MiOiJodHRwczovL2Rldi1ldTEzLW52ai51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwZGQ5N2IyZWIzMDMwMDE5Yzg3OGU1IiwiYXVkIjoiY29mZmVlc2hvcCIsImlhdCI6MTU5NTE3MzU5NSwiZXhwIjoxNTk1MTgwNzk1LCJhenAiOiIzdmJOTDVYMFAwOHJlUTFoMXFSZlNWODAyUjg5TkQzdSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MtZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.JbmeQ4Oxqt1hZuHzSTJgftYtPoltz-b5t7ipbrDY2TFC6HEXOTnELuQMM5iOEHXdPrTHkc7F-gx5R2HLc9FmZpHhXosdzo1R-oBpDv8FLEUYWBS_-5oo4trZxSFk_fg6VUanjrWgdgMxwL-4goeJuYdBpznCSkuQuPBDpR-q9OsUL0XpqJd_RRylmqUnL7sI6fxWQlqc8SqVhfIwNFWudA5WpwgZMRuY_E5Ajg1ONJ1dEGhV6n--e_HSZ26neYg8ZdihiAlBFnehAprpDdqU3xCSoHc_9ZKaRuayJmylFWQ-SlQiuND8CWV8u9qXTzwSOUZhOzhCRyUbuQ9o2HxIDQ

    barista's TOken:
    eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVQa3JDX3ZhV2duOWhacUhfNDlpWCJ9.eyJpc3MiOiJodHRwczovL2Rldi1ldTEzLW52ai51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwZGM3ODBmZDMwZTIwMDEzNjY3NDQ1IiwiYXVkIjoiY29mZmVlc2hvcCIsImlhdCI6MTU5NTE3NDM4MSwiZXhwIjoxNTk1MTgxNTgxLCJhenAiOiIzdmJOTDVYMFAwOHJlUTFoMXFSZlNWODAyUjg5TkQzdSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmRyaW5rcy1kZXRhaWwiXX0.K8bOawHKdQwNoZQTooE8OGuGLF0A1-vwJJB4qSns5OnPU-1z2MrnnlGulkqSyTn2AGLTNHhUOo2I7Cnd52-5K20zuwVIIbXTyy35fDZNHsWqhVQlYHghLtO4z7YQIIp5ltXZM9tmi28ija5Z23PybLAHkggo3vr7L3mTgbjietO4r9mCP9ZAytaixpUALlFkT5-f4MWEOkHCkhRNlQaQV1Z8nOBy7vo_pNKRpuZPHs2R7Of4h9KzhyhRYvTKVKb3aiRWhiBQTx_hmHnJs95ohzJVFgxIA8lHxU4NAJrIA7tOlizBFjCNgrgVOYyxWEuuaWRlTaJBFEda1uXR8mMJcw
    """