#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import pymysql.cursors
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import settings # Our server and db settings, stored in settings.py

app = Flask(__name__)
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'banjoKazooie'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)



####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class Login(Resource):
	#
	# Login, start a session and set/return a session cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Casper", "password": "cr*ap"}'
	#  	-c cookie-jar http://cs3103.cs.unb.ca:50035/users/login
	#
	def post(self):
		if not request.json:
			abort(400) # bad request
		# Parse the json
		parser = reqparse.RequestParser()
		try:
			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request

		# Already logged in
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				# At this point we have sucessfully authenticated.
				session['username'] = request_params['username']
				response = {'status': 'success' }
				responseCode = 201
			except (LDAPException, error_message):
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

class Logout(Resource):
	# GET: Logout: remove session
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar
	#	http://cs3103.cs.unb.ca:50035/users/logout
	def get(self):
		if 'username' in session:
			session.pop('username', None)
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

class Users(Resource):
	# GET: getUsers: retrieves a list of all users
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar
	#	http://cs3103.cs.unb.ca:50035/users?username=bob
	def get(self):
		username = request.args.get('username')
		if 'username' in session:
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				cursor = dbConnection.cursor()
				if username is None:
					sql = 'getUsers'
					cursor.callproc(sql) 
					rows = cursor.fetchall() # get all the results
					response = {'users': rows} # turn set into json and return it
				else:
					sql = 'getUserByName'
					cursor.callproc(sql, [username])
					row = cursor.fetchone() # get a single result
					response = {'content': row}
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
				responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

	# POST: SaveUser: adds a user to the DB
	# 
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "bob"}'
	#  	-c cookie-jar http://cs3103.cs.unb.ca:50035/users	
	def post(self):	
		if 'username' in session:
			username = request.json['username']
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'saveUser'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,[username])
				dbConnection.commit()
				response = cursor.fetchall()
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
				responseCode = 200 # successful
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Login, '/users/login')
api.add_resource(Logout, '/users/logout')
api.add_resource(Users, '/users')

#############################################################################
if __name__ == "__main__":
   	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
