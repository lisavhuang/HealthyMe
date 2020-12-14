import numpy as np
import pandas as pd
import random 

test_df = pd.DataFrame(columns = ["date_time", "temperature", "humidity","steps"])


start = pd.to_datetime("2020-12-6")
end = pd.to_datetime("2020-12-11")

def random_dates(start,end,n=50):
	start_u = start.value//10**9
	end_u = end.value//10**9
	return pd.to_datetime(np.random.randint(start_u,end_u,n), unit= "s")

def generate_data():
	global start
	global end
	global test_df
	test_df["date_time"] = sorted(random_dates(start,end,50))
	test_df["temperature"] = np.random.randint(low = 60, high = 75, size = 50)
	test_df["humidity"] = np.random.randint(low = 40, high = 50,size = 50)
	steps = []
	for x in range(0,5):
		tmp =np.append([0], sorted(np.random.randint(low=1,high=100, size=9)))
		steps = np.append(steps,tmp)
	print(len(steps))
	test_df["steps"] = steps
	test_df = test_df.to_csv("test_data.csv", index = False)

