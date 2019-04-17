from __future__ import print_function
import socket

import psutil
# from psutil._common import bytes2human


af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}

duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
}


def main():
    
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    for nic, addrs in psutil.net_if_addrs().items():
        print("%s:" % (nic))

        if(nic=="eno1"):
            print("HI")
   
            for addr in addrs:
                if(af_map.get(addr.family, addr.family)=="IPv4"):                    
                    print("JSR")

                    print("    %-4s" % af_map.get(addr.family, addr.family), end="")
                    print(" address   : %s" % addr.address)
                    
            print("")


if __name__ == '__main__':
    main()