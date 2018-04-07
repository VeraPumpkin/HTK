# -*- coding: utf-8 -*-
import os
import re
import shutil
import env

tools='..\..\..'+r'\samples\HTKTutorial'

def get_suffix(path,suffix): 
    txtfilenames=[] 
    for dirpath,dirnames,filenames in os.walk(path): 
        filenames=filter(lambda filename:filename[-4:]==suffix,filenames) 
        filenames=map(lambda filename:os.path.join(dirpath,filename),filenames) 
        txtfilenames.extend(filenames)
        
    return txtfilenames

def remove_sign(s,sign):#\d,.!? \\~\/:;@$%=+"
    return re.sub(r'(['+sign+'])','',s)

def preare_data(data_src):
	#建立目录
	'''
	dir=['data','hmms','result']
	data_dir=['train','test','conf','phones','dict']
	for i in dir:
		if os.path.exists(i):shutil.rmtree(i)
		os.mkdir(i)
	[os.makedirs('data\\'+i) for i in data_dir]
	#生成prompts
	for i in ['train','test']:
		fw=open('data\\'+i+'\\'+i+'prompts',"w")
		path_list=get_suffix(data_src+'\\'+i,'.txt')
		lab=''
		for path in path_list:
			fr=open(path,'r')
			lab+=remove_sign(fr.read().upper().replace('-- ',''),\
			'\d,.!?\\~\/:;@$%=+')
			fr.close()
		lab_list=lab.split('\n')
		if i=='test':
			test_str='\n'.join(path_list)
			test_list=test_str.split('\\')
			t=(len(test_list)-1)/len(path_list)
			idx=t*range(1,len(test_list)-1)
			#print idx
			test_list=[test_list[i] for i in range(t,len(test_list),t)]
			root=data_src.split('\\')[0]
			test_str='\n'.join(test_list).replace('\n'+root,'').replace('.txt','')
			path_list=test_str.split('\n')
		pmt_list=map(list,zip(path_list,lab_list))
		pmt_list=[''.join(i) for i in pmt_list]
		prompts='\n'.join(pmt_list).replace('.txt','')
		print >> fw ,prompts
		fw.close()
	#生成单词列表
	cmd='perl '+env.tools+r'\prompts2wlist'+ \
	r' data\train\trainprompts data\dict\wlist'
	print cmd
	os.system(cmd)
	#生成字典
	dic=data_src+r'\doc\timitdic1.txt'
	fr = open(dic, "r")
	fw = open(r'data\dict\timitdic',"w")
	wrd_list=''
	for line in fr:
		line=line.split('/')
		#print line
		wrd_list+=line[0].upper()+remove_sign(line[1],'\d')+' sp'+line[2]
	fw.write(wrd_list)
	fw.close()
	fr.close()
	

	
	#生成 words prompts
	cmd='perl '+env.tools+r'\prompts2mlf data\train\trainwords.mlf'+r' data\train\trainprompts'
	print cmd
	os.system(cmd)
	#生成 tets words prompts 用于测试
	cmd='perl '+env.tools+r'\prompts2mlf data\test\testwords.mlf'+r' data\test\testprompts'
	print cmd
	os.system(cmd)
	#生成phones list 
	#手动补充timitdic缺省的单词
	
	cmd=r'HDMan -m -w data\dict\wlist -n data\phones\monophones0 -l '+\
	r'dlog data\dict\dict data\dict\timitdic'
	print cmd
	os.system(cmd)
	'''
	#配置 替换words->phones 每个句子插入sil  删除sp
	fw=open(r'data\conf\mkphones.led','w')
	print >>fw,'EX\nIS sil sil\nDE sp'
	fw.close()
	#生成train lab
	lab_list=get_suffix(data_src+r'\train','.wrd')
	for line in lab_list:
		lab=open(line,'r').read()
		print lab
		lab1=remove_sign(lab,',.!?\\~\/:;@$%=+"').upper()
		open(line.replace('.wrd','.lab'),'w').write(lab1[2:].replace('--\n','').replace('\'EM','EM').replace('\n\n','\n').replace('"',''))
		
		#可能处理一些特殊单词如 'EM
	#配置 绑定sil 和 sp 共享 tansA
	fw=open(r'data\conf\sil.hed','w')
	print >>fw,'AT 2 4 0.2 {sil.transP}'
	print >>fw,'AT 4 2 0.2 {sil.transP}'
	print >>fw,'AT 1 3 0.3 {sp.transP}'
	print >>fw,'TI silst  {sil.state[3],sp.state[2]}'
	fw.close()
	#绑定三因素
	fw=open('data\conf\mktri.led','w')
	print >>fw,'WB sp'
	print >>fw,'WB sil'
	print >>fw,'TC'
	fw.close()
	#增加因素sil & 删除 sp
	txt=open('data\phones\monophones1','w').write(open(r'data\phones\monophones0','r').read()+'sil')
	txt=open('data\phones\monophones2','w').write(open(r'data\phones\monophones1','r').read().replace('sp\n',''))
	#生成 phones prompts 
	#补充dict缺省的单词
	#替换trainwords
	#open('data/dict/dict1','w').write(open('data/dict/dict','r').read().replace('\n',' sp\n'))
	cmd=r'HLEd -l * -d data\dict\dict2 -i data\phones\trainphones.mlf '\
	r'data\conf\mkphones.led data\train\trainwords.mlf'
	print cmd
	os.system(cmd)
	#mfcc 配置
	fw=open(r'data\conf\wav_config','w')
	print >>fw,'SOURCEFORMAT=NIST'
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
		fw1=open('data\\'+i+'\\'+'code'+i+'.scp',"w")
		fw2=open('data\\'+i+'\\'+i+'.scp',"w")
		wav_list=get_suffix(data_src+'\\'+i,'.wav')
		wav_str='\n'.join(wav_list)
		mfcc_path=wav_str.replace('.wav','.mfc')
		
		mp=map(list,zip(wav_str.split('\n'),mfcc_path.split('\n')))
		pmt_list=[' '.join(i) for i in mp]
		wav_mfcc='\n'.join(pmt_list)
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
	words=open(r'data\dict\wlist','r').read()
	words=words.replace('\n','|')
	words='$WD='+words[:-1]+';\n(SEND-START<$WD>SEND-END)'
	open(r'data\lang\gram','w').write(words)
	#get gram
	cmd=r'HParse data\lang\gram data\lang\wdnet'
	os.system(cmd)
	
