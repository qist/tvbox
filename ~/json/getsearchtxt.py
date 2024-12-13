#!/usr/bin/env python3

import sys
import re
import json
import requests
import time
import traceback
import gzip

p=re.compile(r'.*/s/(.*)')
skipp = re.compile(r'.*(cover|screen|频道).*',re.IGNORECASE)
reqcount=1
sharedict=set()

def getlist(w,shareid, fileid,morepage):
    global p
    global skipp
    global reqcount
    global sharedict

    reqcount += 1
    if reqcount % 5 == 0:
        print(f"reqcount:{reqcount} shareid:{shareid} fileid:{fileid}",file=sys.stderr)
        #time.sleep(1)
    url = f'http://192.168.101.188:9978/proxy?do=pikpak&type=list&share_id={shareid}&file_id={fileid}&pass_code=&morepage={morepage}'
    print(f"url: {url}",file=sys.stderr)
    resp = requests.get(url)
    content = resp.content.decode('utf-8')
    lines = content.split("\n")
    if "folder" not in content and len(lines)<=4:
        return
    isfirst=True
    for line in lines:
        if isfirst:
            isfirst=False
            print(f"first line:{line}",file=sys.stderr)
        if skipp.match(line):
            continue
        linearr = line.split('\t')
        if len(linearr)>2:
            m = p.match(linearr[0])
            if m:
                arr = m.group(1).split("/")
            else:
                arr = linearr[0].split("/")
            shareid=arr[0]
            fileid=arr[1] if len(arr)>1 else ""
            if shareid+"/"+fileid in sharedict:
                print(f"skip shareid{shareid} fileid:{fileid}", file=sys.stderr)
                continue
            w.write(line+"\n")
            w.flush()
            if linearr[2] == "folder":
                getlist(w,shareid,fileid,False)

    if len(lines)>0:
        getlist(w,shareid,fileid,True)

def main():
    try:
        f = gzip.open(sys.argv[1]+".raw.gz",mode="rt",encoding="utf-8")
        if f is not None:
            print(f"found gz raw file:{sys.argv[1]}.raw.gz, extract it",file=sys.stderr)
            with(open(sys.argv[1]+".raw","w",encoding="utf-8")) as w:
                while(True):
                    lines = f.readlines()
                    if len(lines)<=0:
                        break
                    for line in lines:
                        line=line.strip()
                        w.write(line+"\n")
            f.seek(0)
    except:
        traceback.print_exc()
        try:
            f = open(sys.argv[1]+".raw","r",encoding="utf-8")
        except:
            f = None
    if f is not None:
        print("found old raw file")
        while True:
            lines = f.readlines()
            if len(lines)<=0:
                break
            for line in lines:
                linearr = line.split("\t")
                m = p.match(linearr[0])
                if m:
                    arr = m.group(1).split("/")
                else:
                    arr = linearr[0].split("/")
                if len(arr)>1:
                    shareid = arr[0]
                    fileid = arr[1]
                    sharedict.add(shareid+"/"+fileid)
        f.close()
        print(f"old raw file record:{len(sharedict)}")
    else:
        print("no old raw file")
    with(open(sys.argv[1]+".raw","a+",encoding="utf-8")) as w:
        with(open(sys.argv[1],"r",encoding="utf-8")) as f:
            j = json.load(f)
            for c in j:
                shareid=c.get("type_id")
                fileid=""
                m = p.match(shareid)
                if m:
                    arr = m.group(1).split("/")
                else:
                    arr = shareid.split("/")
                shareid=arr[0]
                fileid=arr[1] if len(arr)>1 else ""
                if shareid+"/"+fileid in sharedict:
                    continue
                getlist(w,shareid,fileid,False)

main()
