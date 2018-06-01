import json
import pandas as pd
from sys import exit
import pprint 
import mysql.connector
from sqlalchemy import create_engine
import sqlalchemy as s
from sqlalchemy_utils import database_exists, create_database
#if(line[j:j+11]=="},\"unixfrom\"" or line[j:j+9] == "},\"origin\"" ):
#9359610
#1355
#Need to have pip install sqlalchemy-utils

def read_json(p):
	k = j = 0
	y=""
	for line in p:
		#print(line,"\n\n")
		if(p[j:j+9] == "\"origin\":" or p[j:j+11] == "\"unixfrom\":"):
			k+=1
			#print(p[temp:j])
		y+=line
		j+=1
		if(k==2 and line == "}"):
			break
	#print(k)
	return y,j

def add_row(columns,df,di):
	temp = 	di['data']['body']['plain']
	words = ""
	for j in range(0,len(temp)):
		words+=temp[j]
		if(temp[j] == "\n" and j+1<len(temp)):
			if(temp[j+1] == ">" or j>10000):
				di['data']['body']['plain'] = words
				break
	li = [[di["backend_name"],di['category'],di['data']['Date'],
		      di['data']['From'],di['data']['Message-ID'],
		      di['data']['body']['plain']]]
	df1 = pd.DataFrame(li,columns=columns)
	df3 = df.append(df1)
	return df3
	
	
archives = ["aalldp-dev","aaa-dev","advisory-group","affinity-dev","alto-dev"]
engine = s.create_engine('mysql+mysqlconnector://root:Password@localhost/Pipermail?charset=utf8')
if not database_exists(engine.url):
    create_database(engine.url)
for i in range(len(archives)):
	f = open('opendaylight-' + archives[i] + '.json','r')
	x = f.read()
	temp = json.dumps(x)
	f.close()
	#print(y)
	data,j = read_json(x)
	#print(data,"\n\n")
	# decoding the JSON to dictionay
	di = json.loads(data)

	#print(di)
	# converting json dataset from dictionary to dataframe
	##print(di["data"]["body"]["plain"])
	#pprint.pprint(di)
	#Tried using Subject but sometimes they have fancy symbols that's
	#hard to upload to the database would have to decode it and upload
	#to the database and then encode it back when requesting from
	#the database
	columns = "backend_name","category","Date","From","Message-ID","Text"
	li = [[di["backend_name"],di['category'],di['data']['Date'],
			      di['data']['From'],di['data']['Message-ID'],
			      di['data']['body']['plain']]]
	df = pd.DataFrame(li,columns=columns)
	print(len(x))
	#print(j)
	while(j<len(x)):
		data,r= read_json(x[j:])
		j+=r
		print(j,"\n\n\n")
		if(j==len(x)):
			break
		di = json.loads(data)
		df = add_row(columns,df,di)

	df = df.reset_index(drop=True)
	df.to_csv(archives[i] + ".csv")
	print(pd.read_csv(archives[i] + ".csv",index_col=0))
	df.to_sql(name=archives[i], con=engine, if_exists = 'replace', index=False,)
