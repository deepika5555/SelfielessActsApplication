from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import re
import base64
import requests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('DATABASE_URL','sqlite:////home/deepika/Desktop/cont2_data.db')
db=SQLAlchemy(app)

class Category(db.Model):
	category_name=db.Column(db.String(1000),primary_key=True)
	no_act=db.Column(db.Integer)

class Acts(db.Model):
    category_name=db.Column(db.String(1000))
    actid=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(1000))
    caption=db.Column(db.String(1000))
    upvote=db.Column(db.Integer)
    imgB64=db.Column(db.String(5000000))
    username=db.Column(db.String(1000))

@app.route('/api/v1/categories',methods=['GET'])
def ListCategory():
    categories=Category.query.all()
    data={}
    for category in categories:
        data[category.category_name]=category.no_act
    return jsonify(data)   

@app.route('/api/v1/categories',methods=['POST'])
def AddCategory():
    data=request.get_json()
    try:
        data[0]
    except:
        return  jsonify({'enter' :'properly'}),400
    if data[0]:
        category=Category.query.filter_by(category_name=data[0]).first()
        if category:
            return jsonify({'msg':'category already exist'}),405
        new_category=Category(category_name=data[0],no_act=0)
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'msg':'category created'}),201
    return  jsonify({'enter' :'properly'}),400

@app.route('/api/v1/categories/<category_name>',methods=['DELETE'])
def DeleteCategory(category_name=''):
    if category_name=='':
        return jsonify({'msg':'the category fieldis empty'}),400
    category=Category.query.filter_by(category_name=category_name).first()
    if not category:
        return  jsonify({'msg':'category does not  exist'}),405
    db.session.delete(category)
    db.session.commit() 
    acts=Acts.query.filter_by(category_name=category_name)
    return jsonify({'msg':'the category is deleted'}),200

@app.route('/api/v1/acts',methods=['POST'])
def UploadAct():
        data=request.get_json()
        try:
            data['username']
            data['timestamp']
            data['categoryName']
            data['actId']
            data['imgB64']
            data['caption']
        except:
            return jsonify({'msg':'the fields are not correct'}),400
        try :
            data['upvote']
            return jsonify({'msg':'upvote not required'}),405
        except Exception:
            pattern=r'^[0-3][0-9]-[0-1][0-9]-[0-9][0-9][0-9][0-9]:[0-5][0-9]-[0-5][0-9]-[0-2][0-9]$'
            if not re.match(pattern,data['timestamp']):
                return jsonify({'msg':'timestamp no match'}),400
            act=Acts.query.filter_by(actid=data['actId']).first()
            if act:
                return jsonify({'msg':'actid already exist'}),405
            
            resp=requests.get('http://127.0.0.1:5000/api/v1/users')
            if resp.status_code!=200:
            	return jsonify({'msg':'user does not  exist'}),405
            users=resp.json()
            if data['username'] not in users:
            	return jsonify({'msg':'user does not  exist'}),405
            print(users)
            category=Category.query.filter_by(category_name=data['categoryName']).first()
            if not category:
                return jsonify({'msg':'category does not exist'}),405
            try:
                base64.b64encode(base64.b64decode(data['imgB64'].encode()))==data['imgB64']
            except Exception:
                return jsonify({'msg':'base64 not done'}),405
                
            new_act=Acts(actid=data['actId'],category_name=data['categoryName'],date=data['timestamp'],caption=data['caption'],username=data['username'],upvote=0,imgB64=data['imgB64'])
            #print(data['imgB64'])
            db.session.add(new_act)
            db.session.commit()
            category=Category.query.filter_by(category_name=data['categoryName']).first()
            category.no_act+=1
            db.session.add(category)
            db.session.commit()
            return jsonify({'msg':'the act is uploaded'}),201

@app.route('/api/v1/categories/<category_name>/acts/size',methods=['GET'])
def ListNoOfActsInCategory(category_name=''):
            if category_name=='':
                return jsonify({'msg':'the field  is empty'}),400
            category=Category.query.filter_by(category_name=category_name).first()
            if not category:
                return jsonify({'msg':'category does not exist'}),405
            output=[]
            output.append(category.no_act)
            return jsonify(output),200


            
            
@app.route('/api/v1/categories/<category_name>/acts',methods=['GET'])
def ListActsForCategory(category_name=''):
            if category_name=='':
                return jsonify({'msg':'the field  is empty'}),400
            try:
                r1=request.args['start']
                r2=request.args['end']
            except Exception:    
                category=Category.query.filter_by(category_name=category_name).first()
                if not category:
                    return jsonify({'msg':'category does not exist'}),405
                acts=Acts.query.filter_by(category_name=category_name)
                no_of_acts=Acts.query.filter_by(category_name=category_name).count()
                if no_of_acts>100:
                    return jsonify({'msg':'too many acts'}),204
                output=[]
                print("hiiiiiiiiiiii")
                for act in acts:
                    d={}
                    d['actId']=act.actid
                    d['upvote']=act.upvote
                    d['timestamp']=act.date
                    d['imgB64']=act.imgB64
                    d['caption']=act.caption
                    d['username']=act.username
                    output.append(d)
                return jsonify(output),200 
            category=Category.query.filter_by(category_name=category_name).first()
            if not category:
                return jsonify({'msg':'category does not exist'}),405
            acts=Acts.query.filter_by(category_name=category_name)
            no_of_acts=Acts.query.filter_by(category_name=category_name).count()
            r1=request.args['start']
            r2=request.args['end']
            if int(r1)>=1 and no_of_acts >= int(r2):
                output=[]
                count=int(r2)-int(r1)+1
                if count<=100:
                    for act in acts:
                        count-=1;
                        d={}
                        d['actId']=act.actid
                        d['upvote']=act.upvote
                        d['timestamp']=act.date
                        d['imgB64']=act.imgB64
                        d['caption']=act.caption
                        d['username']=act.username
                        output.append(d)
                        if count==0:
                            break;
                    
                    return jsonify(output),200 
                else:
                    return  jsonify({'msg':'more number of acts'}),204
            return  jsonify({'msg':'could not verify'}),405  
		#ret+-urn make_response('could not verify',204)
             
@app.route('/api/v1/acts/upvote',methods=['POST'])  
def UpvoteAct():
            data=request.get_json()
            try:
                data[0]
            except:
                return make_response('actid is empty',204)
            act=Acts.query.filter_by(actid=data[0]).first()
            if not act:
                return jsonify({'msg':'actid does not exist'}),405
            act.upvote+=1
            db.session.commit()
            return jsonify({'msg':'upvoted'}),201
    
@app.route('/api/v1/acts/<actid>',methods=['DELETE'])
def DeleteAct(actid=''):
            if actid=='':
                return make_response('actid is empty',204)
            act=Acts.query.filter_by(actid=actid).first()
            if not act:
                return jsonify({'msg':'actid does not exist'}),405                   
            db.session.delete(act)
            db.session.commit()
            category=Category.query.filter_by(category_name=act.category_name).first()
            category.no_act-=1
            db.session.add(category)
            db.session.commit()    
            return jsonify({'msg':'the act is deleted'}),200


if __name__=='__main__':
    app.run(host="0.0.0.0",debug=True,port=5001)