def mono_model(monophones,proto,vFloors):	#初始化单因子模型 & 定义hmms
	open(r'hmms\hmm0\macros','w').write('~o <VECSIZE> 39 <MFCC_0_D_A>\n'+\
	open(vFloors,'r').read())
	
	phones=open(monophones,'r').read().split('\n')
	proto_txt=open(proto,'r').read()
	head_idx=proto_txt.find('~o')
	phone_idx=proto_txt.find('~h')
	hmm_idx=proto_txt.find('<BEGINHMM>')
	head_txt=proto_txt[head_idx:phone_idx]
	phone_txt=proto_txt[phone_idx:hmm_idx]
	hmm_txt=proto_txt[hmm_idx:]
	models=[phone_txt.replace('proto',i)+hmm_txt for i in phones]
	models=head_txt+''.join(models)
	open('hmms\hmm0\hmmdefs','w').write(models)
	
def add_sp_model(org_model,model):
	model_txt=open(org_model,'r').read()
	begin=model_txt.find(r'~h "sil"')
	end=model_txt.find('<ENDHMM>',begin)
	sil_model=model_txt[begin:end+9].replace('sil','sp')
	open(model,'w').write(model_txt+sil_model)
if __name__ == "__main__":
	
	
	'''
	print '==============================================='
	print '     Data & Lexicon & language Preparetion     '
	print '==============================================='
	timit=r'G:\TIMIT\TIMIT'
	preare_data(timit)
	
	print '==============================================='
	print '             MFCC Feature Extration            '
	print '==============================================='
	cmd=r'HCopy -T 1 -C data\conf\wav_config -S data\train\codetrain.scp'
	print cmd
	#os.system(cmd)
	#统计均值和方差
	
	if not os.path.exists(r'hmms\hmm0') : os.makedirs(r'hmms\hmm0 ')
	#cmd=r'HCompV -C data\conf\config -f 0.01 -m -S data\train\train.scp -M hmms\hmm0 data\conf\proto'
	print cmd
	#os.system(cmd)
	
	print '==============================================='
	print '         MonoPhone Traning & Decoding          '
	print '==============================================='
	
	#iter 1
	if not os.path.exists(r'hmms\hmm1') : os.makedirs(r'hmms\hmm1')
	mono_model(r'data\phones\monophones2',r'hmms\hmm0\proto',r'hmms\hmm0\vFloors')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm0\macros -H hmms\hmm0\hmmdefs -M hmms\hmm1 data\phones\monophones2'
	print cmd
	os.system(cmd)
	
	#iter 2
	if not os.path.exists(r'hmms\hmm2') : os.makedirs(r'hmms\hmm2')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm1\macros -H hmms\hmm1\hmmdefs -M hmms\hmm2 data\phones\monophones2'
	print cmd
	os.system(cmd)
	
	#iter 3
	if not os.path.exists(r'hmms\hmm3') : os.makedirs(r'hmms\hmm3')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm2\macros -H hmms\hmm2\hmmdefs -M hmms\hmm3 data\phones\monophones2'
	print cmd
	os.system(cmd)
	
	#iter 4
	if not os.path.exists(r'hmms\hmm4') : os.makedirs(r'hmms\hmm4')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm3\macros -H hmms\hmm3\hmmdefs -M hmms\hmm4 data\phones\monophones2'
	print cmd
	os.system(cmd)
	
	#绑定sp 绑定到sil 训练
	add_sp_model(r'hmms\hmm4\hmmdefs',r'hmms\hmm4\hmmdefs_sp')
	if not os.path.exists(r'hmms\hmm5') : os.mkdir(r'hmms\hmm5')
	cmd=r'HHEd -A -D -T 1 -H hmms\hmm4\macros -H hmms\hmm4\hmmdefs_sp -M hmms\hmm5 data\conf\sil.hed data\phones\monophones1'
	os.system(cmd)
	
	#iter 1
	if not os.path.exists(r'hmms\hmm6') : os.makedirs(r'hmms\hmm6')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm5\macros -H hmms\hmm5\hmmdefs_sp -M hmms\hmm6 data\phones\monophones1'
	print cmd
	os.system(cmd)
	
	#iter 2
	if not os.path.exists(r'hmms\hmm7') : os.makedirs(r'hmms\hmm7')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\phones\trainphones.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm6\macros -H hmms\hmm6\hmmdefs_sp -M hmms\hmm7 data\phones\monophones1'
	print cmd
	os.system(cmd)
	
	
	#对齐消除多音 得到新 phone_prompts
	
	open('data/dict/dict4','w').write(open('data/dict/dict3','r').read().replace('\n',' sp\n'))
	cmd='HVite -A -D -T 1 -l * -o SWT -b SILEN -C data/conf/config -a -H hmms/hmm7/macros -H hmms/hmm7/hmmdefs_sp '+\
	'-i aligned.mlf -m -t 250.0 -y lab -I data/train/trainwords.mlf -S data/train/train.scp data/dict/dict2 data/phones/monophones1'
	os.system(cmd)
	
	
	
	train_scp=open('data/train/train.scp','r').read()
	list=train_scp.split('\n')
	search=open('aligned.mlf','r').read()
	count=0
	fw=open('data/train/train1.scp','a')
	for i in list:
		key=i.split('\\')[-1][:-4]
		print key
		yn=search.find(key)
		if yn==-1:
			count+=1
		else:
			fw.write(i+'\n')
	fw.close()
	print count
	
	#iter 1
	if not os.path.exists(r'hmms\hmm8') : os.makedirs(r'hmms\hmm8')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I aligned.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train1.scp -H hmms\hmm7\macros -H hmms\hmm7\hmmdefs_sp -M hmms\hmm8 data\phones\monophones1'
	print cmd
	os.system(cmd)
	
	#iter 2
	if not os.path.exists(r'hmms\hmm9') : os.makedirs(r'hmms\hmm9')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I aligned.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train1.scp -H hmms\hmm8\macros -H hmms\hmm8\hmmdefs_sp -M hmms\hmm9 data\phones\monophones1'
	print cmd
	os.system(cmd)
	
	#open('data/dict/dict3','w').write('SEND-START sil\nSEND-END sil\n'+open('data/dict/dict2','r').read()[:-1])
	# list=open('data/test/test.scp','r').read()
	# list=list.split('\n')
	# list='\n'.join(list[:20])
	# open('data/test/test1.scp','w').write(list)
	
	
	
	#解码 ps. 需要lab文件，注意文件中的特殊单词
	
	
	
	open('data/dict/dict5','w').write(open('data/dict/dict4','r').read().replace(' sp',''))
	'''
	if os.path.exists('result/recout_mono.mlf') : os.remove('result/recout_mono.mlf')
	
	cmd='HVite -H hmms/hmm9/macros -H hmms/hmm9/hmmdefs_sp -S data/test/test1.scp -f -l * -i result/recout_mono.mlf '+\
	'-w data/lang/wdnet -p 0.0 -s 5.0 data/dict/dict4 data/phones/monophones1'
	os.system(cmd)
	#评分 ps.注意试试 testwords只保留文件名，不保留父目录
	'''
	cmd='HResults -I data/test/testwords.mlf data/phones/monophones1 result/recout_mono.mlf'

	
	print '==============================================='
	print '           tri Traning Decoding          '
	print '==============================================='
	#生成三因素列表 三因素句子lab
	cmd=r'HLEd -n data\phones\triphones0 -i data\train\wintri.mlf data\conf\mktri.led data\train\trainphones.mlf.mlf'
	os.system(cmd)
	
	#绑定共享transA,得到绑定信息mktri.hed,triphones0路径不能为反斜杠
	cmd=r'perl '+env.tools+r'\maketrihed data\phones\monophones1 data/phones/triphones0'
	print cmd
	os.system(cmd)
	if os.path.exists(r'data\conf\mktri.hed') : os.remove(r'data\conf\mktri.hed')
	shutil.move(r'mktri.hed',r'data\conf\mktri.hed')
	
	#编辑绑定三因素模型 ps.mktri.hed中第一行包含triphones的路径 不能为反斜杠
	if not os.path.exists(r'hmms\hmm10') : os.mkdir(r'hmms\hmm10')
	
	cmd=r'HHEd -H hmms\hmm9\macros -H hmms\hmm9\hmmdefs_sp -M hmms\hmm10 data\conf\mktri.hed data\phones\monophones1'
	print cmd
	os.system(cmd)
	
	#训练三因素 ps.注意-s stats
	if not os.path.exists(r'hmms\hmm11') : os.mkdir(r'hmms\hmm11')
	cmd=r'HERest -A -D -T 1 -C data\conf\config -I data\train\wintri.mlf -t 250.0 150.0 1000.0 '+\
	r'-S data\train\train.scp -H hmms\hmm10\macros -H hmms\hmm10\hmmdefs_sp -M hmms\hmm11 data/phones/triphones0'
	
	#cmd='HERest -B -C data/conf/config -I data/train/wintri.mlf -t 250.0 150.0 1000.0 -s stats -S data/train/train.scp -H hmms/hmm10/macros -H hmms/hmm10/hmmdefs_sp -M hmms/hmm11 data/phones/triphones0'
	os.system(cmd)
	'''