from Infraction import Alarm
from ChannelInfo import Cell, Channel
from lxml import etree as ET
from Scan import Scan


def xml_gsm_logg_write(cells, channels):
    xml_root = ET.Element('gsmlogg')
    xml_cells = ET.SubElement(xml_root, 'cells')
    for ce in cells:
        for cell in cells[ce]:
            xml_cell = get_cell_element(cell)
            xml_cells.append(xml_cell)

    xml_channels = ET.SubElement(xml_root, 'channels')
    for ch in channels:
        for channel in channels[ch]:
            xml_channel = get_channel_element(channel)
            xml_channels.append(xml_channel)

    tree = ET.ElementTree(xml_root)
    tree.write('gsmlogg.xml', pretty_print=True)


def xml_gsm_logg_read():
    try:
        xml_tree = ET.parse('./gsmlogg.xml')
    except:
        return [], []

    xml_root =  xml_tree.getroot()

    xml_cells = xml_root.findall('cells/cell')
    cells = get_cells_from_xml(xml_cells)

    xml_channels = xml_root.findall('channels/channel')
    channels = get_channels_from_xml(xml_channels)

    return cells, channels

def get_channels_from_xml(xml_channels):
    channels = []
    for xml_channel in xml_channels:
        channel = get_channel_from_xml(xml_channel)
        if isinstance(channel, Channel):
            channels.append(channel)
    return channels

def get_channel_from_xml(xml_channel):
    all = xml_channel.findall('*')
    arfcn = None
    mcc = None
    mnc = None
    lac = None
    ci = None
    crh = None
    cro = None
    to = None
    pt = None
    t3212 = None
    rxlev = None
    txpwr = None
    balist = None
    cellarfcns = None
    alarms = None
    scans = None

    for e in all:
        if e.tag == 'arfcn':
            arfcn = int(e.text)
        elif e.tag == 'mcc':
            mcc = str(e.text)
        elif e.tag == 'mnc':
            mnc = str(e.text)
        elif e.tag == 'lac':
            lac = str(e.text)
        elif e.tag == 'ci':
            ci = int(e.text)
        elif e.tag == 'crh':
            crh = none_check_read(e.text)
        elif e.tag == 'cro':
            cro = none_check_read(e.text)
        elif e.tag == 'to':
            to = none_check_read(e.text)
        elif e.tag == 'pt':
            pt = none_check_read(e.text)
        elif e.tag == 't3212':
            t3212 = none_check_read(e.text)
        elif e.tag == 'rxlev':
            rxlev = none_check_read(e.text)
        elif e.tag == 'txpwr':
            txpwr = none_check_read(e.text)
        elif e.tag == 'balist':
            balist = get_arfcns_from_xml(e)
        elif e.tag == 'cellarfcns':
            cellarfcns = get_arfcns_from_xml(e)
        elif e.tag == 'alarms':
            alarms = get_alarms_from_xml(e)
        elif e.tag == 'scans':
            scans = get_scans_from_xml(e)

    if arfcn == None or mcc == None or mnc == None or lac == None or ci == None:
        return
    else:
        return Channel(arfcn, mcc, mnc,lac, ci, crh, cro, to, pt, t3212, rxlev, txpwr, balist, cellarfcns, scans, alarms)

def get_cells_from_xml(xml_cells):
    cells = []
    for xml_cell in xml_cells:
        cell = get_cell_from_xml(xml_cell)
        if isinstance(cell, Cell):
            cells.append(cell)

    return cells

def get_cell_from_xml(xml_cell):
    all = xml_cell.findall('*')
    ci = None
    mcc = None
    mnc = None
    lac = None
    arfcns = None
    alarms = None
    for e in all:
        if e.tag == 'arfcns':
            arfcns = get_arfcns_from_xml(e)
        elif e.tag == 'ci':
            ci = int(e.text)
        elif e.tag == 'mcc':
            mcc = str(e.text)
        elif e.tag == 'mnc':
            mnc = str(e.text)
        elif e.tag == 'lac':
            lac = str(e.text)
        elif e.tag == 'alarms':
            alarms = get_alarms_from_xml(e)

    if ci == None or mcc == None or mnc == None or lac == None or arfcns == None or alarms == None:
        return
    else:
        return Cell(ci, mcc, mnc, lac, arfcns, alarms)

def get_arfcns_from_xml(xml_arfcns):
    arfcns = [int(a.text) for a in xml_arfcns.findall('arfcn')]
    return arfcns

def get_alarms_from_xml(xml_alarms):
    alarms = []
    for a in xml_alarms.findall('*'):
        alarm = get_alarm_from_xml(a)
        if isinstance(alarm, Alarm):
            alarms.append(alarm)
    return alarms

def get_alarm_from_xml(xml_alarm):
    time = None
    description = None
    location = None
    for c in xml_alarm.getchildren():
        if c.tag == 'time':
            time = c.text
        elif c.tag == 'description':
            description = c.text
        elif c.tag == 'location':
            location = c.text

    if time == None or description == None or location == None:
        return
    else:
        return Alarm(description, location,time)

def get_scans_from_xml(xml_scans):
    scans = []
    for xml_scan in xml_scans.findall('*'):
        scan = get_scan_from_xml(xml_scan)
        if isinstance(scan, Scan):
            scans.append(scan)
    return scans

