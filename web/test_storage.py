import unittest
import mock
from mock import patch, call, mock_open

from storage import redisclient

class storageunittests(unittest.TestCase):
  testMockConfig = {'host': '10.20.30.40', 'port': '6379'}
  
  # Positive tests for basic class functionality
  def test_init_WhenCalledWithMockConfig_WillCallRedisConnection(self):
    with mock.patch('redis.StrictRedis') as mocked_redis:
      cfg = self.testMockConfig
      r = redisclient(cfg['host'], cfg['port'])
      mocked_redis.assert_called_with(host=cfg['host'], port=cfg['port'], db=0)

class storageintegrationtests(unittest.TestCase):
  testIntegrationConfig = {'host': '127.0.0.1', 'port': '6379'}
  
  def test_init_WhenCalledWithMockConfig_WillCallRedisConnection(self):
    cfg = self.testIntegrationConfig
    r = redisclient(cfg['host'], cfg['port'])
    self.assertEqual('test_echo', r.redisconnection.echo('test_echo').decode('utf-8'))
      
  def test_setandgetasint_WhenCalledWithMockKeyValue_WillCallRedisSetWithValues(self):
    cfg = self.testIntegrationConfig
    r = redisclient(cfg['host'], cfg['port'])
    r.set('wibble', 123)
    self.assertEqual(123, r.getasint('wibble'))

  def test_setandgetasstring_WhenCalledWithMockKeyValue_WillCallRedisSetWithValues(self):
    cfg = self.testIntegrationConfig
    r = redisclient(cfg['host'], cfg['port'])
    r.set('wibble', 'abc')
    self.assertEqual('abc', r.getasstring('wibble'))


if __name__ == '__main__':
  unittest.main()
  