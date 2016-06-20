#! /usr/bin/python

import subprocess
import time
import sys
import liveshark
from grgsm_scanner_tweak import full_frequency_scan
from ChannelInfo import Channel, Cell
from Infraction import Alarm
from collections import Counter
from Scan import Scan
from gsm_xml import xml_gsm_logg_write, xml_gsm_logg_read
from gps_location import get_gps_location
from math import floor, sqrt





class Scanner:

    def __init__(self):
        self.cells = {}
        self.channels = {}
        for i in range(125):
            self.channels[i] = []
        self.scans = []
        self.country_MCC = None
        self.unused_arfcns = []
        self.location = None

        self.t3212_threshold = 1
        self.cro_threshold = 63
        self.crh_threshold = 7
        self.pt_threshold = 1
        self.power_threshold = -85

        prev_cells, prev_channels = xml_gsm_logg_read()
        for prev_cell in prev_cells:
            if not prev_cell.CI in self.cells:
                self.new_cellID(prev_cell)
            else:
                self.add_cell(prev_cell)
        for prev_channel in prev_channels:
            self.add_channel(prev_channel)


    def finish(self):
        pass

    def startup(self):

        self.set_country_mcc()

        self.set_unused_arfcns()

        self.set_location()

    def add_channel(self, channel):
        self.channels[channel.ARFCN].append(channel)

    def new_cellID(self, cell):
        self.cells[cell.CI] = [cell]

    def add_cell(self, cell):
        self.cells[cell.CI].append(cell)

    def set_country_mcc(self):
        try:
            print('Please enter Mobile Country Code(MCC) if known.')
            mcc = sys.stdin.readline()
            mcc = str(mcc).rstrip()
            if isinstance(mcc, int):
                self.country_MCC = mcc
        except Exception, msg:
            print msg

        if self.is_country_mcc_set():
            print 'Mobile Country Code(MCC) set to '+ str(self.country_MCC)
        else:
            print 'Mobile Country Code(MCC) unknown'

    def set_location(self):
        while True:
            print 'Set location automatic or manual?'
            type = sys.stdin.readline()
            type = type.rstrip().lower()
            if type == 'auto' or type == 'aotomatic' or type == 'automatically' or type == 'a':
                loc = get_gps_location()
                if loc:
                    self.location = loc
                else:
                    print 'Set location manually.'
                    self.set_location_manually()
                break
            elif type == 'manual' or type == 'manually' or type == 'man' or type == 'm':
                self.set_location_manually()
                break

    def set_location_manually(self):
        print 'Enter location'
        loc = sys.stdin.readline()
        loc = str(loc.rstrip())
        self.location = loc

    def is_country_mcc_set(self):
        if self.country_MCC:
            return True
        else:
            return False

    def set_unused_arfcns(self):
        print 'If any, please enter unused ARFCNs(0-124) one by one. Finish by entering nothing.'
        try:
            while True:
                arfcn = input('ARFCN: ')
                arfcn = int(arfcn)
                if arfcn < 0 or arfcn > 124:
                    return
                if not arfcn in self.unused_arfcns:
                    self.unused_arfcns.append(arfcn)
        except Exception:
            pass
        if len(self.unused_arfcns):
            print 'Unused ARFCNs: ' + str(self.unused_arfcns)
        else:
            print 'No ARFCNs are known to be unused'

    def add_scan(self, start, end):
        self.scans.append([end[0] - start[0], 'Beteween '+ start[1] + ' and '+ end[1]])

    def all_cell_identities(self):
        return [x for x in self.cells]

    def all_mncs(self):
        MNCs = []
        for arfcn in self.channels:
            for channel in self.channels[arfcn]:
                if channel.MNC not in MNCs:
                    MNCs.append(channel.MNC)
        return MNCs

    def get_channel_string(self,channel):
        return 'ARFCN: '+ str(channel.ARFCN) +' CI:'+str(channel.CI)+' LAI:'+str(channel.MCC)+'/'+str(channel.MNC)+'/'+str(channel.LAC)+' '

    def scan(self, scan_speed):
        print 'Obtaining active GSM frequencies.'
        identified_arfcns_power = full_frequency_scan(scan_speed)
        identified_powers = {}
        for p in identified_arfcns_power:
            identified_powers[p[0]] = p[1]
        identified_arfcns = [x[0] for x in identified_arfcns_power]
        if len(identified_arfcns) <= 0:
            print 'No active frequencies found'
            return
        identified_arfcns.sort()
        print identified_arfcns
        bts_info = {}
        print 'Scaning single frequencies/ARFCNs.'
        for arfcn in identified_arfcns:
            info_pkts = liveshark.scan_frequency2(arfcn)
            if len(info_pkts) == 4:
                info_pkts['power'] = identified_powers[arfcn]
                bts_info[arfcn] = info_pkts
            else:
                print "Could not capture info about ARFCN: "+ str(arfcn)
        print "End single scans"
        return bts_info

    def check_channel(self, channel, scan_arfcns):

        for stored in self.channels[channel.ARFCN]:
            if channel == stored:
                stored.add_scan(channel.SCANS[0])
                stored.add_local_power(channel.LOCAL_POWERS[0])
                return

        channel_string = self.get_channel_string(channel)
        BAlength = len(channel.BAList)

        if self.is_country_mcc_set():
            if not channel.MCC == self.country_MCC:
                a = Alarm(channel_string + 'MCC:' + str(channel.MCC) + ' does not equal this country\'s MCC:' + self.country_MCC, self.location)
                channel.add_alarm(a)

        if len(self.unused_arfcns):
            if channel.ARFCN in self.unused_arfcns:
                a = Alarm(channel_string + 'Channel\'s ARFCN is known to not be in use' , self.location)
                channel.add_alarm(a)
            if len(channel.BAList):
                illegal_arfcns = []
                for arfcn in channel.BAList:
                    if arfcn in self.unused_arfcns:
                        illegal_arfcns.append(arfcn)
                if len(illegal_arfcns):
                    a = Alarm(channel_string + 'ARFCN(s) in neighbor list are known to not be in use: ' + str(illegal_arfcns), self.location)
                    channel.add_alarm(a)
            if len(channel.CellARFCNS):
                illegal_arfcns = []
                for arfcn in channel.CellARFCNS:
                    if arfcn in self.unused_arfcns:
                        illegal_arfcns.append(arfcn)
                if len(illegal_arfcns):
                    a = Alarm(channel_string + 'ARFCN(s) in cell list are known to not be in use: ' + str(illegal_arfcns), self.location)
                    channel.add_alarm(a)

        BAList_not_present = True
        for arfcn in channel.BAList:
            if arfcn in scan_arfcns:
                BAList_not_present = False
                break
        if BAList_not_present:
            a = Alarm(channel_string+ 'No channel in neighbor list among those found in scan.', self.location)
            channel.add_alarm(a)


        if BAlength==0 :
            a = Alarm(channel_string + 'The neighbor list is empty.', self.location)
            channel.add_alarm(a)
        if BAlength==1 :
            a = Alarm(channel_string + 'Only one ARFCN in neighbor list.', self.location)
            channel.add_alarm(a)
        if channel.ARFCN not in channel.BAList:
            a = Alarm(channel_string + 'Channel\'s ARFCN is not in it\'s own neighbor list.', self.location)
            channel.add_alarm(a)
        if channel.ARFCN not in channel.CellARFCNS:
            a = Alarm(channel_string + 'Channel\'s ARFCN is not in it\'s cell\'s list of ARFCNS.', self.location)
            channel.add_alarm(a)
        if self.t3212_threshold >= channel.T3212 > 0:
            a = Alarm(channel_string + 'Periodic Location Updating Timer(T3212): '+str(channel.T3212 * 6)+' min., is below or equal threshold: '+ str(self.t3212_threshold * 6)+ ' min.', self.location)
            channel.add_alarm(a)
        if channel.CRH >= self.crh_threshold:
            a = Alarm(channel_string + 'Cell Reselect Hysteresis(CRH): '+ str(channel.CRH) + ', is above or equal the threshold: '+ str(self.crh_threshold), self.location)
            channel.add_alarm(a)

        if not channel.CRO == None:
            if channel.CRO >= self.cro_threshold:
                a = Alarm(channel_string + 'Cell Reselect Offset(CRO): '+ str(channel.CRO)+', is above the thrshold: '+ str(self.cro_threshold), self.location)
                channel.add_alarm(a)
        else:
            a = Alarm(channel_string + 'Cell Reselect Offset(CRO), though it is optional, is not set.', self.location)
            channel.add_alarm(a)

        if not channel.PT == None:
            if channel.PT <= self.pt_threshold:
                a = Alarm(channel_string + 'Penalty Time: '+ str(channel.PT)+', is above the thrshold: '+str(self.pt_threshold), self.location)
                channel.add_alarm(a)
        else:
            a = Alarm(channel_string + 'Penalty Time, though it is optional, is not set.', self.location)
            channel.add_alarm(a)


        channel = self.channel_compare_with_stored(channel)

        return channel

    def check_cell(self, cell):
        cell_alarm = []
        if cell.CI in self.cells:
            if cell in self.cells[cell.CI]:
                return cell_alarm
            for stored in self.cells[cell.CI]:
                if stored.bogus_arfcns(cell):
                    alarm = Alarm("Cell: CI:"+str(cell.CI)+' LAI:'+str(cell.MCC)+'/'+str(cell.MNC)+'/'+str(cell.LAC) +' has been observed with differing ARFCN list:  ' + str(cell.ARFCNS) + '  ' +str(stored.ARFCNS), self.location)
                    stored.add_alarm(alarm)
                    cell_alarm.append(alarm)
                    return cell_alarm
            self.add_cell(cell)
        else:
            self.new_cellID(cell)
        return cell_alarm

    def channel_compare_with_stored(self, channel):
        channel_string = self.get_channel_string(channel)

        for arfcn in self.channels:
            for i in self.channels[arfcn]:
                if channel.CI == i.CI:
                    if not compare_list(channel.CellARFCNS, i.CellARFCNS):
                        a = Alarm("Two channels with same CI do not have the same list of other ARFCNs in cell\n"+channel.print_without_alarms()+'\n'+i.print_without_alarms(), self.location)
                        channel.add_alarm(a)
                        i.add_alarm(a)

        for stored in self.channels[channel.ARFCN]:
            if channel.minor_equality(stored):
                if not channel == stored:
                    a = Alarm(channel_string + "Information has changed on separate scans of same frequency:\n " + channel.print_without_alarms()+'\n'+stored.print_without_alarms(), self.location)
                    channel.add_alarm(a)
                    stored.add_alarm(a)

        return channel

    def operator_check(self, new_channels):
        new_alarms = []

        for new_channel in new_channels:
            channel_overlap = []
            for other_arfcn in self.channels:
                for other_channel in self.channels[other_arfcn]:
                    if not new_channel.MNC == other_channel.MNC:
                        overlap = []
                        for arfcn in new_channel.BAList:
                            if arfcn in other_channel.BAList:
                                overlap.append(arfcn)
                        if len(overlap):
                            new_channel_string = self.get_channel_string(new_channel)
                            other_channel_string = self.get_channel_string(other_channel)
                            a = Alarm(new_channel_string + '<-This channel\'s neighborlist overlaps with that of a channel from another operator: '+ other_channel_string, self.location)
                            new_channel.add_alarm(a)
                            other_channel.add_alarm(a)

        return new_channels

    def power_check(self, scan_arfcns):
        new_alarms = []
        for arfcn in self.channels:
            for stored in self.channels[arfcn]:
                max = stored.get_max_local_power()
                if max > self.power_threshold:
                    if not arfcn in scan_arfcns:
                        channel_string = self.get_channel_string(stored)
                        a = Alarm(channel_string + ' Channel with previously strong signal strength has disappeared.', self.location )
                        stored.add_alarm(a)
                        new_alarms.append(a)

        return new_alarms

    def MNC_check(self):
        #At the end of
        pass

    def check_info(self, bts_info):
        new_channels = []
        cell_alarms = []
        other_alarms = []
        scan_arfcns = [x for x in bts_info]


        for arfcn in bts_info:
            scan_time = liveshark.get_approx_scan_time(bts_info[arfcn]['1'])
            Cell_ARFCNS = liveshark.get_type1_other_cell_arfcns(bts_info[arfcn]['1'])
            BA_List = liveshark.get_BA_list(bts_info[arfcn]['2'])
            type3_info = liveshark.get_type3_info(bts_info[arfcn]['3'])
            type4_info = liveshark.get_type4_info(bts_info[arfcn]['4'])
            cell = Cell(type3_info['CI'], type3_info['MCC'], type3_info['MNC'], type3_info['LAC'], Cell_ARFCNS)
            cell_alarms += self.check_cell(cell)
            channel = Channel(arfcn,
                              type3_info['MCC'],
                              type3_info['MNC'],
                              type3_info['LAC'],
                              type3_info['CI'],
                              type3_info['CRH'],
                              type3_info['CRO'],
                              type3_info['TO'],
                              type3_info['PT'],
                              type3_info['T3212'],
                              type4_info['RXLEV'],
                              type4_info['TXPWR'],
                              BA_List,
                              Cell_ARFCNS,
                              scans=[Scan(scan_time, self.location, bts_info[arfcn]['power'])],
                              alarms=[])
            channel.add_local_power(bts_info[arfcn]['power'])
            n_c = self.check_channel(channel, scan_arfcns)
            if isinstance(n_c, Channel):
                new_channels.append(n_c)

        new_channels = self.operator_check(new_channels)

        other_alarms += self.power_check(scan_arfcns)

        for ch in new_channels:
            self.add_channel(ch)
            for a in ch.ALARMS:
                print a

        for a in cell_alarms:
            print a

        for a in other_alarms:
            print a






def compare_list(x,y):
    return Counter(x) == Counter(y)

if __name__ == '__main__':

    #init = subprocess.call(['./setup'])

    scanner = Scanner()

    scanner.startup()

    while True:
        try:
            scan_speed = input("Please enter scan speed(0-5), to finish press enter ")
            scan_speed = int(scan_speed)
        except Exception:
            break
        if scan_speed >= 0 and scan_speed <= 5:
            scan_start = [time.time(), time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())]

            bts_info = scanner.scan(scan_speed)
            if not bts_info == None:
                scanner.check_info(bts_info)
            scan_end = [time.time(), time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+'\n']
            scanner.add_scan(scan_start, scan_end)
            xml_gsm_logg_write(scanner.cells, scanner.channels)
        else:
            continue


    scanner.finish()
    print 'Exiting IMSI Catcher Catcher'
    sys.exit(0)