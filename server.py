
from flask import Flask
from flask import request, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
import os.path

app = Flask(__name__)

dataframe = pd.DataFrame(columns = ["date","time","steps", "temperature", ])
temp_humidity_df = pd.DataFrame(columns = ["time","temperature", "humidity"])
def get_time():
	now=datetime.now()
	return now.strftime("%Y/%m/%d %H:%M")

def load():
	file_exists = os.path.isfile("temp_humidity.csv")
	if file_exists:
		temp_humidty_df = temp_humidity_df.append(pd.read_csv("temp_humidity.csv"), ignore_index = True)

load()
app = Flask(__name__)
@app.route("/table")
def update_visuals():
	global temp_humidity_df
	return temp_humidity_df.to_html()


@app.route("/")
def update():
	global temp_humidity_df
	data= dict()
	data["temperature"] = request.args.get("temp")
	data["humidity"] = request.args.get("hum")
	data["time"] = get_time()
	temp_humidity_df = temp_humidity_df.append(data,ignore_index = True)
	print(request.args.get("temp"))
	temp_humidity_df.to_csv("temp_humidity.csv",index = False)	
	return temp_humidity_df.to_html()

'''
@app.route("/", methods = ["GET"])
def visuals():
	global temp_humidity_df
	return temp_humidity_df.to_html()
'''

@app.route("/table")
def test():
	global dataframe
	print(request.args.get("var"))
	return "hi"
