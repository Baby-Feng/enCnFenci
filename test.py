import sys
import re
import json
import ast
import pymysql
from time import *
from scipy.stats import kstest#检验正态分布
import matplotlib.pyplot as plt
import numpy as np

def storeDataListToMySql(dataSet,tableName):
	db = pymysql.Connect(host='localhost',user='root',passwd='958952',db='test',port=3306,charset = 'utf8')
	cursor = db.cursor()
	dataSetSize = len(dataSet)
	now = 1
	for data in dataSet:
		print("共 ",dataSetSize," 条记录 , ","正在插入第 ",now," 记录:",data)
		#sql = "INSERT INTO "+tableName+" (tid,title,author,platform,url,label,type) VALUES ('"+data["tid"]+"','"+data["title"]+"','"+data["author"]+"','"+data["platform"]+"','"+data["url"]"','"+data["label"]+"','video')"
		sql = "INSERT INTO "+tableName+" (keyword,sum) VALUES ('"+data["keyword"]+"',"+str(data["sum"])+")"
		cursor.execute(sql)
		db.commit()
		now += 1

def updateDataToMySql(sql):
	db = pymysql.Connect(host='localhost',user='root',passwd='958952',db='test',port=3306,charset = 'utf8')
	cursor = db.cursor()
	cursor.execute(sql)
	db.commit()

def getDataListFromMySql():
	dataList = []
	db = pymysql.Connect(host='localhost',user='root',passwd='958952',db='test',port=3306,charset = 'utf8')
	cursor = db.cursor()
	results = []
	sql = "SELECT tid,title from resource" 
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		db.close()
	for row in results:
		dataList.append({"tid":row[0],"title":row[1]})
	return dataList

def storeDataListToJson(dataList,filename):
	with open(filename,'a',encoding='utf-8') as fp:
		for i in dataList:
			fp.write(json.dumps(i,ensure_ascii=False)+"\n")

def format_str(content):
	content = str(content)
	content_str = ''
	for i in content:
		if is_chinese(i):
			content_str = content_str+i
	return content_str

def is_chinese(uchar):
	"""判断一个unicode是否是汉字"""
	if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
		return True
	else:
		return False

def is_number(uchar):
	"""判断一个unicode是否是数字"""
	if uchar >= u'\u0030' and uchar <= u'\u0039':
		return True
	else:
		return False

def is_alphabet(uchar):
	"""判断一个unicode是否是英文字母"""
	if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
		return True
	else:
		return False

def is_SpecialChar(uchar):
	"""判断一个字符是否是合法字符"""
	specialChar = "@#$%&*_+="
	if specialChar.find(uchar) != -1:
		return True
	else:
		return False

def getDataListFromJson(filename):
	f = open(filename, mode="r", encoding="utf-8")
	s = 0
	adjacency = []
	for info in f:
		a = ast.literal_eval(info)
		s+=1
		adjacency.append(a)
	return adjacency

def getTitleListFromMysql():
	titleList = []
	db = pymysql.Connect(host='localhost',user='root',passwd='958952',db='test',port=3306,charset = 'utf8')
	cursor = db.cursor()
	results = []
	sql = "SELECT title FROM resource"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		db.close()
	for row in results:
		titleList.append(row[0])
	return titleList

def quickSortByProb(data,left,right):
	if (right-left) == 1:
		#待排序集合中只有两个元素,直接比较大小
		if data[left]["prob"] < data[right]["prob"]:
			#左小于右则互换位置,也即大的换到左边
			data[left],data[right] = data[right],data[left]
	elif left<right:
		#待排序集合中元素多余两个
		i=left
		j=right
		#i,j分别是左右指针
		temp = data[left]
		#以左边第一个为比较基准
		while i<j:
			while i<j and data[j]["prob"]<temp["prob"]:
				j -= 1
			#交换位置
			if i<j:
				data[i] = data[j]
				i +=1#左指针右移
			while i<j and data[i]["prob"]>temp["prob"]:
				i += 1
			if i<j:
				data[j] = data[i]
				j -= 1#右指针左移
		data[i] = temp#此时i=j
		quickSortByProb(data,left,i-1)
		quickSortByProb(data,i+1,right)

def quickSortBySequency(data,left,right):
	if (right-left) == 1:
		#待排序集合中只有两个元素,直接比较大小
		if data[left]["sequency"] < data[right]["sequency"]:
			#左小于右则互换位置,也即大的换到左边
			data[left],data[right] = data[right],data[left]
	elif left<right:
		#待排序集合中元素多余两个
		i=left
		j=right
		#i,j分别是左右指针
		temp = data[left]
		#以左边第一个为比较基准
		while i<j:
			while i<j and data[j]["sequency"]<temp["sequency"]:
				j -= 1
			#交换位置
			if i<j:
				data[i] = data[j]
				i +=1#左指针右移
			while i<j and data[i]["sequency"]>temp["sequency"]:
				i += 1
			if i<j:
				data[j] = data[i]
				j -= 1#右指针左移
		data[i] = temp#此时i=j
		quickSortBySequency(data,left,i-1)
		quickSortBySequency(data,i+1,right)

def quickSortBySum(data,left,right):
	if (right-left) == 1:
		#待排序集合中只有两个元素,直接比较大小
		if data[left]["sum"] < data[right]["sum"]:
			#左小于右则互换位置,也即大的换到左边
			data[left],data[right] = data[right],data[left]
	elif left<right:
		#待排序集合中元素多余两个
		i=left
		j=right
		#i,j分别是左右指针
		temp = data[left]
		#以左边第一个为比较基准
		while i<j:
			while i<j and data[j]["sum"]<temp["sum"]:
				j -= 1
			#交换位置
			if i<j:
				data[i] = data[j]
				i +=1#左指针右移
			while i<j and data[i]["sum"]>temp["sum"]:
				i += 1
			if i<j:
				data[j] = data[i]
				j -= 1#右指针左移
		data[i] = temp#此时i=j
		quickSortBySum(data,left,i-1)
		quickSortBySum(data,i+1,right)

