import random
import pandas as pd
import numpy as np
def random_dates(start,end,n=40):
	start_u = start.value//10**9
	end_u = end.value//10**9
	return pd.to_datetime(np.random.randint(start_u, end_u,n), unit = 's')

def random_add():
	start = pd.to_datetime("2020-12-01")
	end = pd.to_datetime("2020-12-05")
	df = pd.DataFrame(columns = ["date_time","temperature","humidity","steps"])
	df["date_time"] = random_dates(start,end)
	df["temperature"] = np.random.randint(50,70,40)	
	df["humidity"] = np.random.randint(30,50,40)
	df["steps"] = np.random.randint(200,3000,40)
	df.to_csv("test.csv",index = False)
def test_start_end_runs():
	start = pd.to_datetime("2020-12-01")
	end = pd.to_datetime("2020-12-05")
	df = pd.DataFrame(columns = ["date_time","temperature","humidity","steps"])
	df["date_time"] = sorted(random_dates(start,end))
	df["temperature"] = np.random.randint(50,70,40)	
	df["humidity"] = np.random.randint(30,50,40)
	steps_array = []
	for x in range(5):
		tmp = np.append([0],sorted(np.random.randint(1,500,7)))
		steps_array = np.append(steps_array,tmp)
	print(steps_array)
	print(len(steps_array))
	df["steps"] = steps_array
	df.to_csv("test.csv",index = False)
test_start_end_runs()
