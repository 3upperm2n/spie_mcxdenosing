#!/usr/bin/env python

import os,sys

p7dir = './1e+07'
p8dir = './1e+08'

p7files = os.listdir(p7dir)
p8files = os.listdir(p8dir)

#print p7files

if len(p7files) <> len(p8files):
    print "file num do not match"
    sys.exit(1)

if set(p7files) <> set(p8files):
    print "file name do not match"
    sys.exit(1)

fileNum=len(p7files)
bigoffset = int(1000000)

for idx, filename in enumerate(p7files):
    fid_offset = idx + 1 + bigoffset # idx starts from 0 + offset
    newname = 'test'+str(fid_offset) + '.mat'

    p7prev= p7dir +  '/' + filename 
    p8prev= p8dir +  '/' + filename 

    p7new_offset = p7dir +  '/' + newname 
    p8new_offset = p8dir +  '/' + newname 

    os.rename(p7prev, p7new_offset)
    os.rename(p8prev, p8new_offset)


#
# deduct the big offset: avoid name conflicts
#
p7files = os.listdir(p7dir)
for idx, filename in enumerate(p7files):
    fid = idx + 1
    outname = 'test'+str(fid) + '.mat'
    print fid, filename, outname 

    p7prev= p7dir +  '/' + filename 
    p8prev= p8dir +  '/' + filename 

    # right order
    p7new= p7dir +  '/' + outname 
    p8new= p8dir +  '/' + outname 

    os.rename(p7prev, p7new)
    os.rename(p8prev, p8new)

    #break