def getCatalogIndex(dictionary,firstWord):
	#从词目录获取索引
	dictionarySize = len(dictionary)
	for i in range(dictionarySize):
		if dictionary[i]["firstWord"] == firstWord:
			return i
	return -1

def getPreDivisionDataList(data):
	#预分割函数,只保留中文和英文信息
	preDivisionDataList = []
	preTemp = 0
	dataSize = len(data)
	status = 0
	for i in range(dataSize):
		now = data[i]
		if is_chinese(now):
			if status != 1 and preTemp < i:
				preDivisionDataList.append(data[preTemp:i])
				preTemp = i
			status = 1
		elif is_alphabet(now):
			if status !=2 and preTemp < i:
				preDivisionDataList.append(data[preTemp:i])
				preTemp = i
			status = 2
		else:
			if preTemp < i:
				preDivisionDataList.append(data[preTemp:i])
			status = 0
			preTemp = i+1
	if preTemp < dataSize:
		preDivisionDataList.append(data[preTemp:dataSize])
	return preDivisionDataList


def getInitialDictionary(dataSet,chWindowSize):
	#参数说明：chWindowSize为中文关键词窗口大小，enWindowSize为英文关键词窗口大小
	dictionary = []
	updateDataSetToDictionary(dictionary,dataSet,chWindowSize)
	return dictionary

def updateDataSetToDictionary(dictionary,dataSet,chWindowSize):
	for origin in dataSet:
		preDivisionDataList = getPreDivisionDataList(origin)
		#预分割
		for data in preDivisionDataList:
			#判断类型
			if is_chinese(data[0]):
				#是中文
				#更新中文,窗口设定为中文窗口
				updateDataToDictionary(dictionary,data,chWindowSize)
			elif is_alphabet(data[0]) and len(data) > 1:
				#是英文,且长度大于1个,一律将大写英文字符替换为小写字符
				#直接保存英文单词
				enStr = data.lower()
				print("英文 : %s"%enStr)
				firstWord = enStr[0]
				index = getCatalogIndex(dictionary,firstWord)
				if index == -1:
					#首字母没找到
					dictionary.append({"firstWord":firstWord,"sum":1,"children":[{"word":enStr,"sum":1}]})
				else:
					#找到
					status = False
					for child in dictionary[index]["children"]:
						if strCompare(child["word"],enStr):
							#找到
							child["sum"] += 1
							status = True
							break
					if not status:
						#没找到，则添加记录
						dictionary[index]["children"].append({"word":enStr,"sum":1})
					dictionary[index]["sum"] += 1
			else:
				#数字、特殊字符不考虑
				pass

def updateDataToDictionary(dictionary,data,windowSize):
	dataSize = len(data)
	for i in range(dataSize-1):
		#最后一个字符不纳入词典
		maxTemp = 0
		#最长关键词下标
		if (i+windowSize) <= dataSize:
			maxTemp = i+windowSize
		else:
			maxTemp = dataSize
		chStr = data[i:maxTemp]
		print("中文 : %s"%chStr)
		firstWord = data[i]
		nowWordIndex = getCatalogIndex(dictionary,firstWord)
		if nowWordIndex == -1:
			#没找到
			nowWordIndex = len(dictionary)
			dictionary.append({"firstWord":firstWord,"sum":0,"children":[]})
		dictionary[nowWordIndex]["sum"] += 1
		updateChildren(dictionary[nowWordIndex]["children"],chStr[1:],0)

def updateChildren(children,chStr,nowTemp):
	if nowTemp >= len(chStr):
		pass
	else:
		nowWord = chStr[nowTemp]
		childrenSize = len(children)
		for i in range(childrenSize):
			if children[i]["word"] == nowWord:
				children[i]["sum"] += 1
				return updateChildren(children[i]["children"],chStr,nowTemp+1)
		#没找到
		children.append({"word":nowWord,"sum":1,"children":[]})
		return updateChildren(children[childrenSize]["children"],chStr,nowTemp+1)

def updateDictionaryToLowDimension(dictionary,deleteStandard):
	temp = 0
	while temp < len(dictionary):
		print("temp = %d"%temp)
		if dictionary[temp]["sum"] < deleteStandard:
			#基数小于标准
			del dictionary[temp]
		else:
			temp += 1

"""
***************************************************************************************************************************************
"""
def getStrListFromSentence(originSentence):
	# chChar = " ，。/；‘【】、·《》？：“”‘’{}|——……￥！~"
	# enChar = "`~!()[]\\;:'"
	# char = chChar + enChar
	phraseList = []
	originSize = len(originSentence)
	index = 0
	origin = originSentence.lower()
	for i in range(originSize):
		if is_chinese(origin[i]) or is_alphabet(origin[i]) or is_number(origin[i]) or is_SpecialChar(origin[i]):
			#说明不是无效字符s
			pass
		else:
			#是无效字符
			if index < i:
				phraseList.append(origin[index:i])
			index = i+1
	if index < originSize:
		phraseList.append(origin[index:originSize])
	strList = []
	for sentence in phraseList: 
		status = 0
		nowStrTemp = 0
		for temp in range(len(sentence)):
			if is_chinese(sentence[temp]):
				#是中文
				if temp == 0:
					status = 1
				if status == 1:
					#之前集合中文字符
					pass
				else:
					#当前是中文字符,且之前集合非中文字符
					strList.append(sentence[nowStrTemp:temp])
					nowStrTemp = temp
					status = 1
					#字符串指针更新，状态更新为正在集合中文字符串
			elif is_alphabet(sentence[temp]):
				if temp == 0:
					status = 2
				if status == 2:
					pass
				else:
					#当前是英文字符，且之前集合非英文字符
					strList.append(sentence[nowStrTemp:temp])
					nowStrTemp = temp
					status = 2
			elif is_number(sentence[temp]):
				if temp == 0:
					status = 3
				if status == 3:
					pass
				else:
					#当前是数字
					strList.append(sentence[nowStrTemp:temp])
					nowStrTemp = temp
					status = 3
			elif is_SpecialChar(sentence[temp]):
				if temp == 0:
					status = 4
				if status == 4:
					pass
				else:
					#当前是英文字符，且之前集合非英文字符
					strList.append(sentence[nowStrTemp:temp])
					nowStrTemp = temp
					status = 4
			else:
				pass
		if nowStrTemp < len(sentence):
			strList.append(sentence[nowStrTemp:len(sentence)])
	print(strList)
	return strList


