from time import sleep
from gnuradio import uhd

def wait_until_lock(uhd_usrp_source):

    gps_lock = False

    try:
        while True:
            lock = uhd_usrp_source.get_mboard_sensor(name='gps_locked')
            if lock.value == 'true':
                gps_lock = True
                print 'GPS lock obtained.'
                break
            sleep(2)


    except KeyboardInterrupt:
            print 'Did not obtain GPS lock.'

    return gps_lock


def get_gps_location():

    uhd_usrp_source = uhd.usrp_source(device_addr="addr=192.168.10.2",
                                    stream_args=uhd.stream_args(
                                        cpu_format="fc32",
                                        channels=range(1)
                                    ))

    gps_lock = wait_until_lock(uhd_usrp_source)
    if not gps_lock:
        return

    location = uhd_usrp_source.get_mboard_sensor(name='gps_gpgga')
    print 'Location obtained from GPS: '+ location.value
    return location.value



def gps_check():
    uhd_usrp_source = uhd.usrp_source(device_addr="addr=192.168.10.2",
                                    stream_args=uhd.stream_args(
                                        cpu_format="fc32",
                                        channels=range(1)
                                    ))

    lock = uhd_usrp_source.get_mboard_sensor(name='gps_locked')
    print lock.value
    location = uhd_usrp_source.get_mboard_sensor(name='gps_gpgga')
    print location.value

if __name__ == '__main__':
    gps_check()




