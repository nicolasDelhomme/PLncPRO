'''
PLNCPRO
This file takes the input of framefinder and extracts features.
It takes th frame finder input as argument
Author : Urminder Singh
email: urmind13_sit@jnu.ac.in
UrMi 14/1/2016
'''

import sys
import math
import re
#from Bio import SeqIO
#from collections import OrderedDict

#open framefinder output file
with open(sys.argv[1]) as f:
	content=f.readlines()
#ignore firstline
content.pop(0)
#store for each sequence
qids=[]
ffscore=[]
orfcoverage=[]

for line in content:
	if '>' in line:
		qids.append(line.split(' ')[0].split('>')[1])
		#print line
		#extract score
		#[framefinder (3,2109) score=273.82 used=99.86% {forward,strict} ]
		#match = re.search(r'score=([\-\d]\d+.\d+)',line)
		match = re.search(r'score=(\d+.\d+)',line)  
		#print match.group(1)
		ffscore.append(float(match.group(1)))
		#extract coverage
		match = re.search(r'used=(\d+.\d+)',line) 
		#print match.group(1)
		orfcoverage.append(float(match.group(1)))

#print qids,ffscore,orfcoverage

#write file with the fearures
fname=sys.argv[1]+'_framefinderfeatures'
f = open(fname,'w')
f.write(str('seqid')+'\t'+str('score')+'\t'+str('orf_coverage')+'\n')
for i in range(len(qids)):
	f.write(str(qids[i])+'\t'+str(ffscore[i])+'\t'+str(orfcoverage[i])+'\n')
#print 'file: '+fname+' writen'

