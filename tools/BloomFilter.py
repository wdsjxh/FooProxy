#coding:utf-8

import time
import math
import random
import logging.config
from cmath 	   import *
from BitVector import BitVector

logger = logging.getLogger()

class BloomFilter(object):

	def __init__(self,error_rate,element_num=None,bit_num=None):
		#初始化布隆过滤器,给定误判率f,哈希函数个数k,过滤器位数组位数m,元素个数n
		#接下来都以f为最小值作为计算前提
		#当k = ln2(m/n)时错误率f最小，这时f = (1/2)**k = (1/2)**(m*ln2/n)
		# f=2**(-m*ln2/n),两边取ln得到: lnf=(-m*ln2/n)*ln2,所以
		# n=-m*ln2*ln2/lnf
		#如果给定了f,m，那么可以计算出当f是最小的误判率时布隆过滤器
		#能够过滤的元素的个数是多少个n
		if bit_num and element_num:
			raise ValueError('Multi arguments are given,needs 2 args,but got 3.')
		elif bit_num:
			element_num = -1 * bit_num * (log(2.0)*log(2.0)) / log(error_rate)
		elif element_num:
			bit_num = -1 * element_num * log(error_rate) / (log(2.0)*log(2.0)) 
		else:
			raise ValueError('Function arguments missing.2 arguments should be given at least.')
		self.error_rate = error_rate
		self.bit_num    = self.align_4bytes(bit_num.real)
		self.element_num= int(math.ceil(element_num.real))
		self.hash_num = int(math.ceil((log(2.0)*self.bit_num/element_num).real))
		self.bit_array = BitVector(size=self.bit_num)
		#生成k个哈希函数的种子，便于生成哈希函数
		self.hash_seeds = self.generate_hashseeds(self.hash_num)
		self.__len = 0

	def __len__(self):
		return self.__len


	def generate_hashseeds(self,hash_num):
		seeds = []
		#初始化为全0的种子列表
		for i in range(hash_num):
			seeds.append(0)
		#利用程序的起始计数时间或者CPU时间作为种子
		#每个种子之间的间隔要大，不然哈希后在位数组中的位置有些会重叠
		while len(set(seeds)) != hash_num:
			for index,value in enumerate(seeds):
				seeds[index] = time.process_time()*random.randint(500,10000)+random.randint(100,50000)
		return seeds


	def hash_element(self,element,seed):
		hash_value = 1
		#对整个元素进行自定义的哈希运算：种子*hash_value+每个元素字符的对应数值
		for char in str(element):
			hash_value = hash_value*seed + ord(char)
		return hash_value


	def insert(self,element):
		guarder = []
		for seed in self.hash_seeds:
			#最后要取模防止数值越界（超过位数组长度）
			hashed_value = int(abs(self.hash_element(element,seed)))%self.bit_num
			guarder.append(self.bit_array[hashed_value])
			#对应位置1表示存入布隆过滤器
			self.bit_array[hashed_value]=1
		#判断元素以前是否被插入过
		if guarder.count(1)==self.hash_num:
			logger.warning('The element "%s" had been inserted into the Filter.It will not be put in the list.'%element)
			return False
		self.__len+=1
		return True


	def is_exists(self,element):
		#判断是否在布隆过滤器里，对元素也要进行K个哈希函数的哈希后再判断
		for seed in self.hash_seeds:
			hashed_value = int(abs(self.hash_element(element,seed)))%self.bit_num
			if self.bit_array[hashed_value] == 0:
				return False 
		return True


	def align_4bytes(self,bit_num):
	#对int型数值的内存对齐，可以让CPU访问内存读写高效
		return int(math.ceil(bit_num/32))*32
	

