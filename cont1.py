from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import re
import base64
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('DATABASE_URL','sqlite:////home/deepika/Desktop/cont1_data.db')
db=SQLAlchemy(app)
class User(db.Model):
    username=db.Column(db.String(1000),primary_key=True)
    password=db.Column(db.String(1000))

def is_sha1(maybe_sha):
	if len(maybe_sha)!=40:
		return False
	try:
		sha_int=int(maybe_sha,16)
	except ValueError:
		return False
	return True

@app.route('/api/v1/users',methods=['POST'])
def Adduser():
    data=request.get_json()
    try:
        data['username']
        data['password']
    except:
        return jsonify({'enter' :'properly'}),400
    if len(data['username'])!=0 or  len(data['password'])!=0:
       	user=User.query.filter_by(username=data['username']).first()
       	print("hio",user)
       	if user:
            return jsonify({'msg':'user already exist'}),405
        if  not (is_sha1(data['password'])):
        	return jsonify({'msg':'password not in sha1'}),405
        new_user=User(username=data['username'],password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'msg':'new user created'}),200
    return jsonify({'enter' :'properly'}),400

@app.route('/api/v1/users/<username>',methods=['DELETE'])
def RemoveUser(username=''): 
    if username=='':
        return jsonify({'msg':'the user field is empty'}),200                                                                   
    user=User.query.filter_by(username=username).first()
    if not user:
        return  jsonify({'msg':'user does not  exist'}),405
    db.session.delete(user)
    db.session.commit()    
    return jsonify({'msg':'the user is deleted'}),200

@app.route('/api/v1/users',methods=['GET'])
def ListAllUsers():
    users=User.query.all()
    data=[]
    for user in users:
        data.append(user.username)
    return jsonify(data),200


if __name__=='__main__':
    app.run(host="0.0.0.0",debug=True)