def judgeStrType(str_a,str_b):
	if is_chinese(str_a[0]) and is_chinese(str_b[0]):
		return True
	elif is_alphabet(str_a[0]) and is_alphabet(str_b[0]):
		return True
	elif is_number(str_a[0]) and is_number(str_b[0]):
		return True
	elif is_SpecialChar(str_a[0]) and is_SpecialChar(str_b[0]):
		return True
	else:
		return False

def strCompare(str_a,str_b):
	len_a = len(str_a)
	len_b = len(str_b)
	if len_a != len_b:
		return False
	else:
		for i in range(len_a):
			if str_a[i] != str_b[i]:
				return False
		return True

def getKeywordIndex(keywordGraph,keyword):
	temp = 1
	keywordGraphSize = len(keywordGraph)
	while temp < keywordGraphSize:
		if strCompare(keywordGraph[temp]["keyword"],keyword):
			return temp
		temp += 1
	return -1

def getStrList(data):
	strList = []
	dataSize = len(data)
	preTemp = 0
	status = 0
	for i in range(dataSize):
		now = data[i]
		if is_chinese(now):
			if status != 1 and preTemp < i:
				strList.append(data[preTemp:i])
				preTemp = i
			status = 1
		elif is_alphabet(now):
			if status !=2 and preTemp < i:
				strList.append(data[preTemp:i])
				preTemp = i
			status = 2
		elif is_number(now):
			if status !=3 and preTemp < i:
				strList.append(data[preTemp:i])
				preTemp = i
			status = 3
		elif is_SpecialChar(now):
			if status != 4 and preTemp < i:
				strList.append(data[preTemp:i])
				preTemp = i
			status = 4
		else:
			if preTemp < i:
				strList.append(data[preTemp:i])
			status = 0
			preTemp = i+1
	if preTemp < dataSize:
		strList.append(data[preTemp:dataSize])
	return strList
	pass

def getKeywordCatalogIndex(catalog,word):
	temp = 0
	catalogSize = len(catalog)
	while temp < catalogSize:
		if catalog[temp]["word"] == word:
			#字符相同,返回当前索引
			return temp
		temp += 1
	return -1

def updateKeywordCatalog(catalog,keyword,keywordIndex):
	for i in keyword:
		#i为每个字符
		catalogIndex =  getKeywordCatalogIndex(catalog,i)
		if catalogIndex != -1:
			#已找到当前字符的索引
			content = catalog[catalogIndex]["indexList"]
			#包含该字符的所有关键词
			status = False
			for indexTemp in content:
				if indexTemp == keywordIndex:
					#说明已经收录该词条
					#更改状态为已查询，退出循环
					status = True
					break
			if status:
				pass
			else:
				#没找到，则添加记录
				catalog[catalogIndex]["indexList"].append(keywordIndex)
		else:
			catalog.append({"word":i,"indexList":[keywordIndex]})

def getKeywordListFromDataSet(dictionary,dataSet,compareStandard):
	keywordList = []
	for data in dataSet:
		keywordListTemp = getKeywordList(dictionary,data,compareStandard)
		keywordList.append(keywordListTemp)
	return keywordList

def getKeywordList(dictionary,data,compareStandard):
#获取一条记录包含的关键词
	strList = getStrList(data)
	print(strList)
	#得到预处理字串,集合同类字符
	keywordList = []
	for strTemp in strList:
		#每个同类字符集进行关键词获取
		now = strTemp[0]
		print(now)
		print(strTemp,now)
		#首字符
		if is_chinese(now):
			#是中文字符
			keywordList += getChineseKeyword(dictionary,strTemp,compareStandard)
		elif is_alphabet(now):
			#是英文字符,不分割
			keywordList.append(strTemp.lower())
		elif is_number(now):
			#是数字,不处理，直接保存
			keywordList.append(strTemp)
		elif is_SpecialChar(now):
			#是特殊字符，不处理，直接保存
			keywordList.append(strTemp)
	return keywordList


