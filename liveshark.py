#! /usr/bin/python

import pyshark
import subprocess
import os
import time
import signal
import socket
import sys
import grgsm_scanner_tweak




class dummy():
    def send(self, foo):
        pass
    def close(self):
        pass


def get_system_information_type(pkt):

        try:
            ccch = pkt['gsm_a.ccch']
        except Exception:
            return None

        field_lines = ccch._get_all_field_lines()

        for i in field_lines:
            a= i.find("System Information Type ")
            if a > -1:
                spos = a + len("System Information Type ")
                epos = i.find("\n", spos)
                type = i[spos:epos]
                return type

        return None

def get_approx_scan_time(pkt):
    sniff_time=str(pkt.sniff_time)
    end = sniff_time.find('.')
    return sniff_time[:end]


def get_type1_other_cell_arfcns(pkt):
    field_lines = pkt['gsm_a.ccch']._get_all_field_lines()
    cell_arfcns = []
    for i in field_lines:
        a = i.find("ARFCNs =")
        if a > 0:
            b =i.find(" ", a+len("ARFCNs ="))+1
            c= i[b:]
            current = 0;
            next = c.find(" ", current)
            while next>-1:
                cell_arfcns.append(int(c[current:next]))
                current = next+1
                next = c.find(" ", current)
            else:
                next = c.find("\n", current)
                cell_arfcns.append(int(c[current:next]))

            return cell_arfcns
    return cell_arfcns

def get_BA_list(pkt):
    field_lines = pkt['gsm_a.ccch']._get_all_field_lines()
    for i in field_lines:
        a = i.find("ARFCNs =")
        if a > 0:
            full = i
            b =i.find(" ", a+len("ARFCNs ="))+1
            c= i[b:]

            BA_list = []
            current = 0;
            next = c.find(" ", current)
            while next>-1:
                BA_list.append(int(c[current:next]))
                current = next+1
                next = c.find(" ", current)
            else:
                next = c.find("\n", current)
                BA_list.append(int(c[current:next]))

            return BA_list
    return []

def get_type3_info(pkt):
    info = {'CI': None, 'MCC': None, 'MNC': None, 'LAC': None, 'CRH': None, 'CRO': None, 'TO': None, 'PT': None, 'T3212':None}
    ccch = pkt['gsm_a.ccch']._get_all_field_lines()

    for i in ccch:
        f = i.find('(LAI) - ')
        if f>-1:
            end = i.find('\n')
            lai= i[f+len('(LAI) - '):end]
            slash1 = lai.find('/')
            slash2 = lai.find('/', slash1+1)
            info['MCC'] = lai[:slash1]
            info['MNC'] = lai[slash1+1:slash2]
            info['LAC'] = lai[slash2+1:]
            continue
        f = i.find('Cell CI')
        if f>-1:
            s=i.find('(')+1
            end = i.find(')')
            info['CI'] = int(i[s:end])
            continue
        f = i.find('Hysteresis')
        if f>-1:
            end = i.find('\n')
            info['CRH'] = int(i[f+12:end])
            continue
        f = i.find('Reselect Offset')
        if f>-1:
            end = i.find('dB')-1
            info['CRO'] = int(i[f+17:end])
            continue
        f = i.find('Temporary Offset')
        if f>-1:
            end = i.find('dB')-1
            info['TO'] = int(i[31:end])
            continue
        f = i.find('Penalty')
        if f>-1:
            end = i.find(' s ')
            info['PT'] = int(i[27:end])
            continue
        f = i.find('T3212')
        if f>-1:
            end = i.find('\n')
            info['T3212'] = int(i[f+6:end].replace(" ", ""))
            continue


    return info

def get_type4_info(pkt):
    info = {'RXLEV':None, 'TXPWR':None, 'PT':None}

    ccch = pkt['gsm_a.ccch']._get_all_field_lines()
    for i in ccch:
        f = i.find("RXLEV")
        if f>=0:
            end = i.find('dBm')-1
            info['RXLEV'] = int(i[f+19:end].replace(" ", ""))
            continue
        f = i.find("TXPWR")
        if f>=0:
            end = i.find('\n')
            info['TXPWR'] = int(i[f+14:end].replace(" ", ""))
            continue
        f = i.find('Penalty')
        if f>-1:
            end = i.find(' s ')
            info['PT'] = int(i[27:end])
            continue
    return info

