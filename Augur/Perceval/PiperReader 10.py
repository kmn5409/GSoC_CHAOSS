import json
import pandas as pd
#import mysql.connector
from sqlalchemy import create_engine
import sqlalchemy as s
from augur import logger
import os
import augur
import datetime
from dateutil.parser import parse
from datetime import datetime, timedelta
#Count 2290
#if(line[j:j+11]=="},\"unixfrom\"" or line[j:j+9] == "},\"origin\"" ):
#9359610
#1355 aaa-dev <CAGu-7A8CzjH8ch1YdyrZid=Zq7bsVThyE5_zKGLQ0hjxDSA8ZQ@mail.gmail.com>
#<CAP3y0aZ=3eFxUbatK26H9qHV4xPJE6BdQxa=n2bqYqp45q=63A@mail.gmail.com>
#alto
#<CACeyj_GoMVd28FtDBVf83HoDQR8QaLgscabFHRraKdkTSibrCQ@mail.gmail.com>
#<70006713F8B28D4F88E17B98E1459AB5A3B72866@nkgeml501-mbs.china.huawei.com>
#428 alto-dev
#Need to have pip install sqlalchemy-utils
#PiperRead8 had all comments


class PiperMail:
	def __init__(self, user, password, host, port, dbname, ghtorrent, buildMode="auto"):
		"""
		Connect to the database

		:param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
		"""
		char = "charset=utf8"
		self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}?{}'.format(
		    user, password, host, port, dbname,char
		)
		#print('GHTorrentPlus: Connecting to {}:{}/{}?{} as {}'.format(host, port, dbname, char,user))
		self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)
		self.ghtorrent = ghtorrent

		try:
		    	# Table creation
			if (buildMode == 'rebuild') or ((not self.db.dialect.has_table(self.db.connect(), 'issue_response_time')) and buildMode == "auto"):
				logger.info("[GHTorrentPlus] Creating Issue Response Time table...")
				self.build_issue_response_time()
		except Exception as e:
		    logger.error("Could not connect to GHTorrentPlus database. Error: " + str(e))	

	def make(self,link):
		#print(self.db)
		print("Okay")
		print(link)
		upload  = False
		#archives = ["aalldp-dev","alto-dev","advisory-group","archetypes-dev"]
		#archives = ["aalldp-dev","archetypes-dev"]
		archives = ["aalldp-dev","archetypes-dev","alto-dev"]
		'''if("augur/notebooks" in os.getcwd()):
				os.chdir("..")
				print(os.getcwd())
				path = os.getcwd() + "/augur/" + "data/" 
		else:
			path = "data/"	'''
		print("Hey")
		path = "/augur/data/"
		db_name = "mail_lists"
		db_name_csv = os.getcwd() + path + db_name
		columns1 = 'augurmsgID', 'backend_name','project','mailing_list','category',\
		           'message_part','message_parts_tot', 'subject','date',\
				   'message_from','message_id','message_text'
		df5 = pd.DataFrame(columns=columns1)
		df5.to_sql(name=db_name, con=self.db,if_exists='replace',index=False,
				dtype={'augurmsgID': s.types.Integer,
					'backend_name': s.types.VARCHAR(length=300),
					'project': s.types.VARCHAR(length=300),
					'mailing_list': s.types.VARCHAR(length=1000),
					'category': s.types.VARCHAR(length=300),
					'message_part': s.types.Integer,
					'message_parts_tot': s.types.Integer,
					'subject': s.types.VARCHAR(length=400),
					'date': s.types.DateTime(),
					'message_from': s.types.VARCHAR(length=500),
					'message_id': s.types.VARCHAR(length=500),
					'message_text': s.types.VARCHAR(length=12000),
				})
		for i in range(len(archives)):
			place = os.getcwd() + path + 'opendaylight-' + archives[i]
			name = os.getcwd() + path + archives[i]
			f = open(place + '.json','r')
			x = f.read()
			temp = json.dumps(x)
			f.close()
			data,j = self.read_json(x)
			di = json.loads(data)
			df = pd.DataFrame(columns=columns1)
			df["date"] = pd.to_datetime(df["date"])
			df5 = pd.DataFrame(columns=columns1)
			columns2 = "backend_name","mailing_list_url","project"
			if(i==0):
				li = [[di['backend_name'],di['origin'],archives[i]]]
				df_mail_list = pd.DataFrame(li,columns=columns2)
			row = 0
			k = 1
			y = False
			while(j<len(x)):
				df,row = self.add_row_mess(columns1,df,di,row,archives[i])
				df6 = df5.append(df)
				df5 = df6		
				val = False		
				if(row>=( (k*5000))):
					y+=1
					df5.to_sql(name=db_name, con=self.db,if_exists='append',index=False)
					df5.to_csv(db_name_csv + ".csv", mode='a')
					val = True
					y = True
				df = pd.DataFrame(columns=columns1)
				data,r= self.read_json(x[j:])
				j+=r
				if(j==len(x)):
					break
				di = json.loads(data)
			if(val == False):
				df5.to_sql(name=db_name, con=self.db,if_exists='append',index=False)
				df5.to_csv(db_name_csv + ".csv", mode='a')
			if(i!=0):
				df_mail_list = self.add_row_mail_list(columns2,di,df_mail_list,archives[i])
			print("File uploaded ",row)
			upload = True
		print(upload)
		if(upload == True):
			name = os.getcwd() + path + "mailing_list_jobs"
			df_mail_list.to_csv(name + ".csv")
			df_mail_list.to_sql(name='mailing_list_jobs',con=self.db,if_exists='replace',index=False)
		print("Finished")


	def add_row_mess(self,columns1,df,di,row,archives):
		temp = 	di['data']['body']['plain']
		words = ""
		k = 1
		val = False
		prev = 0
		length = len(temp)
		#print(length)
		mess_row_tot = 1
		row_num = 0
		if(length < 100):
			j = length
		else:
			mess_row_tot+= int(length/7000)
			if( (mess_row_tot*7000) > length ):
				mess_row_tot+=1
			for j in range(100,length,7000):
				row_num+=1
				k+=1
				split = di['data']['Date'].split()
				sign = split[5][0]
				if sign == '-':
					sign = -1
				else:
					sign = +1
				hours = int(split[5][1:3]) * sign
				mins = int(split[5][3:6]) * sign
				s = " "
				date = parse(s.join(split[:5]))
				date = date + timedelta(hours = hours)
				date = date + timedelta(minutes = mins)
				li = [[1,di['backend_name'],di['origin'],archives,
				di['category'], row_num, mess_row_tot, di['data']['Subject'],
				date, di['data']['From'],
				di['data']['Message-ID'],
				temp[prev:j] ]]
				df1 = pd.DataFrame(li,columns=columns1)
				df3 = df.append(df1)
				df = df3
				prev = j
				row+=1
		if(j+7000>length):
			k+=1
			row_num+=1
			li = [[1,di['backend_name'],di['origin'],archives,
			di['category'], row_num, mess_row_tot, di['data']['Subject'],
			date, di['data']['From'],
			di['data']['Message-ID'],
			temp[prev:j+7000] ]]
			df1 = pd.DataFrame(li,columns=columns1)
			df3 = df.append(df1)
			df = df3
		return df,row
	
	def add_row_mail_list(self,columns2,di,df_mail_list,archives):
		li = [[di['backend_name'], di['origin'], archives]]
		df = pd.DataFrame(li,columns=columns2)
		df4 = df_mail_list.append(df)
		return df4

	def read_json(self,p):
		k = j = 0
		y=""
		for line in p:
			if(p[j:j+9] == "\"origin\":" or p[j:j+11] == "\"unixfrom\":"):
				k+=1
			y+=line
			j+=1
			if(k==2 and line == "}"):
				break
		return y,j
	