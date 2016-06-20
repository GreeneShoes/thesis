#! /usr/bin/python
import subprocess
from grgsm_scanner_tweak import full_frequency_scan
import time
import liveshark
import sys


def pkt_search(pkt):

    try:
        ch = pkt['gsm_a.ccch']
    except Exception:
        return
    lines = ch._get_all_field_lines()
    for l in lines:
        i = l.find('penalty')
        if i >=0:
            print l


while True:
    try:
        arfcn = input("Give ARFCN to scan ")
        arfcn = int(arfcn)
        if arfcn > 124 or arfcn < 0:
            continue
    except Exception:
        continue

    break



info_pkts = liveshark.scan_frequency2(arfcn, scan_speed=1)

if not len(info_pkts):
    print "Failed to capture packets"
    sys.exit(1)

cell_other_arfcns = liveshark.get_type1_other_cell_arfcns(info_pkts['1'])
BA_list = liveshark.get_BA_list(info_pkts['2'])
type3_info = liveshark.get_type3_info(info_pkts['3'])
type4_info = liveshark.get_type4_info(info_pkts['4'])





print "Fake base tower info"

print cell_other_arfcns
print '\n'
print BA_list
print '\n'
print type3_info
print '\n'
print type4_info

#print pkt_search(info_pkts['4'])
#print pkt_search(info_pkts['3'])






print 'finished'