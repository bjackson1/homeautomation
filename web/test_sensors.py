import unittest
import mock
from mock import patch, call, mock_open

import sensors
import networking
    
class temperaturesensortests(unittest.TestCase):
  testConfigLocalSensor1 = {'name': 'Test Sensor 1', 'host': '127.0.0.1', 'id': '28-000000000001'}
  testConfigRemoteSensor1 = {'name': 'Test Sensor 2', 'host': '10.20.30.40', 'id': '28-000000000001'}
  
  # Positive tests for basic class functionality
  def test_init_WhenCalledWithIDAndLocalHostAddress_SetsExpectedPropertiesOnCreatedClass(self):
    cfg = self.testConfigLocalSensor1
    ts = sensors.temperaturesensor(cfg)
    self.assertEqual(cfg['id'], ts.id)
    self.assertEqual(cfg['name'], ts.name)
    self.assertEqual(cfg['host'], ts.host)
    #self.assertEqual('http://' + cfg['host'] + ':5000/temp/' + cfg['id'], ts.address)
    self.assertEqual(True, ts.islocal)

  def test_init_WhenCalledWithIDAndRemoteHostAddress_SetsExpectedPropertiesOnCreatedClass(self):
    cfg = self.testConfigRemoteSensor1
    ts = sensors.temperaturesensor(cfg)
    self.assertEqual(cfg['id'], ts.id)
    self.assertEqual(cfg['name'], ts.name)
    self.assertEqual(cfg['host'], ts.host)
    #self.assertEqual('http://' + cfg['host'] + ':5000/temp/' + cfg['id'], ts.address)
    self.assertEqual(False, ts.islocal)

  def test_update_WhenCalledWithMockedRedis_AttemptsToReadSensorFileAndToSetValueInRedisAndReturnsSetValue(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.update()
      mocked_redis.assert_called_with(cfg['id'], 20)
      self.assertEqual(20, temp)
      
  def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf20InRedisAndReturnsSetValue(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.update()
      mocked_redis.assert_called_with(cfg['id'], 20)
      mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
      self.assertEqual(20, temp)
      
  def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOfMinus20InRedisAndReturnsSetValue(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=-20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.update()
      mocked_redis.assert_called_with(cfg['id'], -20)
      mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
      self.assertEqual(-20, temp)
      
  def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf120InRedisAndReturnsSetValue(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=120000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.update()
      mocked_redis.assert_called_with(cfg['id'], 120)
      mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
      self.assertEqual(120, temp)
      
  def test_update_WhenCalledAgainstRemoteSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf120InRedisAndReturnsSetValue(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=120000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigRemoteSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.update()
      mocked_redis.assert_not_called()
      mocked_file.assert_not_called()
      self.assertEqual(None, temp)

  def test_get_WhenCalledWithMockedRedisForLocalSensorValue_AttemptsToGetValueFromRedisAndReturns20(self):
    with mock.patch('storage.redisclient.get', return_value=20) as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.get()
      mocked_redis.assert_called_with(cfg['id'])
      self.assertEqual(20, temp)

  def test_get_WhenCalledWithMockedRedisForRemoteSensorValue_AttemptsToGetValueFromRedisAndReturns20(self):
    with mock.patch('storage.redisclient.get', return_value=20) as mocked_redis:
      cfg = self.testConfigRemoteSensor1
      ts = sensors.temperaturesensor(cfg)
      temp = ts.get()
      mocked_redis.assert_called_with(cfg['id'])
      self.assertEqual(20, temp)
    
  # Negative tests
  def test_update_WhenCalledAgainstNonExistentFile_ThrowsFileNotFoundError(self):
    with mock.patch('storage.redisclient.set') as mocked_redis:
      cfg = self.testConfigLocalSensor1
      ts = sensors.temperaturesensor(cfg)
      
      try:
        ts.update()
        self.assertFalse('No exception thrown when FileNotFound error was expected')
      except FileNotFoundError:
        self.assertTrue('OK')
      except Exception as ex:
        self.assertFalse('Unexpected \'' + type(ex).__name__ + '\' exception thrown when FileNotFound error was expected')


if __name__ == '__main__':
  unittest.main()