def getChineseKeyword(dictionary,strTemp,compareStandard):
	keywordList = []
	probList = []
	temp = 0
	condProb = 0
	preTemp = 0
	breakStatus = True
	width = 0.1
	#断点
	while temp < len(strTemp):
		nowWord = strTemp[temp]
		if breakStatus:
			#断点
			nowWordIndex = getCatalogIndex(dictionary,nowWord)
			children = dictionary[nowWordIndex]["children"]
			rootSum = dictionary[nowWordIndex]["sum"]
			condProb = 0
			preTemp = temp
			temp += 1
			breakStatus = False
			continue
		#没有断点
		status = False
		#检验数据是否服从正态分布
		dataTemp = []
		for child in children:
			dataTemp.append(child["sum"])
		if len(dataTemp) != 0:
			u = np.mean(dataTemp)#均值
			minValue = min(dataTemp)
		for child in children:
			#利用均值计算断点
			if child["word"] == nowWord:
				#找到,计算条件概率
				status = True
				nowProb = child["sum"]/rootSum
				minTemp = u - ((u - minValue)*width)
				print(nowWord,"均值=",u,"最小值=",minValue,"当前值=",child["sum"],"概率=",nowProb)
				if child["sum"] < minTemp:
					#被认为出现断点
					print("数量不满足")
					if temp - preTemp > 1:
						keywordList.append(strTemp[preTemp:temp])
						condProb = 0
					breakStatus = True
					break
				if condProb == 0 and nowProb < 1/len(children):
					#发生断点
					print("概率减小")
					if temp - preTemp > 1:
						keywordList.append(strTemp[preTemp:temp])
						condProb = 0
					breakStatus = True
					break
				if condProb!=0 and nowProb < condProb:
					#条件概率减小,计算两次条件概率之差,超过标准认为出现断点
					if condProb - nowProb > compareStandard:
						if temp - preTemp > 1:
							keywordList.append(strTemp[preTemp:temp])
							condProb = 0
						breakStatus = True
					else:
						#条件概率变化在可控范围内
						breakStatus = False
						condProb = nowProb
						children = child["children"]
						rootSum = child["sum"]
						temp += 1
				else:
					#找到，且数量在标准之上，没有断点
					breakStatus = False
					temp += 1
					condProb = nowProb
					children = child["children"]
					rootSum = child["sum"]
				#找到孩子
				break
		if status:
			#如果找到
			#条件概率变化在可控范围内，则已经处理完毕
			#若条件概率
			pass
		else:
			#没找到,发生断点
			print("没找到...")
			if temp - preTemp > 1:
				print("还有内容,添加:",strTemp[preTemp:temp])
				keywordList.append(strTemp[preTemp:temp])
				#keywordList.append({"keyword":strTemp[preTemp:temp],"prob":rootSum})
			breakStatus = True
	if len(strTemp) - preTemp > 1 and not breakStatus:
		#还有数据且没发生断点
		keywordList.append(strTemp[preTemp:])
		#keywordList.append({"keyword":strTemp[preTemp:temp],"prob":rootSum})
	print(keywordList)
	return keywordList



def keywordGraphNeighbourListPruning(neighbourList,neighbourSum,pruningStandard):
	temp = 0
	deleteSum = 0
	while temp < len(neighbourList):
		if neighbourList[temp]["sum"] <= pruningStandard:
			#次数不够，删除
			deleteSum += neighbourList[temp]["sum"]
			del neighbourList[temp]
		else:
			temp += 1
	neighbourSum -= deleteSum

def createKeywordDatabaseCatalog(keywordDatabase):
	keywordDatabaseSize = len(keywordDatabase)
	temp = 1
	while temp < keywordDatabaseSize:
		updateKeywordCatalog(keywordDatabase[0]["catalog"],keywordDatabase[temp]["keyword"],temp)
		temp += 1

def getInitialKeywordDatabase(keywordGraph):
	#获得词库
	initialKeywordDatabase = [{"catalog":[]}]
	standard = 2
	temp = 1
	keywordGraphSize = len(keywordGraph)
	while temp < keywordGraphSize:
		keywordSum = keywordGraph[temp]["sum"]
		nowKeyword = keywordGraph[temp]["keyword"]
		if keywordSum > standard:
			updateChAndEnKeywordDatabase(initialKeywordDatabase,keywordGraph,temp,standard)
		else:
			#不是关键词,不处理
			pass
		temp += 1
	createKeywordDatabaseCatalog(initialKeywordDatabase)
	return initialKeywordDatabase

def updateChAndEnKeywordDatabase(keywordDatabase,keywordGraph,rootIndex,standard):
	root = keywordGraph[rootIndex]
	rootKeyword = root["keyword"]
	preList = root["preList"]
	rearList = root["rearList"]
	if (is_chinese(rootKeyword[0]) or is_alphabet(rootKeyword[0])) and len(rootKeyword) > 1:
		#中文、英文且字符个数大于1,可以直接添加
		keywordDatabase.append({"keyword":rootKeyword,"sum":root["sum"]})

def updateKeywordDatabase(keywordDatabase,keywordGraph,rootIndex,standard):
	root = keywordGraph[rootIndex]
	rootKeyword = root["keyword"]
	preList = root["preList"]
	rearList = root["rearList"]
	if (is_chinese(rootKeyword[0]) or is_alphabet(rootKeyword[0])) and len(rootKeyword) > 1:
		#中文、英文且字符个数大于1,可以直接添加
		keywordDatabase.append({"keyword":rootKeyword,"sum":root["sum"]})
	#添加混合关键词
	for rear in rearList:
		rearIndex = rear["index"]
		if rear["sum"] > standard and rearIndex !=0 and not judgeStrType(rootKeyword,keywordGraph[rearIndex]["keyword"]):
			rearKeyword = keywordGraph[rearIndex]["keyword"]
			keywordDatabase.append({"keyword":rootKeyword+rearKeyword,"sum":rear["sum"]})
	for pre in preList:
		#保存英语特殊符号混合关键词
		preIndex = pre["index"]
		if pre["sum"] > standard and preIndex !=0 and not judgeStrType(rootKeyword,keywordGraph[preIndex]["keyword"]):
			#可以认为是关键词,允许添加
			preKeyword = keywordGraph[pre["index"]]["keyword"]
			keywordDatabase.append({"keyword":preKeyword+rootKeyword,"sum":pre["sum"]})
			#考虑前-root-后组成的关键词
			for rear in rearList:
				if rear["sum"] > standard and rear["index"] !=0:
					rearIndex = rear["index"]
					rearKeyword = keywordGraph[rearIndex]["keyword"]
					rear_preList = keywordGraph[rearIndex]["preList"]
					for rear_pre in rear_preList:
						if rear_pre["index"] == pre["index"] and rear_pre["sum"] > standard:
							#可以进行组合
							maxSum = pre["sum"]
							if maxSum > rear["sum"]:
								maxSum = rear["sum"]
								#保存最小值
							keywordDatabase.append({"keyword":preKeyword+rootKeyword+rearKeyword,"sum":maxSum})
		else:
			#不是关键词
			pass




