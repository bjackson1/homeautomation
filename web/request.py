
import sys

sys.path.append('/var/www/homeautomation/web')

import urllib.request


def getfromurl(url):
  with urllib.request.urlopen(url, timeout=5) as response:
    ret = response.read().decode('utf-8')

  return ret
