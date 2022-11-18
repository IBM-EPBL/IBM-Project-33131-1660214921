import re
import numpy as np
import os
from flask import Flask, app,request,render_template, flash, request,redirect,url_for
from tensorflow import keras
from keras import models
from keras.models import load_model
from keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from keras.applications.inception_v3 import preprocess_input
import requests
from cloudant.client import  Cloudant

client=Cloudant.iam('6ff3e404-5b20-4069-b75f-b9b4e167e039-bluemix','Sll7e4MtPW8teDCTDgoS5hCzr5nRB4zWQw-lkQJvRYIN',connect=True)
my_database=client.create_database('my_database')

model1=load_model(r'D:\Web-codeRed\level.h5')
model2=load_model(r'D:\Web-codeRed\body.h5')

app=Flask(__name__)
#default home page or route 
"""@app.route('/')
def index():
    return render_template('index.html')"""

@app.route('/index.html/<user>')
def home(user):
    return render_template('index.html',name=user)

@app.route('/register/<user>')
def register(user):
    return render_template('signup.html',name=user)

@app.route('/aftregister',methods=['GET','POST'])
def aftregister():
    if request.method == 'POST':#
        x = [x for x in request.form.values()]
        print(x)
        data = {
            '_id': x[1],
            'name': x[0],
            'psw': x[2]
        }
        print(data)
        query = {'_id': {'Seq': data['_id']}}
        docs = my_database.get_query_result(query)
        print(docs)
        print(len(docs.all()))
        if (len(docs.all()) == 0):
            url = my_database.create_document(data)
            return render_template('signup.html', pred="Register, please login using your details")
        else:
            return render_template('signup.html', pred="You are already a member, please login using your details")

@app.route('/login/<user>')
def login(user):
    return render_template('login.html',name=user)

@app.route('/aftlog', methods=['GET','POST'])
def aftlog():
        if request.method == 'POST':

            user = request.form['_id']
            passw = request.form['psw']
            print(user, passw)

            query = {'_id': {'$eq': user}}
            docs = my_database.get_query_result(query)
            print(docs)
            print(len(docs.all()))
            if (len(docs.all()) == 0):
                return render_template('login.html', pred="The username is not found.")
            else:
                if ((user == docs[0][0]['_id'] and passw == docs[0][0]['psw'])):
                    return render_template('prediction.html')
                else:
                    return render_template('login.html',pred="user name and password incorrect")

@app.route('/logout/<user>')
def logout(user):
    return render_template('logout.html',name=user)


@app.route('/prediction/<user>')
def prediction(user):
    return render_template('prediction.html',name=user)

@app.route('/result',methods=["GET", "POST"])
def result():
    if request.method=="POST":
       f=request.files['image']
       basepath=os.path.dirname(__file__) 
       filepath=os.path.join(basepath, 'uploads', f.filename) 
       f.save(filepath)
       img=image.load_img(filepath, target_size=(256,256))
       x=image.img_to_array(img)
       x=np.expand_dims (x, axis=0) 
       img_data=preprocess_input(x)
       prediction1=np.argmax(model1.predict(img_data)) 
       prediction2=np.argmax(model2.predict(img_data))
       index1=['front', 'rear', 'side'] 
       index2=['minor', 'moderate', 'severe']
       result1 = index1[prediction1]
       result2 = index2[prediction2]
       if(result1== "front" and result2 == "minor"):
            value="3000 - 5000 INR"
       elif (result1 == "front" and result2 == "moderate"):
            value="6000 - 8000 INR"
       elif(result1== "front" and result2 == "severe"):
            value = "9000 - 11000 INR"
       elif (result1 == "rear" and result2== "minor"):
            value="4000 - 6000 INR"
       elif(result1 == "rear" and result2 == "moderate"):
            value="7000 - 9000 INR"
       elif(result1== "rear" and result2 == "severe"):
            value="11000-13000 INR"
       elif (result1== "side" and result2 == "minor"):
            value="6000 - 8000 INR"
       elif (result1== "side" and result2 == "moderate"):
            value="9000 11000 INR"
       elif(result1 == "side" and result2 == "severe"):
            value = "12000 - 15000 INR"
       else:
            value="16000 - 50000 INR"
       return render_template( 'prediction.html',prediction=value)

if(__name__== "__main__"):
    app.run(debug=True)