def get_scan_from_xml(xml_scan):
    time = None
    location = None
    power = None
    for c in xml_scan.getchildren():
        if c.tag == 'time':
            time = c.text
        elif c.tag == 'location':
            location = c.text
        elif c.tag == 'power':
            power = c.text

    if time == None or location == None or power == None:
        return
    else:
        return Scan(time, location, power)

def get_cell_element(cell):
    xml_cell = ET.Element('cell')
    xml_ci = ET.SubElement(xml_cell, 'ci')
    xml_ci.text = str(cell.CI)
    xml_mcc = ET.SubElement(xml_cell, 'mcc')
    xml_mcc.text = str(cell.MCC)
    xml_mnc = ET.SubElement(xml_cell, 'mnc')
    xml_mnc.text = str(cell.MNC)
    xml_lac = ET.SubElement(xml_cell, 'lac')
    xml_lac.text = str(cell.LAC)
    xml_arfcns = ET.SubElement(xml_cell, 'arfcns')
    for arfcn in cell.ARFCNS:
        xml_arfcn = get_arfcn_element(arfcn)
        xml_arfcns.append(xml_arfcn)
    xml_alarms = ET.SubElement(xml_cell, 'alarms')
    for alarm in cell.ALARMS:
        xml_alarm = get_alarm_element(alarm)
        xml_alarms.append(xml_alarm)

    return xml_cell

def get_channel_element(channel):
    xml_channel = ET.Element('channel')
    xml_arfcn = ET.SubElement(xml_channel, 'arfcn')
    xml_arfcn.text = str(channel.ARFCN)
    xml_ci = ET.SubElement(xml_channel, 'ci')
    xml_ci.text = str(channel.CI)
    xml_mcc = ET.SubElement(xml_channel, 'mcc')
    xml_mcc.text = str(channel.MCC)
    xml_mnc = ET.SubElement(xml_channel, 'mnc')
    xml_mnc.text = str(channel.MNC)
    xml_lac = ET.SubElement(xml_channel, 'lac')
    xml_lac.text = str(channel.LAC)
    xml_crh = ET.SubElement(xml_channel, 'crh')
    xml_crh.text = none_check_write(channel.CRH)
    xml_cro = ET.SubElement(xml_channel, 'cro')
    xml_cro.text = none_check_write(channel.CRO)
    xml_to = ET.SubElement(xml_channel, 'to')
    xml_to.text = none_check_write(channel.TO)
    xml_pt = ET.SubElement(xml_channel, 'pt')
    xml_pt.text = none_check_write(channel.PT)
    xml_t3212 = ET.SubElement(xml_channel, 't3212')
    xml_t3212.text = none_check_write(channel.T3212)
    xml_rxlev = ET.SubElement(xml_channel, 'rxlev')
    xml_rxlev.text = none_check_write(channel.RXLEV)
    xml_txpwr = ET.SubElement(xml_channel, 'txpwr')
    xml_txpwr.text = none_check_write(channel.TXPWR)
    xml_balist = ET.SubElement(xml_channel, 'balist')
    for arfcn in channel.BAList:
        xml_arfcn = get_arfcn_element(arfcn)
        xml_balist.append(xml_arfcn)
    xml_cellarfcns = ET.SubElement(xml_channel, 'cellarfcns')
    for arfcn in channel.CellARFCNS:
        xml_arfcn = get_arfcn_element(arfcn)
        xml_cellarfcns.append(xml_arfcn)
    xml_alarms = ET.SubElement(xml_channel, 'alarms')
    for alarm in channel.ALARMS:
        xml_alarm = get_alarm_element(alarm)
        xml_alarms.append(xml_alarm)
    xml_scans = ET.SubElement(xml_channel, 'scans')
    for scan in channel.SCANS:
        xml_scan = get_scan_element(scan)
        xml_scans.append(xml_scan)


    return xml_channel

def get_arfcn_element(arfcn):
    xml_arfcn = ET.Element('arfcn')
    xml_arfcn.text = str(arfcn)
    return xml_arfcn

def get_alarm_element(alarm):
    xml_alarm = ET.Element('alarm')
    xml_time = ET.SubElement(xml_alarm, 'time')
    xml_time.text = str(alarm.time)
    xml_description = ET.SubElement(xml_alarm, 'description')
    xml_description.text = str(alarm.description)
    xml_location = ET.SubElement(xml_alarm, 'location')
    xml_location.text = str(alarm.location)
    return xml_alarm

def get_scan_element(scan):
    xml_scan = ET.Element('scan')
    xml_time = ET.SubElement(xml_scan, 'time')
    xml_time.text = str(scan.time)
    xml_location = ET.SubElement(xml_scan, 'location')
    xml_location.text = str(scan.location)
    xml_power = ET.SubElement(xml_scan, 'power')
    xml_power.text = str(scan.power)
    return xml_scan

def none_check_write(value):
    if value == None:
        return 'None'
    else:
        return str(value)

def none_check_read(value):
    if value == 'None':
        return None
    else:
        return int(value)



if __name__ == '__main__':
    xml_gsm_logg_read()