def updateKeywordGraphToLowDimension(keywordGraph):
	#主要功能：提取不同类型的混合关键词
	pruningStandard = 2
	temp = 1
	deleteKeywordStandard = 2
	while temp < len(updateKeywordGraph):
		nowKeywordSum = keywordGraph[temp]["sum"]
		if nowKeywordSum <= deleteKeywordStandard:
			#数量小于标准，认定不是关键词
			keywordGraph[temp]["sum"] == 0
		else:
			#认为是关键词,删除孩子列表
			keywordGraphNeighbourListPruning(keywordGraph[temp]["rearList"],keywordGraph[temp]["rearSum"],pruningStandard)
			keywordGraphNeighbourListPruning(keywordGraph[temp]["preList"],keywordGraph[temp]["preSum"],pruningStandard)
			#减枝操作执行完毕
			keyword = keywordGraph[temp]["keyword"]
			if is_number(keyword[0]) or is_SpecialChar(keyword[0]):
				#考虑进行关键词合并
				preList = keyword

			else:
				#不做处理
				pass



def getInitialKeywordGraph(keywordList):
	keywordGraph = [{"sum":0,"catalog":[]}]
	for keyword in keywordList:
		#keyword为每一句中的关键词集合
		updateKeywordToKeywordGraph(keywordGraph,keyword)
	return keywordGraph

def updateKeywordToKeywordGraph(keywordGraph,keyword):
	print(keyword)
	keywordSize = len(keyword)
	preIndex = 0
	nowIndex = 0
	nowIndex = getKeywordIndex(keywordGraph,keyword[0])
	if nowIndex == -1:
		keywordGraph.append({"keyword":keyword[0],"sum":0,"preList":[],"preSum":0,"rearList":[],"rearSum":0})
		nowIndex = len(keywordGraph)-1
	temp = 0
	#数量自增1
	while temp < keywordSize:
		#temp为每个关键词的索引
		#updateKeywordCatalog(keywordGraph[0]["catalog"],keyword[temp],nowIndex)
		#至少有1个
		keywordGraph[nowIndex]["sum"] += 1
		keywordGraph[0]["sum"] += 1
		nextIndex = 0
		if temp < keywordSize - 1:
			nextIndex = getKeywordIndex(keywordGraph,keyword[temp+1])
			if nextIndex == -1:
				#没找到
				keywordGraph.append({"keyword":keyword[temp+1],"sum":0,"preList":[],"preSum":0,"rearList":[],"rearSum":0})
				nextIndex = len(keywordGraph)-1
		if temp == 0:
			#只更新后驱
			updateRearList(keywordGraph[nowIndex],nextIndex)
		elif temp == keywordSize-1:
			#只更新前驱
			updatePreList(keywordGraph[nowIndex],preIndex)
		else:
			updatePreList(keywordGraph[nowIndex],preIndex)
			updateRearList(keywordGraph[nowIndex],nextIndex)
		temp += 1
		preIndex = nowIndex
		nowIndex = nextIndex

def updateKeywordCatalogToKeywordGraph(keywordGraph):
	temp = 1
	keywordGraphSize = len(keywordGraph)
	while temp < keywordGraphSize:
		keyword = keywordGraph[temp]["keyword"]
		keywordSum = keywordGraph[temp]["sum"]#出现次数
		if keywordSum > 2:
			#关键词合格
			updateKeywordCatalog(keywordGraph[0]["catalog"],keyword,temp)
		else:
			pass
		temp += 1

def updatePreList(root,preIndex):
	preListSize = len(root["preList"])
	status = False
	for i in range(preListSize):
		if root["preList"][i]["index"] == preIndex:
			#已找到
			status = True
			#更改状态
			root["preList"][i]["sum"] += 1
			break
	if status:
		pass
	else:
		#没找到则添加
		root["preList"].append({"index":preIndex,"sum":1})
	root["preSum"] += 1

def updateRearList(root,rearIndex):
	rearListSize = len(root["rearList"])
	status = False
	for i in range(rearListSize):
		if root["rearList"][i]["index"] == rearIndex:
			#已找到
			status = True
			#更改状态
			root["rearList"][i]["sum"] += 1
			break
	if status:
		pass
	else:
		#没找到则添加
		root["rearList"].append({"index":rearIndex,"sum":1})
	root["rearSum"] += 1



def getChildStrType(childStr):
	if is_chinese(childStr[0]):
		return 1
	elif is_alphabet(childStr[0]):
		return 2
	elif is_number(childStr[0]):
		return 3
	elif is_SpecialChar(childStr[0]):
		return 4
	else:
		return -1

def getInnorKeywordIndexList(list_a,list_b):
	innerKeywordIndexList = []
	for a in list_a:
		for b in list_b:
			if a == b:
				#找到相同的关键词索引
				innerKeywordIndexList.append(b)
				break
	return innerKeywordIndexList

def getWordCatalogIndexListFromStr(catalog,strTemp):
	wordCatalogIndexList = []
	for word in strTemp:
		wordCatalogIndexList.append(getKeywordCatalogIndex(catalog,word))
	return wordCatalogIndexList

def judgeStr(sequencyStr,windowSize):
	status = -1
	for i in sequencyStr:
		if i == '1':
			if status < windowSize:
				#说明在范围内
				status = 0
			else:
				#相邻两个1中间0的个数超过上限，被认为发散
				return False
		else:
			#遇到0
			if status > -1:
				#说明遇到1
				status += 1
	return True


