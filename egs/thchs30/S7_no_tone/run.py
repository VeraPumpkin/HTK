# -*- coding: utf-8 -*- 
import env
import scripts as spt

import shutil
import os

def prepare_phones(dir):
	fw=open(dir+'/phones','w')
	print >>fw,'v'
	print >>fw,'n'
	print >>fw,'s'
	fw.close()
	fw=open(dir+'/dict','w')
	print >>fw,'v v'
	print >>fw,'n n'
	print >>fw,'s s'
	fw.close()
	fw=open(dir+'/phnmap','w')
	print >>fw,'a v'
	print >>fw,'aa v'
	print >>fw,'ai v'
	print >>fw,'an v'
	print >>fw,'ang v'
	print >>fw,'ao v'
	print >>fw,'b n'
	print >>fw,'c n'
	print >>fw,'ch n'
	print >>fw,'d n'
	print >>fw,'e v'
	print >>fw,'ee v'
	print >>fw,'ei v'
	print >>fw,'en v'
	print >>fw,'eng v'
	print >>fw,'er v'
	print >>fw,'f n'
	print >>fw,'g n'
	print >>fw,'h n'
	print >>fw,'i v'
	print >>fw,'ia v'
	print >>fw,'ian v'
	print >>fw,'iang v'
	print >>fw,'iao v'
	print >>fw,'ie v'
	print >>fw,'ii v'
	print >>fw,'in v'
	print >>fw,'ing v'
	print >>fw,'iong v'
	print >>fw,'iu v'
	print >>fw,'ix v'
	print >>fw,'iy v'
	print >>fw,'iz v'
	print >>fw,'j n'
	print >>fw,'k n'
	print >>fw,'l n'
	print >>fw,'m n'
	print >>fw,'n n'
	print >>fw,'o v'
	print >>fw,'ong v'
	print >>fw,'oo v'
	print >>fw,'ou v'
	print >>fw,'p n'
	print >>fw,'q n'
	print >>fw,'r n'
	print >>fw,'s n'
	print >>fw,'sh n'
	print >>fw,'t n'
	print >>fw,'u v'
	print >>fw,'ua v'
	print >>fw,'uai v'
	print >>fw,'uan v'
	print >>fw,'uang v'
	print >>fw,'ueng v'
	print >>fw,'ui v'
	print >>fw,'un v'
	print >>fw,'uo v'
	print >>fw,'uu v'
	print >>fw,'v v'
	print >>fw,'van v'
	print >>fw,'ve v'
	print >>fw,'vn v'
	print >>fw,'vv v'
	print >>fw,'x n'
	print >>fw,'z n'
	print >>fw,'zh n'
	print >>fw,'sil s'
	fw.close()