def scan_frequency2(arfcn, bts_client=dummy(), scan_speed=5):
    print "Scanning ARFCN: " + str(arfcn)
    start = time.time()
    info_pkts = {}
    try:
        gsm_frequency = str((935+0.2*arfcn)*1000000)
        p = subprocess.Popen(['sudo','./grgsm_livemon_tweak', '-f', gsm_frequency], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        cap = pyshark.LiveCapture(interface='lo')
        cap.sniff(timeout=12.0+(5-scan_speed), packet_count=180+((5-scan_speed)*10))
        os.kill(p.pid, signal.SIGTERM)
        for i in range(len(cap)):
            pkt = cap[i]
            type = get_system_information_type(pkt)
            if type == None:
                continue
            elif type == '1':
                info_pkts['1'] = pkt
            elif type == '2':
                info_pkts['2'] = pkt
            elif type == '3':
                info_pkts['3'] = pkt
            elif type == '4':
                info_pkts['4'] = pkt
            if len(info_pkts) == 4:
                break
        if len(info_pkts) != 4:
            info_pkts = {}

    except KeyboardInterrupt:
        print "Interrupted by user, shuting down"
        os.kill(p.pid, signal.SIGTERM)
        bts_client.send("Failure")
        bts_client.close()
        if __name__ == '__main__':
            sys.exit(1)
        else:
            info_pkts = {}

    except Exception, msg:
        print "Failure during scanning of identified frequency"
        print msg
        os.kill(p.pid, signal.SIGTERM)
        bts_client.send("Failure")
        bts_client.close()
        if __name__ == '__main__':
            sys.exit(1)
        else:
            info_pkts = {}

    end = time.time()
    #print "Single scan time elapsed: " + str(end-start)

    return info_pkts

def scan_frequency(arfcn, bts_client=dummy()):
    print "Scanning ARFCN: " + str(arfcn)
    start = time.time()
    info_pkts = {}
    try:
        gsm_frequency = str((935+0.2*arfcn)*1000000)
        p = subprocess.Popen(['sudo','./grgsm_livemon_tweak', '-f', gsm_frequency], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        cap = pyshark.LiveCapture(interface='lo')
        for pkt in cap.sniff_continuously(packet_count=120):

            type = get_system_information_type(pkt)
            if type == None:
                continue
            elif type == '1':
                info_pkts['1'] = pkt
            elif type == '2':
                info_pkts['2'] = pkt
            elif type == '3':
                info_pkts['3'] = pkt
            elif type == '4':
                info_pkts['4'] = pkt
            if len(info_pkts) == 4:
                break
        os.kill(p.pid, signal.SIGTERM)
        if len(info_pkts) != 4:
            info_pkts = {}

    except KeyboardInterrupt:
        print "Interrupted by user, shuting down"
        os.kill(p.pid, signal.SIGTERM)
        bts_client.send("Failure")
        bts_client.close()
        if __name__ == '__main__':
            sys.exit(1)
        else:
            info_pkts = {}

    except Exception, msg:
        print "Failure during scanning of identified frequency"
        print msg
        os.kill(p.pid, signal.SIGTERM)
        bts_client.send("Failure")
        bts_client.close()
        if __name__ == '__main__':
            sys.exit(1)
        else:
            info_pkts = {}

    end = time.time()
    print "Single scan time elapsed: " + str(end-start)

    return info_pkts

def receive_connection():
    bind_ip = "0.0.0.0"
    bind_port = 9999
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip,bind_port))
    server.listen(1)
    print "Liveshark is waiting for connection."
    client, addr = server.accept()
    return client

def get_scan_arguments(message):
    output = {}
    arguments = ['speed', 'tactic']
    for a in arguments:
        s = message.find(a)
        e = message.find('\n',s)
        output[a] = message[s+len(a)+1:e]

    if len(output) == len(arguments):
        return output
    else:
        print 'Failed to get scan arguments'
        bts_client.send("Failure")
        bts_client.close()
        sys.exit(0)

def scan_for_active_frequencies(speed, bts_client):
    arfcns = []
    try:
        scan_speed = "--speed="+speed
        f = subprocess.Popen(['sudo', './grgsm_scanner', scan_speed ], stdout=subprocess.PIPE)
        #f = subprocess.Popen(['sudo', './grgsm_scanner', '--gain=150',scan_speed ], stdout=subprocess.PIPE)
        sub = 'ARFCN:'
        while True:
            line = f.stdout.readline()
            if line !='':
                print line.rstrip()
                if line.find(sub) >= 0:
                    e = line.find(',')
                    arfcn = line[len(sub)+2:e].replace(' ','')
                    arfcns.append(arfcn)
            else:
                break
    except KeyboardInterrupt:
        print "Interrupted by user, shuting down."
        bts_client.send('Failure')
        bts_client.close()
        sys.exit(1)

    except Exception, msg:
        print "Exception while scaning for frequencies."
        print "Exception message:"
        print msg
        bts_client.send('Failure')
        bts_client.close()
        sys.exit(1)

    return arfcns

