
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
from collections import defaultdict,OrderedDict
app = Flask(__name__)
raw_data_df = pd.DataFrame(columns = ["date_time","temperature", "humidity","steps"])
summary_df = pd.DataFrame()
set_date = datetime.datetime.now().date()
def get_time():
	#returns in pandas datetime format
	now= datetime.datetime.now()
	return pd.to_datetime(now.strftime("%m/%d/%Y %H:%M"))

def load():
	global raw_data_df
	file_exists = os.path.isfile("raw_data.csv")
	if file_exists:
		raw_data_df = raw_data_df.append(pd.read_csv("raw_data.csv"), ignore_index = True)
		raw_data_df["date_time"] = pd.to_datetime(raw_data_df["date_time"])
		raw_data_df = raw_data_df.set_index("date_time")
		raw_data_df = raw_data_df.sort_index()
	else:
		raw_data_df.to_csv("raw_data.csv",index = False)
def load_test():
	global raw_data_df
	raw_data_df = raw_data_df.append(pd.read_csv("test/test_data.csv"),ignore_index=True)
	raw_data_df["date_time"] = pd.to_datetime(raw_data_df["date_time"])
def summarize():
	#for each run find :
	# duration,dew_temp, distance,pacing,bpm
	global summary_df
	global raw_data_df
	#recommended pacing adjustments
	rec_dict = defaultdict(lambda: 1)
	rec_dict[10] = 1.0025
	rec_dict[11] = 1.0075
	rec_dict[12] = 1.015
	rec_dict[13] = 1.025
	rec_dict[14] = 1.0375
	rec_dict[15] = 1.0525
	rec_dict[16] = 1.07
	rec_dict[17] = 1.09
	rec_dict[18] = 0
	runs_df = raw_data_df.copy()
	runs_df = runs_df.reset_index()
	start = runs_df.index[runs_df["steps"]==0].tolist()
	end = [x-1 for x in start[1:]]
	end = np.append(end, [len(runs_df.index)-1])
	start_end_times = sorted(np.append(start,end))
	filtered_df = (runs_df[["date_time","steps"]].iloc[start_end_times].copy())
	filtered_df["duration"] =filtered_df["date_time"]
	filtered_df = filtered_df.diff().iloc[1::2,:]
	filtered_df["bpm"] = filtered_df["steps"]/filtered_df["duration"].dt.total_seconds()*60
	summary_df = pd.concat([filtered_df[["duration","bpm"]],runs_df],axis=1,join_axes = [filtered_df.index])
	summary_df = summary_df.reset_index(drop=True)
	summary_df["dew_temp"] = ((summary_df["temperature"]-32)/1.8) + ((100-summary_df["humidity"])/5.) + summary_df["temperature"]
	summary_df["distance"] = summary_df["steps"] * 2.2 * 0.000189394
	summary_df["pacing"] = summary_df["duration"]/summary_df["distance"]
	mile_time = summary_df[summary_df["dew_temp"]<=100]["pacing"].mean()
	summary_df["rec_pacing"] = summary_df["dew_temp"].apply(lambda x: rec_dict[((int)(x/10))]*mile_time)
	summary_df = summary_df[summary_df.steps !=0]
def get_week_range(today):
	idx= (today.weekday()+1)%7 #sets sunday as 0
	sun = today - datetime.timedelta(idx)
	sat = today +datetime.timedelta(6-idx)
	return [sun,sat]
load()
summarize()
@app.route("/playlists",methods = ["GET","POST"])
def playlists():
    	return redirect(spotify.index())
@app.route("/callback")
def callback():
	global summary_df
	summarize()
	avg_bpm= ((int)(summary_df[summary_df["dew_temp"]<=100]["bpm"].mean()/10))*10
	auth_token = request.args["code"]
	auth_header=spotify.callback(auth_token)
	playlist_data = spotify.get_bpm_playlists(avg_bpm,auth_header)
	results = playlist_data["playlists"]["items"]
	return render_template("playlists.html", bpm=avg_bpm, results = results)
@app.route("/update_data", methods = ["GET"])
def update_data():
	#receives the data sent from the arduino
	global raw_data_df
	if request.method == "GET":
		raw_data_df = raw_data_df.reset_index()
		data = OrderedDict()
		now = datetime.datetime.now()
		data["date_time"] = [now]
		data["temperature"] =[(int)( request.args.get("temp"))]
		data["humidity"]= [(int) (request.args.get("hum"))]
		data["steps"] = [(float)(request.args.get("steps"))]
		tmp_df = pd.DataFrame(data)
		raw_data_df = pd.concat([raw_data_df,tmp_df])
		tmp_df.to_csv("raw_data.csv",index = False,mode = "a", header = False)
		raw_data_df = raw_data_df.set_index("date_time")
	return "received"
@app.route("/runs",methods = ["GET"])
def runs():
	global summary_df
	summarize()
	avg_bpm= ((int)(summary_df[summary_df["dew_temp"]<=100]["bpm"].mean()/10))*10
	mile_time = summary_df[summary_df["dew_temp"]<=100]["pacing"].mean()
	fmile_time = str(datetime.timedelta(seconds=mile_time.seconds))
	formatted_df= pd.DataFrame()
	formatted_df["Date"] = summary_df["date_time"].apply(lambda x:x.strftime("%m/%d/%Y, %H:%M"))
	formatted_df["Temperature"] = summary_df["temperature"].apply(lambda x: "{} F".format(x)) 
	formatted_df["Humidity"] = summary_df["humidity"].apply(lambda x : "{} %".format(x))
	formatted_df["Duration"] = summary_df["duration"].apply(lambda x :str(datetime.timedelta(seconds=x.seconds)))
	formatted_df["Distance (mile)"] = summary_df["distance"].apply(lambda x: "{:.2f}".format(x))
	formatted_df["Pacing (min/mile)"] = summary_df["pacing"].apply(lambda x : str(datetime.timedelta(seconds=x.seconds)))
	formatted_df["Advised Pacing (min/mile)"] = summary_df["rec_pacing"].apply(lambda x: str(datetime.timedelta(seconds=x.seconds)))
	formatted_html = Markup(formatted_df.to_html(classes = "styled-table"))
	return render_template("runs.html", bpm = avg_bpm, mile_time = fmile_time, table = formatted_html)
@app.route("/home", methods = ["GET", "POST"])
def home():
	#displays current week
	global set_date
	global summary_df
	if request.method == "POST":
		if  "prev" in request.form:
			set_date = set_date - datetime.timedelta(7)
		elif "next" in request.form:
			set_date = set_date + datetime.timedelta(7)
	summarize()
	summary_df = summary_df.set_index("date_time")
	today = datetime.datetime.now()
	str_today = today.strftime("%A, %d %B, %Y") 	 
	sun,sat = get_week_range(set_date)
	filtered_df = summary_df.loc[sun:sat]
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
	total_distance =  filtered_df["distance"].sum()
	str_total_distance = "{:.2f}".format(total_distance)
	return render_template("home.html",today = str_today, sun = str_sun, sat = str_sat,title = title,x_data =x_data,x_labels = x_labels, y_data = y_data,total_distance = str_total_distance)

@app.route("/test", methods = ["GET","POST"])
def test():
	test_df = pd.DataFrame(columns = ["date_time", "temperature", "humidity","steps"])
	test_df = test_df.append("test/test_data.csv",inex = False,ignore_index = True)
	test_df.to_csv()
	return render_template("table.html",today = today, years = years, months = sorted(months.keys()),weeks = weeks,table = table)

if __name__ == "__main__":
	app.run(debug= True,host="0.0.0.0",port=5000)