def prepare_data(thchs30,tools):
	
	# create directory
	print '# create directory'
	dir = ['data','hmms','result']
	data_dir = ['train','test','conf','phones','dict']
	for i in dir:
		if os.path.exists(i):shutil.rmtree(i)
		os.mkdir(i)
	[os.makedirs('data/'+i) for i in data_dir]
	# prepare data prompts & train label
	
	print '# prepare data prompts'
	for i in ['train','test']:
		data_src = thchs30+'/data_thchs30/' + i
		path_list = spt.get_suffix(data_src,'.trn')
		fw = open('data/'+i+'/prompts','a')
		for path in path_list:
			path = path.replace('\\','/')
			lab_src = data_src+'/' + open(path).read()
			wrd_scp = repr(open(lab_src[:-1],'r').read().decode('utf-8'))
			wrd_scp = spt.utf_to_str(wrd_scp)
			wrd_scp=wrd_scp.split(r'\\n')
			Chinese = wrd_scp[0].replace('\\u','w').replace('l = ','')
			pinyin = wrd_scp[1]
			phones =wrd_scp[2]
			
			if i == 'train':
				wrd_scp = path.replace('.wav.trn','') + ' ' + Chinese + '\n'
				fw.write(wrd_scp)
			else:
				wrd_scp = path.split('/')[-1].replace('.wav.trn','') + ' ' + Chinese + '\n'
				fw.write(wrd_scp)
			
		fw.close()
	# generating words list from sentence
	print '# generating words list from sentence'
	cmd= 'perl '+tools+'/prompts2wlist' + \
	' data/train/prompts data/dict/wlist'
	os.system(cmd)
	
	#open('data/dict/wlist1','w').write(\
	#spt.remove_sign(open('data/dict/wlist','r').read(),'\da-z=')[2:])
	# copy dictionary
	print '# copy dictionary'
	lex = spt.utf_to_str(open(thchs30+'/resource/dict/lexicon.txt','r').read().decode('utf-8'))
	lex=lex.split('\\n')
	lex1=''
	for line in lex:
		pron=line.split(' ')
		wd = str(pron[0])
		phone=spt.remove_sign(' '.join(pron[1:]),'\d')
		lex1+=wd+' '+phone+'\n'
	print lex1
	open('data/dict/lexicon','w').write(lex1)

	# generating words prompts for train & test
	print ('# generating words prompts for train & test')
	cmd='perl '+tools+'/prompts2mlf data/train/trainwords.mlf'+\
	' data/train/prompts'
	os.system(cmd)
	cmd='perl '+tools+'/prompts2mlf data/test/testwords.mlf'+\
	' data/test/prompts'
	os.system(cmd)

	# copy phone list
	phones=open(thchs30+'/resource/dict/nonsilence_phones.txt','r').read();
	phones=phones.split('\n')
	mono=spt.remove_sign(phones[0],'\d')+'\n'
	for i in range(1,len(phones)-1):
		if spt.remove_sign(phones[i],'\d')!=spt.remove_sign(phones[i-1],'\d'):
			
			mono+=spt.remove_sign(phones[i],'\d')+'\n'
	open('data/phones/monophones0','w').write(mono+'sil')
	open('data/phones/monophones1','w').write(mono+'sp\nsil')
	# config: insert sil into sentence & delete sp
	fw = open(r'data\conf\mkphones.led','w')
	print >>fw,'EX\nIS sil sil\nDE sp'
	fw.close()
	# config: tied sil & sp
	fw = open(r'data\conf\sil.hed','w')
	print >>fw,'AT 2 4 0.2 {sil.transP}'
	print >>fw,'AT 4 2 0.2 {sil.transP}'
	print >>fw,'AT 1 3 0.3 {sp.transP}'
	print >>fw,'TI silst  {sil.state[3],sp.state[2]}'
	fw.close()
	# generating phones prompts
	cmd='HLEd -l * -d data/dict/lexicon -i data/train/trainphones.mlf '\
	r'data/conf/mkphones.led data/train/trainwords.mlf'
	print cmd
	os.system(cmd)
	
	prepare_phones('data/phones')
	
	plist=open('data/phones/phnmap','r').read().split('\n')
	plen=len(plist)
	print plen
	trainphn=open('data/train/trainphones.mlf','r').read()
	item1=trainphn.split('\n')
	for tmp in plist[:-1]:
		item=tmp.split(' ')
		for j in range(len(item1)):
			if item1[j]==item[0]:
				item1[j]=item[1]
	trainphn='\n'.join(item1)
	open('data/train/trainphones1.mlf','w').write(trainphn)
	open('data/train/trainphones1.mlf','w').write(trainphn)
	open('data/phones/phones1','w').write(open('data/phones/phones','r').read()+'sp\n')
	#生成 lab
	data_src = thchs30+'/data_thchs30/train'
	path_list = spt.get_suffix(data_src,'.trn')
	for path in path_list:
		path = path.replace('\\','/')
		lab_src = data_src+'/' + open(path).read()
		wrd_scp = repr(open(lab_src[:-1],'r').read().decode('utf-8'))
		wrd_scp = spt.utf_to_str(wrd_scp)
		wrd_scp=wrd_scp.split(r'\\n')
		Chinese = wrd_scp[0].replace('\\u','w').replace('l = ','')
		pinyin = wrd_scp[1]
		phones =spt.remove_sign(wrd_scp[2],'\d')
		
		item1=phones.split(' ')
		for tmp in plist[:-1]:
			item=tmp.split(' ')
			for j in range(len(item1)):
				if item1[j]==item[0]:
					item1[j]=item[1]
		phones='\n'.join(item1)		
		open(path.replace('.wav.trn','.lab'),'w').write(phones)	
	#mfcc 配置
	fw=open(r'data\conf\wav_config','w')
	
	print >>fw,'SOURCEFORMAT=WAVEFORM'
	print >>fw,'SOURCEFORMAT=WAV'
	print >>fw,'TARGETKIND=MFCC_0_D_A'
	print >>fw,'TARGETRATE=100000.0'
	print >>fw,'SAVECOMPRESSED=T'
	print >>fw,'USEHAMMING=T'
	print >>fw,'WINDOWSIZE=250000.0'
	print >>fw,'SAVEWITHCRC=T'
	print >>fw,'PREEMCOEF=0.97'
	print >>fw,'NUMCHANS=26'
	print >>fw,'CEPLIFTER=22'
	print >>fw,'NUMCEPS=12'
	fw.close()
	#训练 解码 配置
	fw=open(r'data\conf\config','w')
	print >>fw,'TARGETKIND=MFCC_0_D_A'
	print >>fw,'TARGETRATE=100000.0'
	print >>fw,'SAVECOMPRESSED=T'
	print >>fw,'USEHAMMING=T'
	print >>fw,'WINDOWSIZE=250000.0'
	print >>fw,'SAVEWITHCRC=T'
	print >>fw,'PREEMCOEF=0.97'
	print >>fw,'NUMCHANS=26'
	print >>fw,'CEPLIFTER=22'
	print >>fw,'NUMCEPS=12'
	fw.close()
	#生成mfcc prompts
	for i in ['train','test']:
		data_src=thchs30+'/data_thchs30/'+i
		fw1=open('data/'+i+'/mfcc.scp',"w")
		fw2=open('data/'+i+'/'+i+'.scp',"w")
		wav_list=spt.get_suffix(data_src,'.wav')
		print data_src
		wav_str='\n'.join(wav_list)
		mfcc_path=wav_str.replace('.wav','.mfc').replace('\\','/')
		
		mp=map(list,zip(wav_str.split('\n'),mfcc_path.split('\n')))
		pmt_list=[' '.join(i) for i in mp]
		wav_mfcc='\n'.join(pmt_list).replace('\\','/')
		fw1.write(wav_mfcc)
		fw2.write(mfcc_path)
	#生成 proto
	fw=open(r'data\conf\proto','w')
	print >>fw,'~o <STREAMINFO> 1 39'
	print >>fw,'<VECSIZE> 39<NULLD><MFCC_D_A_0><DIAGC>'
	print >>fw,'~h "proto"'
	print >>fw,'<BEGINHMM>'
	print >>fw,'<NUMSTATES> 5'
	print >>fw,'<STATE> 2'
	print >>fw,'<MEAN> 39'
	print >>fw,' -1.012254e+001 -7.264226e+000 -5.370609e+000 -9.712223e+000 -8.047407e+000 -5.681805e+000 -5.715530e+000 -8.866713e-001 -3.691204e+000 -1.679087e+000 -2.372116e+000 -1.992831e+000 5.435896e+001 3.500786e-003 3.751630e-003 -3.257445e-004 8.666397e-004 4.723764e-003 -5.870885e-004 2.242961e-004 -5.077728e-003 -4.136859e-003 -6.560616e-004 -4.315113e-003 -2.692402e-003 3.635559e-003 -9.592683e-005 -2.103158e-004 1.351117e-004 -1.661481e-005 -3.384908e-004 -2.177467e-004 -1.438305e-004 1.636888e-004 2.628795e-004 5.652815e-006 2.228666e-004 2.034386e-004 -1.619475e-005'
	print >>fw,'<VARIANCE> 39'
	print >>fw,' 1.019786e+002 5.942492e+001 7.969102e+001 8.208926e+001 7.801923e+001 7.487221e+001 7.644022e+001 6.621936e+001 6.555122e+001 4.695240e+001 4.796211e+001 3.524432e+001 1.175200e+002 4.562054e+000 3.524029e+000 3.336633e+000 4.190800e+000 4.308127e+000 4.198907e+000 4.401058e+000 4.303515e+000 3.945027e+000 3.243079e+000 2.985245e+000 2.440658e+000 5.602147e+000 6.298034e-001 5.834209e-001 5.080934e-001 6.770245e-001 7.052047e-001 7.098504e-001 7.490557e-001 7.594697e-001 6.945505e-001 5.957313e-001 5.417506e-001 4.463942e-001 8.994048e-001'
	print >>fw,'<GCONST> 1.383837e+002'
	print >>fw,'<STATE> 3'
	print >>fw,'<MEAN> 39'
	print >>fw,' -1.012254e+001 -7.264226e+000 -5.370609e+000 -9.712223e+000 -8.047407e+000 -5.681805e+000 -5.715530e+000 -8.866713e-001 -3.691204e+000 -1.679087e+000 -2.372116e+000 -1.992831e+000 5.435896e+001 3.500786e-003 3.751630e-003 -3.257445e-004 8.666397e-004 4.723764e-003 -5.870885e-004 2.242961e-004 -5.077728e-003 -4.136859e-003 -6.560616e-004 -4.315113e-003 -2.692402e-003 3.635559e-003 -9.592683e-005 -2.103158e-004 1.351117e-004 -1.661481e-005 -3.384908e-004 -2.177467e-004 -1.438305e-004 1.636888e-004 2.628795e-004 5.652815e-006 2.228666e-004 2.034386e-004 -1.619475e-005'
	print >>fw,'<VARIANCE> 39'
	print >>fw,' 1.019786e+002 5.942492e+001 7.969102e+001 8.208926e+001 7.801923e+001 7.487221e+001 7.644022e+001 6.621936e+001 6.555122e+001 4.695240e+001 4.796211e+001 3.524432e+001 1.175200e+002 4.562054e+000 3.524029e+000 3.336633e+000 4.190800e+000 4.308127e+000 4.198907e+000 4.401058e+000 4.303515e+000 3.945027e+000 3.243079e+000 2.985245e+000 2.440658e+000 5.602147e+000 6.298034e-001 5.834209e-001 5.080934e-001 6.770245e-001 7.052047e-001 7.098504e-001 7.490557e-001 7.594697e-001 6.945505e-001 5.957313e-001 5.417506e-001 4.463942e-001 8.994048e-001'
	print >>fw,'<GCONST> 1.383837e+002'
	print >>fw,'<STATE> 4'
	print >>fw,'<MEAN> 39'
	print >>fw,' -1.012254e+001 -7.264226e+000 -5.370609e+000 -9.712223e+000 -8.047407e+000 -5.681805e+000 -5.715530e+000 -8.866713e-001 -3.691204e+000 -1.679087e+000 -2.372116e+000 -1.992831e+000 5.435896e+001 3.500786e-003 3.751630e-003 -3.257445e-004 8.666397e-004 4.723764e-003 -5.870885e-004 2.242961e-004 -5.077728e-003 -4.136859e-003 -6.560616e-004 -4.315113e-003 -2.692402e-003 3.635559e-003 -9.592683e-005 -2.103158e-004 1.351117e-004 -1.661481e-005 -3.384908e-004 -2.177467e-004 -1.438305e-004 1.636888e-004 2.628795e-004 5.652815e-006 2.228666e-004 2.034386e-004 -1.619475e-005'
	print >>fw,'<VARIANCE> 39'
	print >>fw,' 1.019786e+002 5.942492e+001 7.969102e+001 8.208926e+001 7.801923e+001 7.487221e+001 7.644022e+001 6.621936e+001 6.555122e+001 4.695240e+001 4.796211e+001 3.524432e+001 1.175200e+002 4.562054e+000 3.524029e+000 3.336633e+000 4.190800e+000 4.308127e+000 4.198907e+000 4.401058e+000 4.303515e+000 3.945027e+000 3.243079e+000 2.985245e+000 2.440658e+000 5.602147e+000 6.298034e-001 5.834209e-001 5.080934e-001 6.770245e-001 7.052047e-001 7.098504e-001 7.490557e-001 7.594697e-001 6.945505e-001 5.957313e-001 5.417506e-001 4.463942e-001 8.994048e-001'
	print >>fw,'<GCONST> 1.383837e+002'
	print >>fw,'<TRANSP> 5'
	print >>fw,' 0.000000e+000 1.000000e+000 0.000000e+000 0.000000e+000 0.000000e+000'
	print >>fw,' 0.000000e+000 6.000000e-001 4.000000e-001 0.000000e+000 0.000000e+000'
	print >>fw,' 0.000000e+000 0.000000e+000 6.000000e-001 4.000000e-001 0.000000e+000'
	print >>fw,' 0.000000e+000 0.000000e+000 0.000000e+000 7.000000e-001 3.000000e-001'
	print >>fw,' 0.000000e+000 0.000000e+000 0.000000e+000 0.000000e+000 0.000000e+000'
	print >>fw,'<ENDHMM>'
	fw.close()
	
	#语言模型
	#get wdnet词网络
	if not os.path.exists(r'data\lang') : os.mkdir(r'data\lang')
	words=open(r'data\phones\phones','r').read()
	words=words.replace('\n','|')
	words='$WD='+words[:-1]+';\n(SEND-START<$WD>SEND-END)'
	open(r'data\lang\gram','w').write(words)
	#get gram
	cmd=r'HParse data\lang\gram data\lang\wdnet'
	os.system(cmd)
	
