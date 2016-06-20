import time
from Infraction import Alarm
from collections import Counter

def compare_list(x,y):
    return Counter(x) == Counter(y)

class Channel:
    def __init__(self, arfcn, mcc, mnc, lac, ci, crh, cro, to, pt, t3212, rxlev, txpwr, balist, cellarfcns, scans=[], alarms=[]):
        self.ARFCN = int(arfcn)
        self.MCC = str(mcc)
        self.MNC = str(mnc)
        self.LAC = str(lac)
        self.CI = int(ci)
        self.CRH = self.value_check(crh)
        self.CRO = self.value_check(cro)
        self.TO = self.value_check(to)
        self.PT = self.value_check(pt)
        self.T3212 = self.value_check(t3212)
        self.RXLEV = self.value_check(rxlev)
        self.TXPWR = self.value_check(txpwr)
        self.BAList = [int(x) for x in balist]
        self.CellARFCNS = [int(x) for x in cellarfcns]
        self.ALARMS = alarms
        self.SCANS = scans
        self.LOCAL_POWERS = []



    def __eq__(self, other):
        output = self.ARFCN == other.ARFCN
        output = output and self.MCC == other.MCC
        output = output and self.MNC == other.MNC
        output = output and self.LAC == other.LAC
        output = output and self.CI == other.CI
        output = output and self.CRH == other.CRH
        output = output and self.CRO == other.CRO
        output = output and self.TO == other.TO
        output = output and self.PT == other.PT
        output = output and self.T3212 == other.T3212
        output = output and self.RXLEV == other.RXLEV
        output = output and self.TXPWR == other.TXPWR
        output = output and compare_list(self.BAList, other.BAList)
        output = output and compare_list(self.CellARFCNS, other.CellARFCNS)
        return  output



    def __str__(self):
        output = 'Channel:\n'
        output += '  ARFCN: '+str(self.ARFCN)+'\n'
        output += '  MCC: '+str(self.MCC)+'\n'
        output += '  MNC: '+str(self.MNC)+'\n'
        output += '  LAC: '+str(self.LAC)+'\n'
        output += '  CI: '+str(self.CI)+'\n'
        output += '  Other ARFCNs in same cell: '+str(self.CellARFCNS)+'\n'
        output += '  CRH: '+ self.print_value(self.CRH)+'\n'
        output += '  CRO: '+self.print_value(self.CRO)+'\n'
        output += '  TO: '+self.print_value(self.TO)+'\n'
        output += '  PT: '+self.print_value(self.PT)+'\n'
        output += '  T3212: '+self.print_value(self.T3212)+'\n'
        output += '  RXLEV ACRESS MIN: '+self.print_value(self.RXLEV)+'\n'
        output += '  MS TXPWR MAX CCH: '+self.print_value(self.TXPWR)+'\n'
        output += '  Neighbour List: '+str(self.BAList)+'\n'
        output += 'Channel was scanned at:\n'
        for scan in self.SCANS:
            output += '  ' + str(scan) + '\n'
        if len(self.ALARMS):
            output += 'Channel Alarms:\n'
            for alarm in self.ALARMS:
                output += '  ' + str(alarm)+'\n'
        output += '\n'
        return output

    def print_without_alarms(self):
        output = 'Channel:\n'
        output += '  ARFCN: '+str(self.ARFCN)
        output += '  MCC: '+str(self.MCC)
        output += '  MNC: '+str(self.MNC)
        output += '  LAC: '+str(self.LAC)
        output += '  CI: '+str(self.CI)
        output += '  Other ARFCNs in same cell: '+str(self.CellARFCNS)
        output += '  CRH: '+ self.print_value(self.CRH)
        output += '  CRO: '+self.print_value(self.CRO)
        output += '  TO: '+self.print_value(self.TO)
        output += '  PT: '+self.print_value(self.PT)
        output += '  T3212: '+self.print_value(self.T3212)
        output += '  RXLEV ACCESS MIN: '+self.print_value(self.RXLEV)
        output += '  MS TXPWR MAX CCH: '+self.print_value(self.TXPWR)
        output += '  Neighbour List: '+str(self.BAList)
        return output

    def minor_equality(self, other):
        return self.ARFCN == other.ARFCN and self.CI == other.CI and self.MCC == other.MCC and self.MNC == other.MNC and self.LAC == other.LAC


    def add_alarm(self,alarm):
        self.ALARMS.append(alarm)

    def add_scan(self, scan):
        self.SCANS.append(scan)

    def add_local_power(self, power):
        self.LOCAL_POWERS.append(power)

    def get_max_local_power(self):
        if len(self.LOCAL_POWERS):
            return max(self.LOCAL_POWERS)

    def value_check(self, value):
        try:
            return int(value)
        except:
            return None

    def print_value(self, value):
        if value == None:
            return 'None'
        else:
            return str(value)








class Cell:

    def __init__(self, CI, MCC, MNC, LAC, arfcns, alarms = []):
        self.CI = int(CI)
        self.MCC = str(MCC)
        self.MNC = str(MNC)
        self.LAC = str(LAC)
        self.ARFCNS = [int(x) for x in arfcns]
        self.ALARMS = alarms

    def __eq__(self, other):
        sets = compare_list(self.ARFCNS, other.ARFCNS)
        ci = self.CI == other.CI
        mcc = self.MCC == other.MCC
        mnc = self.MNC == other.MNC
        lac = self.LAC == other.LAC
        return ci and mcc and mnc and lac and sets

    def __str__(self):
        output = '\n'
        output += 'Cell\n'
        output += '  Cell ID: '+ str(self.CI)+' LAI: '+str(self.MCC)+'/'+str(self.MNC)+'/'+str(self.LAC)+'\n'
        output += '  Cell\'s ARFCNs: ' + str(self.ARFCNS)+'\n'
        if len(self.ALARMS):
            output += 'Cell Alarms:\n'
            for alarm in self.ALARMS:
                output += '  '+str(alarm) + '\n'
        output += '\n'

        return output

    def bogus_arfcns(self, other):
        sets = compare_list(self.ARFCNS, other.ARFCNS)
        ci = self.CI == other.CI
        mcc = self.MCC == other.MCC
        mnc = self.MNC == other.MNC
        lac = self.LAC == other.LAC
        return ci and mcc and mnc and lac and (not sets)

    def toString(self):
        return self.__str__()


    def add_alarm(self,alarm):
        self.ALARMS.append(alarm)