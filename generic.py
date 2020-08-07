import docker
from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import re
import base64
import requests
import json
import threading
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

class generic_container:
        def __init__(self,min,max,cont_list,health_time,scale_time,port,threshold):
                self.min=min
                self.max=max
                self.cont_list=cont_list
                self.health_time=health_time
                self.scale_time=scale_time
                self.port=port
                self.count=0
                self.threshold=threshold

        def f(self,f_stop):
                for container in self.cont_list:
                        port=container[2]
                        resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/_health')
                        print("containers %s"%self.cont_list)
                        if resp.status_code==500: 
                                container[0].stop()
                                cont=self.create_container(container[2])  #send the port number
                                container[0]=cont[0]
                                print("Health Check",self.cont_list)
                if not f_stop.is_set():
                        threading.Timer(10,self.f,[f_stop]).start()

        def two_minutes_timer(self,two_stop):
                no_cont=int(self.count/self.threshold) + self.min
                self.count=0
                length=len(self.cont_list)
                if no_cont==length:
                        print("equal") 
                elif no_cont<length:
                        n=length-no_cont
                        index=length-1
                        i=0
                        while n!=0:
                                self.cont_list[index-i][0].stop()
                                self.port-=1
                                self.cont_list.pop(index-i)
                                i+=1
                                n-=1
                else:
                        n=no_cont-length
                        if length>=self.max:
                                return
                        while n!=0:
                                cont=self.create_container(self.port)
                                self.port+=1
                                self.cont_list.append(cont)
                                n-=1            
                if not two_stop.is_set():
                        threading.Timer(self.scale_time,self.two_minutes_timer,[two_stop]).start()
                
                
        def create_container(self,port):
                client=docker.from_env()
                container=client.containers.run('acts',ports={'80/tcp':port},volumes={'/home/ubuntu/docker':{'bind':'/common','mode':'rw'}},detach=True)
                cont=[container,0,port]
                return cont
        def load_balancer(self):
                n=0
                for cont in self.cont_list:
                        n+=1
                        if cont[1]==0:
                                cont[1]=1
                                container=list(cont)
                                return self.cont_list[n-1][2]
                        if n==len(self.cont_list):
                                self.cont_list=[[x[0],0,x[2]] for x in self.cont_list]
                                self.cont_list[0][1]=1
                                return self.cont_list[0][2]


'''
client=docker.from_env()
for container in client.containers.list():
      image=str(container.image)
      cont=[]
      if image[9:13]=="acts":   
                cont_list.append([container,0,8000])
'''
@app.route('/',methods=['POST'])
def some():
        return jsonify({'msg':'on /'}),200
@app.route('/',methods=['GET'])
def some1():
        return jsonify({'msg':'on /'}),200

@app.route('/api/v1/categories',methods=['GET'])
def ListCategory():
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)

        GC.count+=1
        resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/categories')
        if resp.status_code==500:
                return jsonify({'msg':'container crashed'}),500
        if resp.status_code==200:
                return jsonify(resp.json()),200
          
@app.route('/api/v1/categories',methods=['POST'])
def AddCategory():
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        data1=request.get_json()                   
        resp=requests.post('http://127.0.0.1:'+str(port)+'/api/v1/categories',data=json.dumps(data1))
        return jsonify(resp.json()),resp.status_code
    
@app.route('/api/v1/categories/<category_name>',methods=['DELETE'])
def DeleteCategory(category_name=''):
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        resp=requests.delete('http://127.0.0.1:'+str(port)+'/api/v1/categories/'+category_name)
        return jsonify(resp.json()),resp.status_code
        
@app.route('/api/v1/acts',methods=['POST'])
def UploadAct():
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        data1=request.get_json()
        resp=requests.post('http://127.0.0.1:'+str(port)+'/api/v1/acts',data=json.dumps(data1))
        return jsonify(resp.json()),resp.status_code      
     
@app.route('/api/v1/categories/<category_name>/acts/size',methods=['GET'])
def ListNoOfActsInCategory(category_name=''):
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/categories/'+category_name+'/acts/size')
        return jsonify(resp.json()),resp.status_code 
        
        
@app.route('/api/v1/categories/<category_name>/acts',methods=['GET'])
def ListActsForCategory(category_name=''):
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        try:
                r1=request.args['start']
                r2=request.args['end']
        except Exception: 
                resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/categories/'+category_name+'/acts')
                return jsonify(resp.json()),resp.status_code
        resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/categories/'+category_name+'/acts',params={'start':r1,'end':r2})
        return jsonify(resp.json()),resp.status_code

@app.route('/api/v1/acts/upvote',methods=['POST'])  
def UpvoteAct():
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        data1=request.get_json()
        resp=requests.post('http://127.0.0.1:'+str(port)+'/api/v1/acts/upvote',data=json.dumps(data1))        
        return jsonify(resp.json()),resp.status_code
        
@app.route('/api/v1/acts/<actid>',methods=['DELETE'])
def DeleteAct(actid=''):
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        resp=requests.delete('http://127.0.0.1:'+str(port)+'/api/v1/acts/'+actid)
        return jsonify(resp.json()),resp.status_code
        
@app.route('/api/v1/acts/count',methods=['GET'])
def Total_no_of_acts():
        global timer_var
        if not timer_var:
                timer_var=1
                two_stop=threading.Event()
                GC.two_minutes_timer(two_stop)
        port=GC.load_balancer()
        print(port)
        GC.count+=1
        resp=requests.get('http://127.0.0.1:'+str(port)+'/api/v1/acts/count')
        return jsonify(resp.json()),resp.status_code 
        

        
                        

if __name__=='__main__':
    timer_var=0
    GC=generic_container(1,10,[],10,10,8000,2)

    f_stop=threading.Event()
    GC.f(f_stop)

    cont1=GC.create_container(GC.port)
    GC.cont_list.append(cont1)
    print(GC.cont_list)
    GC.port+=1
    app.run(host="0.0.0.0",debug=True,use_reloader=False,port=80)

    

    
                
