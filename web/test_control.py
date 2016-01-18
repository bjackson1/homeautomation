import unittest
import mock
from mock import patch, call, mock_open

from control import control
import networking
    
class controlunittests(unittest.TestCase):
  testConfigLocalControl1 = {'id': 'test1', 'name': 'Test Control 1', 'host': '127.0.0.1', 'controlpin': '28'}
  testConfigLocalControl2 = {'id': 'test1', 'name': 'Test Control 1', 'host': '127.0.0.1', 'controlpin': '28', 'statuspin': '14'}
  testConfigLocalControl3 = {'id': 'test1', 'name': 'Test Control 1', 'host': '127.0.0.1', 'controlpin': '28', 'reversed': True}
  testConfigRemoteControl1 = {'name': 'Test Control 2', 'host': '10.20.30.40', 'id': '28-000000000001'}
  
  # Positive tests for basic class functionality
  def test_init_WhenCalledWithLocalHostAddress_SetsExpectedPropertiesOnCreatedClass(self):
    cfg = self.testConfigLocalControl1
    c = control(cfg)
    self.assertEqual(cfg['id'], c.id)
    self.assertEqual(int(cfg['controlpin']), c.controlpin)
    #self.assertEqual(cfg['statuspin'], c.statuspin)
    self.assertEqual(cfg['name'], c.name)
    self.assertEqual(cfg['host'], c.host)
    self.assertEqual(False, c.reversed)
    self.assertEqual(True, c.islocal)

  def test_init_WhenCalledWithStatusPin_SetsExpectedStatusPinValue(self):
    cfg = self.testConfigLocalControl2
    c = control(cfg)
    self.assertEqual(14, c.statuspin)

  def test_init_WhenCalledWithReversedSet_SetsExpectedReversedValue(self):
    cfg = self.testConfigLocalControl3
    c = control(cfg)
    self.assertEqual(True, c.reversed)

  def test_set_WhenCalledWithOnAndNonReversedNoStatusItem_SetsGPIOPinToOne(self):
    with mock.patch('storage.redisclient.set',) as mocked_redis, mock.patch('RPi.GPIO.output',) as mocked_rpi:
      cfg = self.testConfigLocalControl1
      c = control(cfg)
      c.set('on')
      mocked_redis.assert_called_with('test1', 'on')
      mocked_rpi.assert_called_with(28, 1)

  def test_set_WhenCalledWithOnAndReversedNoStatusItem_SetsGPIOPinToZero(self):
    with mock.patch('storage.redisclient.set',) as mocked_redis, mock.patch('RPi.GPIO.output',) as mocked_rpi:
      cfg = self.testConfigLocalControl3
      c = control(cfg)
      c.set('on')
      mocked_redis.assert_called_with('test1', 'on')
      mocked_rpi.assert_called_with(28, 0)

  def test_set_WhenCalledWithOffAndNonReversedNoStatusItem_SetsGPIOPinToZeroAndStatusPinToZero(self):
    with mock.patch('storage.redisclient.set',) as mocked_redis, mock.patch('RPi.GPIO.output',) as mocked_rpi:
      cfg = self.testConfigLocalControl2
      c = control(cfg)
      c.set('off')
      mocked_redis.assert_called_with('test1', 'off')
      mocked_rpi.assert_any_call(28, 0)
      mocked_rpi.assert_any_call(14, 0)

  # def test_get_WhenCalledWithMockedOn_CallsRedisClientWithCorrectKeyAndReturnsOn(self):
  #   with mock.patch('storage.redisclient.get', return_value='on') as mocked_redis, mock.patch('RPi.GPIO.input', return_value=1) as mocked_rpi:
  #     cfg = self.testConfigLocalControl2
  #     c = control(cfg)
  #     ret = c.get()
  #     mocked_redis.assert_called_with('test1')
  #     #mocked_rpi.assert_any_call(28)
  #     #mocked_rpi.assert_any_call(14)
  #     self.assertEqual('on', ret)



  # def test_init_WhenCalledWithIDAndRemoteHostAddress_SetsExpectedPropertiesOnCreatedClass(self):
  #   cfg = self.testConfigRemoteSensor1
  #   ts = sensors.temperaturesensor(cfg)
  #   self.assertEqual(cfg['id'], ts.id)
  #   self.assertEqual(cfg['name'], ts.name)
  #   self.assertEqual(False, ts.islocal)
  #   self.assertEqual(cfg['host'], ts.host)

  # def test_update_WhenCalledWithMockedRedis_AttemptsToReadSensorFileAndToSetValueInRedisAndReturnsSetValue(self):
  #   with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.update()
  #     mocked_redis.assert_called_with(cfg['id'], 20)
  #     self.assertEqual(20, temp)
      
  # def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf20InRedisAndReturnsSetValue(self):
  #   with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.update()
  #     mocked_redis.assert_called_with(cfg['id'], 20)
  #     mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
  #     self.assertEqual(20, temp)
      
  # def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOfMinus20InRedisAndReturnsSetValue(self):
  #   with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=-20000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.update()
  #     mocked_redis.assert_called_with(cfg['id'], -20)
  #     mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
  #     self.assertEqual(-20, temp)
      
  # def test_update_WhenCalledAgainstLocalSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf120InRedisAndReturnsSetValue(self):
  #   with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=120000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.update()
  #     mocked_redis.assert_called_with(cfg['id'], 120)
  #     mocked_file.assert_called_with('/sys/bus/w1/devices/' + cfg['id'] + '/w1_slave')
  #     self.assertEqual(120, temp)
      
  # def test_update_WhenCalledAgainstRemoteSensorWithMockedIO_AttemptsToReadSensorFileAndToSetValueOf120InRedisAndReturnsSetValue(self):
  #   with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=120000') as mocked_file, mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigRemoteSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.update()
  #     mocked_redis.assert_not_called()
  #     mocked_file.assert_not_called()
  #     self.assertEqual(None, temp)

  # def test_get_WhenCalledWithMockedRedisForLocalSensorValue_AttemptsToGetValueFromRedisAndReturns20(self):
  #   with mock.patch('storage.redisclient.get', return_value=20) as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.get()
  #     mocked_redis.assert_called_with(cfg['id'])
  #     self.assertEqual(20, temp)

  # def test_get_WhenCalledWithMockedRedisForRemoteSensorValue_AttemptsToGetValueFromRedisAndReturns20(self):
  #   with mock.patch('storage.redisclient.get', return_value=20) as mocked_redis:
  #     cfg = self.testConfigRemoteSensor1
  #     ts = sensors.temperaturesensor(cfg)
  #     temp = ts.get()
  #     mocked_redis.assert_called_with(cfg['id'])
  #     self.assertEqual(20, temp)
    
  # # Negative tests
  # def test_update_WhenCalledAgainstNonExistentFile_ThrowsFileNotFoundError(self):
  #   with mock.patch('storage.redisclient.set') as mocked_redis:
  #     cfg = self.testConfigLocalSensor1
  #     ts = sensors.temperaturesensor(cfg)
      
  #     try:
  #       ts.update()
  #       self.assertFalse('No exception thrown when FileNotFound error was expected')
  #     except FileNotFoundError:
  #       self.assertTrue('OK')
  #     except Exception as ex:
  #       self.assertFalse('Unexpected \'' + type(ex).__name__ + '\' exception thrown when FileNotFound error was expected')


if __name__ == '__main__':
  unittest.main()
