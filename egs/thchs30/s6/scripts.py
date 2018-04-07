# -*- coding: utf-8 -*-
import re
import os

def get_suffix(path,suffix): 
    txtfilenames=[] 
    for dirpath,dirnames,filenames in os.walk(path): 
        filenames=filter(lambda filename:filename[-4:]==suffix,filenames) 
        filenames=map(lambda filename:os.path.join(dirpath,filename),filenames) 
        txtfilenames.extend(filenames)
        
    return txtfilenames

def remove_sign(s,sign):#\d,.!? \\~\/:;@$%=+"
    return re.sub(r'(['+sign+'])','',s)

def utf_to_str(utf):
	return repr(utf).replace('u\'','').replace('\'','').replace('"','').replace(r'\\u','w').replace(r'\u','w')