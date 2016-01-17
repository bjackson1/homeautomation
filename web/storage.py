import redis

class redisclient:
  def __init__(self, address, port):
    self.redisconnection = redis.StrictRedis(host=address, port=port, db=0)

  def get(self, key):
    return self.redisconnection.get(key)
    
  def getasstring(self, key):
    return self.get(key).decode('utf-8')

  def getasint(self, key):
    return int(self.get(key).decode('utf-8'))
    
  def set(self, key, value):
    self.redisconnection.set(key, value)
    
