
from flask import Flask, Markup, render_template
from flask import request, jsonify,redirect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import datetime 
import os.path
import math
import spotify
app = Flask(__name__)
raw_data_df = pd.DataFrame(columns = ["date_time","temperature", "humidity","steps"])
set_date = datetime.date.today()

def get_time():
	#returns in pandas datetime format
	now=datetime.datetime.now()
	return pd.to_datetime(now.strftime("%m/%d/%Y %H:%M"))

def load():
	global raw_data_df
	file_exists = os.path.isfile("raw_data.csv")
	if file_exists:
		raw_data_df = raw_data_df.append(pd.read_csv("raw_data.csv"), ignore_index = True)
	else:
		raw_data_df.to_csv("raw_data.csv",index = False)
def get_week_range(today):
	idx= (today.weekday()+1)%7 #sets sunday as 0
	sun = today - datetime.timedelta(idx)
	sat = today +datetime.timedelta(6-idx)
	return [sun,sat]
def group_runs():
	#gets total steps and time for each run
	raw_data_df = raw_data_df.append(pd.read_csv("test.csv"),ignore_index = True)
	zeros = raw_data_df[raw_data_df["steps"]==0].tolist()
	print(zeros)

	
load()
@app.route("/for-you",methods = ["GET","POST"])
def index():
    	return redirect(spotify.index())
@app.route("/callback")
def callback():
	bpm = "150"
	auth_token = request.args["code"]
	auth_header=spotify.callback(auth_token)
	playlist_data = spotify.get_bpm_playlists(bpm,auth_header)
	results = playlist_data["playlists"]["items"]
	return render_template("playlists.html", bpm=bpm, results = results)
@app.route("/update_data", methods = ["GET"])
def update_data():
	global raw_data_df
	if request.method == "GET":
		data = dict()
		data["temperature"] = request.args.get("temp")
		data["humidity"]=request.args.get("hum")
		data["steps"] = request.args.get("steps")
		now = datetime.datetime.now()
		data["date_time"] = now
		print(data)
		raw_data_df = raw_data_df.append(data,ignore_index = True)
		print(raw_data_df)
		raw_data_df.to_csv("raw_data.csv",index = False,mode = "a", header = False)
	return "received"
	 

@app.route("/home", methods = ["GET", "POST"])
def home():
	#displays current week
	global set_date
	test_df = pd.DataFrame(columns = ["date_time", "temperature", "humidity","steps"])
	test_df = test_df.append(pd.read_csv("test.csv"),ignore_index = False)
	test_df["date_time"] = pd.to_datetime(test_df["date_time"])
	test_df = test_df.sort_values (by = ["date_time"])
	test_df = test_df.set_index("date_time")
	now = datetime.datetime.now()
	today = datetime.date.today()
	str_today = today.strftime("%A, %d %B, %Y") 	 
	if request.method == "POST":
		if  "prev" in request.form:
			set_date = set_date - datetime.timedelta(7)
		elif "next" in request.form:
			set_date = set_date + datetime.timedelta(7)
	sun,sat = get_week_range(set_date)
	filtered_df = test_df.loc[sun:sat]
	table =Markup(filtered_df.to_html())
	str_sun = sun.strftime("%m/%d/%Y")
	str_sat = sat.strftime("%m/%d/%Y")
	title = "Steps per day"
	steps_df = filtered_df["steps"]
	idx = pd.date_range(sun,sat)
	idx = [x.strftime("%A") for x in idx]
	tmp_df = steps_df.reindex(idx,fill_value=0)
	steps_df= steps_df.reset_index()
	steps_df["date_time"] = steps_df["date_time"].apply(lambda x:x.strftime("%A"))
	steps_df = steps_df.set_index("date_time")
	agg_df = pd.concat([steps_df,tmp_df],sort=False)
	agg_df= agg_df.groupby("date_time")["steps"].agg("sum")
	agg_df = agg_df.reindex(tmp_df.index)
	x_data = Markup(tmp_df.index.tolist())
	x_labels = "Steps"
	y_data = agg_df.tolist()
	total_distance = 2.2 * filtered_df["steps"].sum()*0.000189394
	print(total_distance)
	str_total_distance = "{:.2f}".format(total_distance)
	return render_template("home.html",today = str_today, sun = str_sun, sat = str_sat,title = title,x_data =x_data,x_labels = x_labels, y_data = y_data,total_distance = str_total_distance)

@app.route("/test", methods = ["GET","POST"])
def test():
	test_df = pd.DataFrame(columns = ["date_time", "temperature", "humidity","steps"])
	test_df = test_df.append(pd.read_csv("test_data.csv"),ignore_index = True)
	test_df["date_time"] = pd.to_datetime(test_df["date_time"])
	years = test_df["date_time"].dt.year.unique()
	months = {"January":1, "February":2, "March":3, "April":4, "May":5,"June": 6, "July":7,"August":8, "September":9,"October":10,"November":11,"December":12} 
	test_df = test_df.sort_values (by = ["date_time"])
	table = Markup(test_df.to_html())
	now = datetime.now()
	today = now.strftime("%d %B, %Y")
	weeks = range(1,5)
	if request.method == "POST":
		year = request.form.get("years",None)
		month = request.form.get("month",None)
		week = request.form.get("weeks",None)
		print(year,month,week)	
	return render_template("table.html",today = today, years = years, months = sorted(months.keys()),weeks = weeks,table = table)

if __name__ == "__main__":
	app.run(debug= True,host="0.0.0.0",port=5000)
