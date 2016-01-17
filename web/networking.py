from netifaces import interfaces, ifaddresses, AF_INET

def ip4_addresses():
  ip_list = []
  for interface in interfaces():
    for link in ifaddresses(interface)[AF_INET]:
      ip_list.append(link['addr'])
  return ip_list

def addressislocal(ipaddress):
  return ipaddress in ip4_addresses()
  