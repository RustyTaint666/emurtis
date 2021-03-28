#!/usr/bin/env python3
import sys
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import reqparse, Resource, Api
from flask_session import Session
from pathlib import Path
import pymysql.cursors
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import settings # Our server and db settings, stored in settings.py
import ssl #include ssl libraries
from werkzeug.exceptions import BadRequest, NotFound # BadRequest exception for exception handling

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
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "me", "password": "pass"}' -c cookie-jar http://cs3103.cs.unb.ca:50035/users/login
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
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://cs3103.cs.unb.ca:50035/users?username=test
	@app.route('/users')
	def get():
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
			except BadRequest as e:
				abort(400)
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
			except BadRequest as e:
				abort(400)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
				responseCode = 201 # successful
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

class Videos(Resource):
	# POST: SaveVideo: Saves a given video to the media path and the path to the DB
	# 
	# Example curl command for users:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "bob"}' -c cookie-jar http://cs3103.cs.unb.ca:50035/users	
	@app.route('/users/<int:userId>/videos', methods=['POST'])
	def postVideo(userId):	
		if 'username' in session:
			username = request.json['username']
			try:
				#make the path first
				uploadVid = request.files['file']
				savePath = "/videos"
				Path(savePath).mkdir(parents=True, exist_ok=True)
				if (uploadVid.filename != ''):
					uploadVid.save(uploadVid.filename)
				
				#this places the video in the designated path
				save(savePath)

				#getting json stuff
				videoName = request.json['videoName']
				videoDesc = request.json['videoDesc']

				#after path has been made (and video placed in it)
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'saveVideo'
				cursor = dbConnection.cursor()
				cursor.callproc(sql,[userId, videoName, savePath, videoDesc]) #need userId, videoName, videoPath, videoDescription
				dbConnection.commit()
				response = cursor.fetchall()
			except BadRequest as e:
				abort(400)
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

	# GET: getVideo: retrieves a single video
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://cs3103.cs.unb.ca:50035/users/<uid>/videos/<vid>
	@app.route('/users/<int:userId>/videos/<int:videoId>')
	def getVideo(userId, videoId):
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
				sql = 'getVideo'
				cursor.callproc(sql, [videoId])
				row = cursor.fetchone() # get a single result
				if row:
					response = {'video': row}
				else:
					raise NotFound()
			except BadRequest as e:
				abort(400)
			except NotFound as e:
				abort(404)
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

	
	# GET: getVideosByUserId: retrieves a list of all videos from one particular user
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://cs3103.cs.unb.ca:50035/users/{userId}/videos
	@app.route('/users/<int:userId>/videos')
	def getVideosByUserId(userId):
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
				sql = 'getVideosByUserId'
				cursor.callproc(sql, [userId]) 
				rows = cursor.fetchall() # get all the results
				if rows:
					response = {'videos': rows} # turn set into json and return it
				else:
					raise NotFound()
			except BadRequest as e:
				abort(400)
			except NotFound as e:
				abort(404)
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
	
	# DELETE: deleteVideo: delete a single video
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar http://cs3103.cs.unb.ca:50035/users/<uid>/videos/<vid>
	@app.route('/users/<int:userId>/videos/<int:videoId>', methods=["DELETE"])
	def deleteVideo(userId, videoId):
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
				sql = 'deleteVideo'
				cursor.callproc(sql, [videoId])
				dbConnection.commit()
				if cursor.rowcount > 0:
					responseCode = 204
					response = {'status': 'success'} # turn set into json and return it
				else:
					raise NotFound()
			except BadRequest as e:
				abort(400)
			except NotFound as e:
				abort(404)
			except:
				abort(500) # Nondescript server error
			finally:
				cursor.close()
				dbConnection.close()
				responseCode = 204
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
	context = ('cert.pem', 'key.pem') # Identify the certificates you've generated.
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