def sortKeywordList(keywordList,windowSize):
	quickSortByProb(keywordList,0,len(keywordList)-1)
	temp = 0
	preProb = 0
	preProbIndex = 0
	while temp < len(keywordList):
		nowSum = keywordList[temp]["sum"]
		nowSequency = keywordList[temp]["sequency"]
		keyword = keywordList[temp]["keyword"]
		if nowSum == 1 or not judgeStr(nowSequency,windowSize) or len(keyword)-nowSum > windowSize:
			#删除
			del keywordList[temp]
		else:
			#按照sum进行排序
			nowProb = keywordList[temp]["prob"]
			if nowProb != preProb:
				#概率不相等
				quickSortBySum(keywordList,preProbIndex,temp-1)
				preProb = nowProb
				preProbIndex = temp
			else:
				pass
			temp += 1

def getKeywordFromSearchStr(keywordGraph,searchStr):
	catalog = keywordGraph[0]["catalog"]
	# strList = getStrList(searchStr)
	# #预分割
	# for strTemp in strList:
	# 	if is_chinese(strTemp[0]) or is_alphabet(strTemp[0]):
	keywordListTemp = []
	strTemp = searchStr
	strTempSize = len(strTemp)
	for i in range(strTempSize):
		now = strTemp[i]#当前字符
		nowIndex = getKeywordCatalogIndex(catalog,now)
		nowKeywordIndexList = catalog[nowIndex]["indexList"]
		#获取包含该字符的关键词列表
		for keywordIndex in nowKeywordIndexList:
			if i == 0:
				keywordListTemp.append({"index":keywordIndex,"sum":1,"wordList":[i]})
			else:
				status = False
				for keywordTemp in keywordListTemp:
					if keywordIndex == keywordTemp["index"]:
						keywordTemp["sum"] += 1
						keywordTemp["wordList"].append(i)
						break
				if status:
					pass
				else:
					#没找到，则添加
					keywordListTemp.append({"index":keywordIndex,"sum":1,"wordList":[i]})
		#添加完毕,准备添加下一个字符
	keywordList = []
	for i in keywordListTemp:
		if i["sum"] > 1:
			keywordIndex = i["index"]
			keywordSum = keywordGraph[keywordIndex]["sum"]
			keyword = keywordGraph[keywordIndex]["keyword"]
			wordList = i["wordList"]
			sequencyList = list("0"*strTempSize)
			for j in wordList:
				sequencyList[j] = "1"
			sequencyStr = ''.join(sequencyList)
			keywordList.append({"keyword":keyword,"keywordSum":keywordSum,"prob":i["sum"]/len(keyword),"sequency":sequencyStr,"sum":i["sum"]})
	sortKeywordList(keywordList,2)
	for i in keywordList:
		print(i)
	results = []
	maxScore = "1"*strTempSize#满分
	nowScore = ""
	for i in keywordList:#贪心算法
		result = binSubtraction(maxScore,i["sequency"])
		if result != -1:
			#可以相减
			results.append({"word":i["keyword"],"sequency":i["sequency"],"sum":i["keywordSum"]})
			maxScore = result
		else:
			#不能相减，换下一个
			pass
	#计算匹配度
	quickSortBySum(results,0,len(results)-1)
	#strTemp,maxScore
	print(results)

def binSubtraction(bin_a,bin_b):
	lenTemp = len(bin_a)
	result = ""
	for i in range(lenTemp):
		if bin_a[i] == bin_b[i]:
			#消去
			result += '0'
		else:
			#不相等
			if bin_a[i] == '1' and bin_b[i] == '0':
				result += '1'
			else:
				#不行，返回-1，不能做减法
				return -1
	return result
#主函数
def getIndexFromKeywordGraph(keywordGraph,word):
	keywordGraphSize = len(keywordGraph)
	for i in range(keywordGraphSize):
		if keywordGraph[i]["word"] == word:
			return i
	return -1

def getInitialKeywordGraph1(dataSet):
	initialKeywordGraph = []
	for data in dataSet:
		updateKeywordToKeywordGraph1(initialKeywordGraph,data)
	return initialKeywordGraph

def updateKeywordToKeywordGraph1(keywordGraph,keyword):
	firstWord = keyword["keyword"][0]
	index = getIndexFromKeywordGraph(keywordGraph,firstWord)
	if index == -1:
		keywordGraph.append({"word":firstWord,"keywordList":[keyword]})
	else:
		keywordGraph[index]["keywordList"].append(keyword)


def getKeywordList1(keywordGraph,searchStr):
	temp = 0
	preTemp = 0
	matchIndex = -1
	matchSum = 0
	keywordList = []
	nowKeywordList = []
	while temp < len(searchStr):
		now = searchStr[temp]
		if len(nowKeywordList) == 0:
			index = getIndexFromKeywordGraph(keywordGraph,now)
			nowKeywordList = keywordGraph[index]["keywordList"]
			matchIndex = -1
			temp += 1
		else:
			print("ok")
			status = False
			dataTemp = []
			for keywordTemp in nowKeywordList:
				keyword = keywordTemp["keyword"]
				if len(keyword)-1 >= temp-preTemp and keyword[temp - preTemp] == now:
					status = True
					dataTemp.append(keywordTemp)
					if len(keyword)-1 == temp-preTemp:
						#遇到完全匹配关键词
						matchIndex = temp+1
						matchSum = keywordTemp["sum"]
					break
			if not status:
				#没找到，说明遇到断点
				if matchIndex != -1:
					#保存完全匹配关键词
					keywordList.append({"keyword":searchStr[preTemp:matchIndex],"sum":matchSum})
					matchIndex = -1
					matchSum = 0
				else:
					#没有遇到完全匹配关键词，则按顺序保存
					#准则:尽量保存有用的信息，提高检索的成功率
					if temp - preTemp > 1:
						keywordList.append({"keyword":searchStr[preTemp:temp],"sum":1})
				nowKeywordList = []
				preTemp = temp
			else:
				#找到
				nowKeywordList = dataTemp
				temp += 1
	temp = 0
	if matchIndex != -1:
		#保存完全匹配关键词
		keywordList.append({"keyword":searchStr[preTemp:matchIndex],"sum":matchSum})
	else:
		if preTemp < len(searchStr)-1:
			#没有完全匹配到关键词
			keywordList.append({"keyword":searchStr[preTemp:len(searchStr)],"sum":1})
	print(keywordList)
	return keywordList

