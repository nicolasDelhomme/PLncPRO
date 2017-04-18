'''
PLNCPRO
This files reads the blastx output and extracts features
for each query. This takes as input the blast output in the following format
"qseqid sseqid pident evalue qcovs qcovhsp score bitscore qframe sframe"
this output is generated by blast command:
./blastx -query ex.fa -db unirefdb -strand plus -evalue 1e-10 -outfmt '6 qseqid sseqid pident evalue qcovs qcovhsp score bitscore qframe sframe' -out blastres2.txt -num_threads 4

This file reads all results from blast and doesnt filter based on ident or qcov
Author : Urminder Singh
email: urmind13_sit@jnu.ac.in
UrMi 5/2/16
'''
from __future__ import division
import sys
import math
import re
import threading
from collections import OrderedDict
import Queue
import urllib2
from random import randint
import time
start_time = time.time()
#################################################################
###Defaults

################################################################

##################################################################
########################Define Functions

def split_list(seq, num):
	avg = len(seq) / float(num)
	out = []
	last = 0.0

	while last < len(seq):
		out.append(seq[int(last):int(last + avg)])
		last += avg

	return out

################################################################
####class for multithreading

def getlog10(val):
	if val == 0:
		return -250
	else:
		return math.log(val)

def getlog2(val):
	if val == 0:
		return 0
	else:
		return math.log(val,2)
def getentropy(a,b,c):
	#print a,b,c
	t=a+b+c
	if t==0:
		return 1
	pa=a/t
	pb=b/t
	pc=c/t
	#print -1*((pa*getlog2(pa))+(pb*getlog2(pb))+(pc*getlog2(pc)))
	return -1*((pa*getlog2(pa))+(pb*getlog2(pb))+(pc*getlog2(pc)))

class BlastParse(threading.Thread):
	def __init__(self,data,ids):
        	super(BlastParse, self).__init__()
        	self.data=data
        	self.ids=ids
        	self.reslist=[]
	def run(self):
		for q in self.ids:
			ctr=0
			hitscore=0
			bitscore=0
			frames=0
			frame1=0
			frame2=0
			frame3=0
			#print 'now q is',q
			for line in self.data:
				if q == line.split('\t')[0]:
					#print 'here'
					perident=float(line.split('\t')[2])
					evalue=float(line.split('\t')[3])
					qcov=float(line.split('\t')[4])
					qframe=int(line.split('\t')[8])
					#print 'q   qframe'
					#print q,str(qframe)
					
					ctr=ctr+1
					hitscore=hitscore+(-1*getlog10(evalue))
					bitscore=bitscore+float(line.split('\t')[7])
					if(qframe==1):
						frame1=frame1+1
					elif(qframe==2):
						frame2=frame2+1
					elif(qframe==3):
						frame3=frame3+1
					
			#print q,':',str(ctr)
			#self.reslist.append(str(q)+'~'+str(ctr))
			#hitscore=hitscore/ctr
			#self.reslist.append([str(q),ctr])
			#print q,str(frame1),str(frame2),str(frame3),str(qcov)			
			self.reslist.append([str(q),ctr,hitscore,frame1,frame2,frame3,bitscore])			
			

def joinresults(l):
	#print l
	all_qids=[]
	for x in l:
		for y in x:
			#print y[0]
			all_qids.append(y[0])
			
	#remove duplicates
	all_qids=list(OrderedDict.fromkeys(all_qids))	
	#print all_qids
	numhits=[]
	hit_scores=[]
	bit_scores=[]
	frame1=0
	frame2=0
	frame3=0
	frame_en=[]
	foundflag=0
	for q in all_qids:
		ctr=0
		hitscore=0
		bitscore=0
		frame1=0
		frame2=0
		frame3=0
		for x in l:
			foundflag=0
			for y in x:
				
				if q==y[0]:
					#print 'here'
					#print y[1]
					ctr=ctr+int(y[1])
					hitscore=hitscore+float(y[2])
					bitscore=bitscore+float(y[6])
					frame1=frame1+float(y[3])
					frame2=frame2+float(y[4])
					frame3=frame3+float(y[5])
					foundflag=1
			#if foundflag==0:
			#	print 'not found'
			#	break
		numhits.append(ctr)
		hit_scores.append(hitscore)
		bit_scores.append(bitscore)
		#print q+'all frames'
		frame_en.append(getentropy(frame1,frame2,frame3))
	#print numhits
	return all_qids,numhits,hit_scores,frame_en,bit_scores


###################################################################
#open blast file
with open(sys.argv[1]) as f:
	content=f.readlines()
#define lists for data
queryids=[]
numhits=[] #number of hits per query

#print 'Reading blast output...'

##divide the blast file (content) and do multithreading
#print len(content)
#N=len(content)/500
N=10
c=split_list(content,N )
#extract queryids for each sublist i.e. c[i]
qids=[]
for x in c:
	q=[]
	for line in x:
		q.append(line.split('\t')[0])
	#remove duplicates
	q=list(OrderedDict.fromkeys(q))
	qids.append(q)
	
#print 'final qids'
#print qids


#for each split run a thread

thread_list = []
for i in range(len(c)):
	# Instantiates the thread
	# (i) does not make a sequence, so (i,)
	#t = threading.Thread(target=countnumhits(c[i],qids[i]), args=(i,))
	t=BlastParse(c[i],qids[i])
	#print t
	# Sticks the thread in a list so that it remains accessible
	thread_list.append(t)

# Starts threads
for thread in thread_list:
	thread.start()
	#print '\n\n\n'
for thread in thread_list:
	thread.join()

# Demonstrates that the main process waited for threads to complete
#print "Done!"
#print("--- %s seconds ---" % (time.time() - start_time))

#print 'all res'
res=[]
for thread in thread_list:
	res.append(thread.reslist)
queryids,numhits,hitscores,frame_entropy,bitscores=joinresults(res)
#queryids,numhits=joinresults(res)

#print 'Total queries',str(len(queryids))
#write features to file
#print 'Writing to file...'
#write query ids and hits to file
fname=sys.argv[1]+'_blastfeatures'
f = open(fname,'w')
f.write(str('seqid')+'\t'+str('all_numhits')+'\t'+str('all_HitScore')+'\t'+str('all_Frame_Entropy')+'\t'+str('all_Bitscore')+'\n')
for i in range(len(queryids)):
	f.write(str(queryids[i])+'\t'+str(numhits[i])+'\t'+str(hitscores[i])+'\t'+str(frame_entropy[i])+'\t'+str(bitscores[i])+'\n')
	#f.write(str(queryids[i])+'\t'+str(numhits[i])+'\n')

#print 'File:',fname,'written'
#print("--- %s seconds ---" % (time.time() - start_time))