def mono_model(monophones,proto,vFloors):	#初始化单因子模型 & 定义hmms
	open('hmms/hmm0/macros','w').write('~o <VECSIZE> 39 <MFCC_0_D_A>\n'+\
	open(vFloors,'r').read())
	
	phones=open(monophones,'r').read().split('\n')[:-1]
	proto_txt=open(proto,'r').read()
	head_idx=proto_txt.find('~o')
	phone_idx=proto_txt.find('~h')
	hmm_idx=proto_txt.find('<BEGINHMM>')
	head_txt=proto_txt[head_idx:phone_idx]
	phone_txt=proto_txt[phone_idx:hmm_idx]
	hmm_txt=proto_txt[hmm_idx:]
	models=[phone_txt.replace('proto',i)+hmm_txt for i in phones]
	models=head_txt+''.join(models)
	open('hmms/hmm0/hmmdefs','w').write(models)
def mapdic(src):
	txt=open('lexicon.txt','r').read().decode('utf-8').split('\n')
	fw=open('map_lexicon.txt','a')
	fw1=open('map.txt','a')
	i=1
	for line in txt:
		txt=line.split(' ')
		word=txt[0]
		phone=' '.join(txt[1:])
		fw.write('word'+str(i)+' '+phone+'\n')
		fw1.write(word.encode('gbk')+' word'+str(i)+'\n')
		i+=1
	fw.close()
	fw1.close()
