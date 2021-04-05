#!/bin/bash
curl -i -H "Content-Type: application/json" -X POST -d '{"username": "<unb_id>", "password": "<unb_password>"}' -c cookie-jar -k https://cs3103.cs.unb.ca:50035/users/login

curl -i -H "Content-Type: application/json" -X POST -d '{"username": "<unb_id>"}' -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users?username=test

curl -i -X POST -H "vidName: bigName" -H  "vidDesc: desc" -F "videoFile=@<full_path_to_file>" -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users/1/videos

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users/1/videos/1

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users/1/videos

curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users/1/videos/1

curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k https://cs3103.cs.unb.ca:50035/users/logout