def maxStrForwardMatching(keywordGraph,searchStr):
	strList = getStrListFromSentence(searchStr)
	keywordList = []
	for strTemp in strList:
		print(strTemp)
		if is_chinese(strTemp[0]) or is_alphabet(strTemp[0]):
			keywordList += getKeywordList1(keywordGraph,strTemp)
		elif is_number(strTemp[0]) or is_SpecialChar(strTemp[0]):
			#遇到特殊字符和数字则直接保留
			keywordList.append(strTemp)
		else:
			pass
	return keywordList

def updateKeywordDatabase(keywordDatabase,keyword):
	for keywordTemp in keywordDatabase:
		if strCompare(keyword,keywordTemp["keyword"]):
			#匹配到已有字符串
			keywordTemp["sum"] += 1
			return
	keywordDatabase.append({"keyword":keyword,"sum":1})
	return

def getInitialKeywordDatabase1(dictionary,dataSet,compareStandard):
	chKeywordDatabase = []
	enKeywordDatabase = []
	for data in dataSet:
		strList = getStrList(data)
		#分离中英文字符串
		for strTemp in strList:
			if is_chinese(strTemp[0]):
				#是中文，记录中文关键词
				chineseKeywordList = getChineseKeyword(dictionary,strTemp,compareStandard)
				for keyword in chineseKeywordList:
					updateKeywordDatabase(chKeywordDatabase,keyword)
			elif is_alphabet(strTemp[0]):
				#是英文，直接保存
				updateKeywordDatabase(enKeywordDatabase,strTemp.lower())
			else:
				#其它字符
				pass

def updateKeywordDatabaseToLowDimension(keywordDatabase):
	temp = 0
	while temp < len(keywordDatabase):
		if keywordDatabase[temp]["sum"] < 11:
			#删除
			del keywordDatabase[temp]
		else:
			#不删除
			temp += 1

def updateTitleListLabel(keywordGraph):
	dataSet = getDataListFromMySql()
	standard = 50
	for data in dataSet:
		print("当前记录 : %s"%data["title"])
		keywordList = maxStrForwardMatching2(keywordGraph,data["title"],standard)
		label = "计算机"
		tableName= "resource"
		for keyword in keywordList:
			label += "-"+keyword["keyword"]
		print(label)
		sql = "update "+tableName+" set label = '"+label+"' where tid = '"+data["tid"]+"'"
		print(sql)
		updateDataToMySql(sql)


def printChildren(children):
	for child in children:
		print(child)

def getKeywordList2(keywordGraph,searchStr,standard):
	temp = 0
	preTemp = 0
	matchIndex = -1
	matchProb = 0
	keywordList = []
	nowKeywordList = []
	while temp < len(searchStr):
		now = searchStr[temp]
		if len(nowKeywordList) == 0:
			index = getIndexFromKeywordGraph(keywordGraph,now)
			nowKeywordList = keywordGraph[index]["keywordList"]
			print(nowKeywordList)
			temp += 1
		else:
			status = False
			dataTemp = []
			print("*"*30)
			for keywordTemp in nowKeywordList:
				print(keywordTemp)
				keyword = keywordTemp["keyword"]
				#keyword = keywordTemp["keyword"]
				if len(keyword)-1 >= temp-preTemp: 
					#正向最大串匹配算法
					if keyword[temp - preTemp] == now:
						status = True
						dataTemp.append(keywordTemp)
					if strCompare(keyword,searchStr[preTemp:temp+1]) and keywordTemp["sum"] > standard:
						#找到完全匹配的关键词,且出现数量大于标准
						matchIndex = temp+1
						matchProb = keywordTemp["sum"]
					print("keyword : ",keyword,"完全匹配索引 : ",matchIndex)
			if not status:
				#没找到
				print("出现匹配断点,完全匹配索引 : ",matchIndex)
				if matchIndex != -1:
					#有完全匹配的关键词
					print("添加 : ",searchStr[preTemp:matchIndex])
					keywordList.append({"keyword":searchStr[preTemp:matchIndex],"sum":matchProb})
					matchProb = 0
					matchIndex = -1
				nowKeywordList = []
				preTemp = temp
			else:
				#找到
				print("当前字符 : ",now,"完全匹配串 : ",searchStr[preTemp:matchIndex])
				nowKeywordList = dataTemp
				temp += 1
	if matchIndex != -1:
		#找到完全匹配的关键词
		keywordList.append({"keyword":searchStr[preTemp:matchIndex],"sum":matchProb})
	print(keywordList)
	return keywordList

def getEnKeywordList(keywordGraph,strTemp,standard):
	firstWord =strTemp[0]
	index = getIndexFromKeywordGraph(keywordGraph,firstWord)
	#获取首字母索引
	if index != -1:
		keywordListTemp = keywordGraph[index]["keywordList"]
		for keywordTemp in keywordListTemp:
			#完全相等
			if strCompare(strTemp,keywordTemp["keyword"]) and keywordTemp["sum"] > standard:
				return keywordTemp
		#没有关键词
	return None