def configure_camo(bts_info):
    pass

def create_configuration(bts_info_power):
    foo = [[x, bts_info_power[x][1] ] for x in bts_info_power]
    print foo


    configstring = ''
    max = [-float('inf'),-float('inf')]
    detectable_arfcns = [x for x in bts_info_power]

    for arfcn in bts_info_power:
        if bts_info_power[arfcn][1] > max[1]:
            max = [arfcn, bts_info_power[arfcn][1]]

    max_arfcn = max[0]




    BA_list = get_BA_list(bts_info_power[max_arfcn][0]['2'])
    print 'max arfcn: '+ str(max_arfcn)
    print 'Max ' + str(BA_list)


    chosen_arfcn = None
    for arfcn in BA_list:
        if not arfcn in detectable_arfcns:
            chosen_arfcn = arfcn
            print 'Chosen ARFCN:'+ str(chosen_arfcn)
            break

    if chosen_arfcn == None:
        bts_client.send('Failure, no suitable ARFCN.')
        bts_client.close()
        sys.exit(0)

    type3_info = get_type3_info(bts_info_power[max_arfcn][0]['3'])
    type4_info = get_type4_info(bts_info_power[max_arfcn][0]['4'])

    all_cell_identities = []
    for arfcn in bts_info_power:
        all_cell_identities.append(get_type3_info(bts_info_power[arfcn][0]['3'])['CI'])

    chosen_cell_identity = (type3_info['CI']+100) % 65535
    while True:
        if chosen_cell_identity not in all_cell_identities:
            break
        chosen_cell_identity +1 % 65535


    configstring += 'BAList '
    for n in BA_list:
        configstring += str(n) + ' '
    configstring += '\n'


    for i in type3_info:
        if i =='LAC':
            configstring += str(i) + ' ' + str(int(type3_info[i])-1) + '\n'
            continue
        elif i == 'CI':
            configstring += str(i) + ' ' + str(chosen_cell_identity) + '\n'
            continue
        elif i == 'T3212':
            configstring += str(i) + ' ' + str(6) + '\n'
            continue
        elif i == 'CRH':
            configstring += str(i) + ' ' + str(7) + '\n'
            continue
        elif i == 'MNC':
            mnc = str(type3_info[i])
            if len(mnc) == 1:
                mnc = '0'+mnc
            configstring += i + ' '+ mnc + '\n'
            continue

        configstring += i + ' ' + str(type3_info[i]) + '\n'


    cell_arfcn_list = [chosen_arfcn]    #cell with only one ARFCN. Any better ideas?
    configstring += 'CellOtherARFCNs '
    for n in cell_arfcn_list:
        configstring += str(n) + ' '
    configstring += '\n'

    for i in type4_info:
        configstring += i + ' ' + str(type4_info[i]) + '\n'


    configstring += "ARFCN "+ str(chosen_arfcn) + '\n'

    return configstring





if __name__ == '__main__':

    #init = subprocess.call(['./setup'])
    #if init != 0:
     #   print "Failed to initialize"
      #  sys.exit

    # Wait for connection
    bts_client = receive_connection()
    message = bts_client.recv(256)
    arguments = get_scan_arguments(message)
    print arguments

    scan_start = time.time()

    # Scan for gsm frequencies
    print "Liveshark has accepted connection, starting scan."
    arfcns_power = grgsm_scanner_tweak.full_frequency_scan(int(arguments['speed']))

    if len(arfcns_power):
        print "Nearby ARFCN(s) identified:"
        print [x[0] for x in arfcns_power]

    else:
        print "No nearby GSM signals identified"
        bts_client.send('Failure, no nearby GSM signals identified.')
        bts_client.close()
        sys.exit(0)


    # Scan the identified frequencies
    bts_info_power = {}
    print "Scanning the identified frequencies"
    for arfcn in arfcns_power:
        info_pkts = scan_frequency2(arfcn[0], bts_client)
        if len(info_pkts) == 4:
            bts_info_power[arfcn[0]] = [info_pkts, arfcn[1]]
        else:
            print "Could not capture info about ARFCN: "+ str(arfcn[0])

    config = create_configuration(bts_info_power)

    #FNULL = open(os.devnull, 'w')
    bts_client.send(config)
    bts_client.close()

    scan_end = time.time()
    print "Full scan took: " + str(scan_end - scan_start) + " seconds."
    sys.exit(0)