def add_sp_model(org_model,model):
	model_txt=open(org_model,'r').read()
	begin=model_txt.find(r'~h "sil"')
	end=model_txt.find('<ENDHMM>',begin)
	sil_model=model_txt[begin:end+9].replace('sil','sp')
	open(model,'w').write(model_txt+sil_model)
if __name__=="__main__":
	thchs30 = env.thchs30
	tools = env.tools
	print "============================================================================"
	print "                Data & Lexicon & Language Preparation                       "
	print "============================================================================"
	#prepare_phones('data/phones')
	
	#mapdic('lexicon.txt')
	#prepare_data(thchs30,tools)
	
	print '==============================================='
	print '             MFCC Feature Extration            '
	print '==============================================='
	for i in ['train','test']:
		cmd='HCopy -T 1 -C data/conf/wav_config -S data/'+i+'/mfcc.scp'
		print cmd
		#os.system(cmd)
	#统计均值和方差
	'''
	
	if not os.path.exists('hmms/hmm0') : os.mkdir('hmms/hmm0 ')
	cmd='HCompV -C data/conf/config -f 0.01 -m -S data/train/train.scp -M hmms/hmm0 data/conf/proto'
	print cmd
	os.system(cmd)
	
	print '==============================================='
	print '         MonoPhone Traning & Decoding          '
	print '==============================================='
	#iter 1
	
	if not os.path.exists('hmms/hmm1') : os.mkdir('hmms/hmm1')
	mono_model('data/phones/phones','hmms/hmm0/proto','hmms/hmm0/vFloors')
	'''
	cmd='HERest -A -D -T 1 -C data/conf/config -I data/train/trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	'-S data/train/train.scp -H hmms/hmm0/macros -H hmms/hmm0/hmmdefs -M hmms/hmm1 data/phones/phones'
	os.system(cmd)
	'''
	#iter 2
	if not os.path.exists('hmms/hmm2') : os.mkdir('hmms/hmm2')
	cmd='HERest -A -D -T 1 -C data/conf/config -I data/train/trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	'-S data/train/train.scp -H hmms/hmm1/macros -H hmms/hmm1/hmmdefs -M hmms/hmm2 data/phones/phones'
	print cmd 
	os.system(cmd)
	
	#iter 3
	if not os.path.exists(r'hmms\hmm3') : os.mkdir(r'hmms\hmm3')
	cmd='HERest -A -D -T 1 -C data/conf/config -I data/train/trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	'-S data/train/train.scp -H hmms/hmm2/macros -H hmms/hmm2/hmmdefs -M hmms/hmm3 data/phones/phones'
	print cmd
	os.system(cmd)
	#iter 4
	if not os.path.exists(r'hmms\hmm4') : os.mkdir(r'hmms\hmm4')
	cmd='HERest -A -D -T 1 -C data/conf/config -I data/train/trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	'-S data/train/train.scp -H hmms/hmm3/macros -H hmms/hmm3/hmmdefs -M hmms/hmm4 data/phones/phones'
	print cmd
	os.system(cmd)
	
	
	
	#绑定sp 绑定到sil 训练
	add_sp_model(r'hmms\hmm4\hmmdefs',r'hmms\hmm4\hmmdefs_sp')
	if not os.path.exists(r'hmms\hmm5') : os.mkdir(r'hmms\hmm5')
	cmd=r'HHEd -A -D -T 1 -H hmms\hmm4\macros -H hmms\hmm4\hmmdefs_sp -M hmms\hmm5 data\conf\sil.hed data\phones\phones1'
	os.system(cmd)
	#iter 1
	if not os.path.exists(r'hmms\hmm6') : os.mkdir(r'hmms\hmm6')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\train\trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm5\macros -H hmms\hmm5\hmmdefs_sp -M hmms\hmm6 data\phones\phones1'
	print cmd
	os.system(cmd)
	
	#iter 2
	if not os.path.exists(r'hmms\hmm7') : os.mkdir(r'hmms\hmm7')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\train\trainphones1.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm6\macros -H hmms\hmm6\hmmdefs_sp -M hmms\hmm7 data\phones\phones1'
	print cmd
	os.system(cmd)
	
	
	
	#解码 ps. 需要lab文件，注意文件中的特殊单词
	cmd='HVite -H hmms/hmm7/macros -H hmms/hmm7/hmmdefs_sp -S data/test/test1.scp -f -l * -i result/recout_mono.mlf '+\
	'-w data/lang/wdnet -p 0.0 -s 5.0 data/dict/lexicon2 data/phones/phones1'
	os.system(cmd)
	#评分 ps.注意试试 testwords只保留文件名，不保留父目录
	
	#cmd=r'HResults -I data/test/testwords.mlf data/phones/phones1 result/recout_mono.mlf'
	'''
	'''
	print '==============================================='
	print '           tri Traning Decoding          '
	print '==============================================='
	#生成三因素列表 三因素句子lab
	cmd=r'HLEd -n data\phones\triphones0 -i data\train\wintri.mlf data\conf\mktri.led data\train\aligned.mlf'
	print cmd
	os.system(cmd)
	
	#绑定共享transA,得到绑定信息mktri.hed,triphones0路径不能为反斜杠
	cmd=r'perl '+tools+r'\maketrihed data\phones\phones1 data/phones/triphones0'
	print cmd
	os.system(cmd)
	if os.path.exists(r'data\conf\mktri.hed') : os.remove(r'data\conf\mktri.hed')
	shutil.move(r'mktri.hed',r'data\conf\mktri.hed')
	
	#编辑绑定三因素模型 ps.mktri.hed中第一行包含triphones的路径 不能为反斜杠
	if not os.path.exists(r'hmms\hmm10') : os.mkdir(r'hmms\hmm10')
	
	cmd=r'HHEd -H hmms\hmm9\macros -H hmms\hmm9\hmmdefs_sp -M hmms\hmm10 data\conf\mktri.hed data\phones\phones1'
	print cmd
	os.system(cmd)
	'''