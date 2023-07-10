from flask import *
from joblib import load
import numpy as np
import json
import sqlite3
from flask_mail import *
from ipl_cloud import *

with open("config.json",'r') as f:
   par = json.load(f)['params']
with open("config.json",'r') as f:
   model_names=json.load(f)['models']
app = Flask(__name__,template_folder='template',static_folder='static')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = par['gmail-user']
app.config['MAIL_PASSWORD'] = par['gmail-pass']
app.config['MAIL_ASCII_ATTACHMENTS'] = True
app.config['DEBUG'] = True
mail = Mail(app)

@app.route("/",methods=["GET","POST"])
def home():
   model_db=sqlite3.connect(par['db_uri'])
   model_cur=model_db.cursor()
   slug_name="ipl_fsp"
   model_cur.execute(f"SELECT * FROM ml_models WHERE slug='{slug_name}'")
   mc=model_cur.fetchone()
   m={
      'name':mc[1],
      'slug':mc[2],
      'date':mc[3]
   }
   if(request.method == 'POST'):
      con=sqlite3.connect(par['db_uri'])
      cur=con.cursor()
      username= request.form.get("name")
      email= request.form.get("email")
      about= request.form.get("subject")
      msg= request.form.get("message")
      try:
         cur.execute(f"insert into Contact (name,mail,subject,message) \
                     values ('{username}', '{email}','{about}','{msg}')  " )
         con.commit()
         con.close()
      except Exception as e:
         print(e)
      send_mess = Message("you got a mail from "+ email,
                  sender=email,
                  recipients=[par['gmail-user']],
                  body=msg)
      try:
         mail.send(send_mess)
         return render_template("index.html",params=par,msg_status="message sent",model_n=m,mod=list(model_names.keys()))
      except Exception as e:
         print(e)
         return  render_template("index.html",params=par,msg_status="message not sent",model_n=m,mod=list(model_names.keys()))
   return render_template("index.html",params=par,mod=list(model_names.keys()),model_n=m)



@app.route("/ipl_fsp",methods=["GET","POST"])
def get_ipl_fsp():
   model_db=sqlite3.connect(par['db_uri'])
   model_cur=model_db.cursor()
   slug_name="ipl_fsp"
   model_cur.execute(f"SELECT * FROM ml_models WHERE slug='{slug_name}'")
   mc=model_cur.fetchone()
   model={
      'name':mc[1],
      'slug':mc[2],
      'date':mc[3]
   }
   teams=['Chennai Super Kings','Delhi Capitals','Gujarat Lions','Kings XI Punjab','Kolkata Knight Riders',
                'Mumbai Indians','Pune Warriors','Rajasthan Royals','Royal Challengers Bangalore','Sunrisers Hyderabad']
   toss_teams=['Chennai Super Kings','Delhi Capitals','Gujarat Lions','Kings XI Punjab','Kolkata Knight Riders',
                'Mumbai Indians','Pune Warriors','Rajasthan Royals','Royal Challengers Bangalore','Sunrisers Hyderabad']
   city_names=['Ahmedabad','Bangalore','Chandigarh','Chennai','Delhi','Dharamsala','Hyderabad','Jaipur','Kolkata','Mohali','Mumbai','Pune']
   toss_decisions=['feild','bat']
   if(request.method == 'POST'):
      inning=request.form.get("inning")
      bat=request.form.get('batting_team')
      bowl=request.form.get('bowling_team')
      city_input=request.form.get('city_name')
      toss_winner=request.form['toss_win']
      toss_decision=request.form.get('toss_decisions')
      current_runs=request.form.get("current_runs")
      current_wickets=request.form.get("current_wickets")
      current_ball=request.form.get("current_ball")
      score=ipl_predict(inning,bat,bowl,city_input,toss_winner,toss_decision,current_runs,current_wickets,current_ball)
      return render_template("model.html",params=par,mod=model,score=score,tt=toss_teams,td=toss_decision,c_names=city_names,teams=teams)
   return render_template("model.html",params=par,mod=model,score="calculate",tt=toss_teams,td=toss_decisions,c_names=city_names,teams=teams)
@app.route("/blog-single.html",methods=["GET","POST"])
def bs():
   return render_template("blog-single.html")



if (__name__ == "__main__"):
   app.run(port=3000,host="0.0.0.0")