def maxStrForwardMatching2(keywordGraph,searchStr,standard):
	strList = getStrListFromSentence(searchStr)
	keywordList = []
	for strTemp in strList:
		print(strTemp)
		if is_chinese(strTemp[0]):
			keywordList += getKeywordList2(keywordGraph,strTemp,standard)
		elif is_alphabet(strTemp[0]):
			status = getEnKeywordList(keywordGraph,strTemp,standard)
			if status != None:
				#说明有关键词
				keywordList.append(status)
			else:
				pass
		elif is_number(strTemp[0]) or is_SpecialChar(strTemp[0]):
			#遇到特殊字符和数字
			pass
		else:
			pass
	#去重
	temp = 0
	while temp < len(keywordList)-1:
		nowKeyword = keywordList[temp]["keyword"]
		selectTemp = temp + 1
		while selectTemp < len(keywordList):
			selectKeyword = keywordList[selectTemp]["keyword"]
			if strCompare(nowKeyword,selectKeyword):
				#相等，则删除
				del keywordList[selectTemp]
			else:
				#不相等，比较下一个
				selectTemp += 1
		temp += 1
	quickSortBySum(keywordList,0,len(keywordList)-1)
	return keywordList

def getHistoryList():
	historyList = [
	1209346809,
	1005226030,
	1003334006,
	1004572025,
	1004171002,
	1209570828,
	1003664023,
	1004578051,
	983003,
	1002893007,
	555001,
	1005096022,
	1208923802,
	1208936828,
	1004714034,
	1208965816,
	1004722032,
	1208923815,
	1005152007,
	1209465848]



if __name__ == "__main__":
	#historyList = getHistoryList()
	# chKeywordDatabase = getDataListFromJson("ch_keyword_0612_v2.json")
	# enKeywordDatabase = getDataListFromJson("en_keyword_0612_v2.json")
	# # updateKeywordDatabaseToLowDimension(chKeywordDatabase)
	# # updateKeywordDatabaseToLowDimension(enKeywordDatabase)
	# keywordGraph = getInitialKeywordGraph1(chKeywordDatabase)
	# for i in enKeywordDatabase:
	# 	updateKeywordToKeywordGraph1(keywordGraph,i)
	# storeDataListToJson(keywordGraph,"keywordGraph-0612-v2.json")
	keywordGraph = getDataListFromJson("keywordGraph-0612-v2.json")
	#storeDataListToJson(chKeywordDatabase,"ch_keyword_0612_v2.json")
	#storeDataListToJson(enKeywordDatabase,"en_keyword_0612_v2.json")
	#titleList = getTitleListFromMysql()
	#updateTitleListLabel(keywordGraph)
	print(maxStrForwardMatching(keywordGraph,"黑马程序员java项目开发"))
	#storeDataListToJson(dataSet,"keywordGraph_keywordList-0612-v2.json")
	# titleList = ["python数据分析"]
	#dictionary = getInitialDictionary(titleList,10)
	#storeDataListToJson(dictionary,"dictionary-0611-v1.json")
	# dictionary = getDataListFromJson("dictionary-0611-v1.json")
	# getInitialKeywordDatabase1(dictionary,titleList,0.4)
	#updateDictionaryToLowDimension(dictionary,3)
	#storeDataListToJson(dictionary,"dictionary-0611-v2_lowDimension_by_3.json")
	# dataSet = []
	# for i in titleList:
	# 	keyword = getKeywordList(dictionary,i,0.4)
	# 	print(keyword)
	# 	dataSet.append({"title":i,"keywordList":keyword})
	# storeDataListToJson(dataSet,"dictionary_keywordList-0612-v2_0.40.json")
	#dictionary = getDataListFromJson("dictionary-0604-v1.json")
	#keywordList = getKeywordListFromDataSet(dictionary,titleList)
	#keywordGraph = getDataListFromJson("keywordGraph-0606-v1.json")
	#updateKeywordCatalogToKeywordGraph(keywordGraph)
	#storeDataListToJson(keywordGraph,"keywordGraph-0606-v1.json")
	#keywordDatabase = getInitialKeywordDatabase(keywordGraph)
	#keywordDatabase = getDataListFromJson("keywordDatabase-0608-v2.json")
	#storeDataListToJson(keywordDatabase,"keywordDatabase-0610-v1.json")
	#dataList = getDataListFromJson("keywordDatabase-0608-v2.json")
	#storeDataListToMySql(dataList[1:])
	#searchStr = "python爬虫办公自动化好玩"
	#startTime = time()
	#getKeywordFromSearchStr(keywordDatabase,searchStr)
	#endTime = time()
	#print("运行时间：",endTime-startTime)
	#print(getStrList(test))
	#print(getKeywordList(dictionary,test,0.4))
	# dataSet = []
	# for i in titleList:
	# 	dataSet.append(getKeywordList(dictionary,i,0.30))
	# storeDataListToJson(dataSet,"dictionary_keywordList-0610-v2-0.30.json")
	# keywordList = getDataListFromJson("dictionary_keywordList-0604-v1.json")
	#keywordList = [["python", "爬虫", "+", "办公", "自动化", "+", "好玩", "diy"]]
	#keywordGraph = getDataListFromJson("keywordGraph-0604-v1.json")
	# temp = 1
	# keywordList = []
	# while temp < len(keywordGraph):
	# 	keywordList.append({"keyword":keywordGraph[temp]["keyword"],"sum":keywordGraph[temp]["sum"]})
	# 	temp += 1
	# storeDataListToMySql(keywordList)
	#keywordList = getDataListFromMySql("SELECT keyword from keyword")
	#keywordGraph = getInitialKeywordGraph1(keywordList)
	#storeDataListToJson(keywordGraph,"keywordGraph-0610-v1.json")
	# strList = getStrListFromSentence("黑马程序员c++视频教程")
	# keywordGraph = getDataListFromJson("keywordGraph-0610-v1.json")
	# for i in strList:
	# 	getKeywordList1(keywordGraph,i)
	# keywordGraph = getInitialKeywordGraph1(dataSet)
	# storeDataListToJson(keywordGraph,"keywordGraph-0610-v2.json")
	# keywordGraph = getDataListFromJson("keywordGraph-0610-v2.json")
	# print(maxStrForwardMatching(keywordGraph,"计算机2级"))
