#! /usr/bin/python
import time
import socket
import getopt
import sys
import subprocess


def usage():
    print "Usage configure_bts_client: [options]"
    print ""
    print "Optoins:"
    print "  -h, --help         Show this help message"
    print "  -s, --speed        Scan speed [default=4]. Value range 0-5"
    print "  -t, --tactic       Tactic when configuring IMSI catcher: [camo=default, quick]"

    sys.exit(0)


def stop_components():
    subprocess.call(['sudo', 'stop', 'openbts'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'stop', 'asterisk'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'stop', 'sipauthserve'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'stop', 'smqueue'], stdout=subprocess.PIPE)

def start_components():
    subprocess.call(['sudo', 'start', 'asterisk'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'start', 'sipauthserve'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'start', 'smqueue'], stdout=subprocess.PIPE)
    subprocess.call(['sudo', 'start', 'openbts'], stdout=subprocess.PIPE)


def start_transceiver():
    subprocess.call(['/OpenBTS/transceiver'])

def run_command(command):
    subprocess.call(['sudo', '/OpenBTS/OpenBTSCLI', '-c', command])

def configure_bts(config):
    for i in configurations:
        start = config.find(i)
        end = config.find('\n', start)
        if start < 0 or end < 0:
            print 'Failure with: ' + i
            continue
        conf_value = config[start+len(i)+1:end]
        if configurations[i] != None:
            run_command(configurations[i] + conf_value)
            #print configurations[i] + conf_value



#read commandline arguments


global speed
global supported_tactics
global configurations

configurations = {'CI': 'config GSM.Identity.CI ', 'MCC': 'config GSM.Identity.MCC ', 'MNC': 'config GSM.Identity.MNC ', 'LAC': 'config GSM.Identity.LAC ', 'CRH': 'config GSM.CellSelection.CELL-RESELECT-HYSTERESIS ', 'CRO': None, 'TO': None, 'PT': None, 'T3212': 'config GSM.Timer.T3212 ', 'BAList': None, 'TXPWR': 'devconfig GSM.CellSelection.MS-TXPWR-MAX-CCH ', 'RXLEV': 'devconfig GSM.CellSelection.RXLEV-ACCESS-MIN ', 'ARFCN': 'config GSM.Radio.C0 '}
supported_tactics = ['camo', 'quick']
speed = '4'
setup_tactic = 'camo'

try:
     opts, args = getopt.getopt(sys.argv[1:], 'hs:t:',['help', 'speed', 'tactic'])
except getopt.GetoptError as err:
    print str(err)
    usage()


# set commandline argumens
for o,a in opts:

    if o in ('-h', '--help'):
        usage()
    elif o in ('-s', '--speed'):
        try:
            s = int(a)
            if s <= 5 and s >= 0:
                speed = a
            else:
                raise Exception
        except Exception:
            usage()
    elif o in ('-t', '--tactic'):
        if a in supported_tactics:
            setup_tactic = a
        else:
            usage()




# connect to scanner

target_host = '129.241.208.237'
target_port = 9998


stop_components()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
scan_input = 'speed='+speed+'\n'+'tactic='+setup_tactic+'\n'
client.send(scan_input)

print "Waiting fo config info"
config_info = client.recv(256)
if config_info == 'Failure':
    print config_info
    stop_components()	

# configure openbts
stop_components()
start_components()
print "Waiting for OpenBTS to start up."
time.sleep(15)
configure_bts(config_info)
stop_components()
start_components()







