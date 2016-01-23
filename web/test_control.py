import unittest
import mock
from mock import patch, call, mock_open

from control import control
import networking


class controlunittests(unittest.TestCase):
    testConfigLocalControl1 = {'name': 'Test Control 1',
                               'host': '127.0.0.1',
                               'controlpin': '28'}
    testConfigLocalControl2 = {'name': 'Test Control 1',
                               'host': '127.0.0.1', 'controlpin': '28',
                               'statuspin': '14'}
    testConfigLocalControl3 = {'name': 'Test Control 1',
                               'host': '127.0.0.1', 'controlpin': '28',
                               'reversed': True}
    testConfigRemoteControl1 = {'name': 'Test Control 2',
                                'host': '10.20.30.40',
                                'id': '28-000000000001'}

    # Positive tests for basic class functionality
    def test_init_WhenCalledWithLocalHostAddress_SetsExpectedPropertiesOnCreatedClass(self):
        cfg = self.testConfigLocalControl1
        c = control('test1', cfg)
        self.assertEqual(int(cfg['controlpin']), c.controlpin)
        self.assertEqual(cfg['name'], c.name)
        self.assertEqual(cfg['host'], c.host)
        self.assertEqual(False, c.reversed)
        self.assertEqual(True, c.islocal)

    def test_init_WhenCalledWithStatusPin_SetsExpectedStatusPinValue(self):
        cfg = self.testConfigLocalControl2
        c = control('test1', cfg)
        self.assertEqual(14, c.statuspin)

    def test_init_WhenCalledWithReversedSet_SetsExpectedReversedValue(self):
        cfg = self.testConfigLocalControl3
        c = control('test1', cfg)
        self.assertEqual(True, c.reversed)

    def test_set_WhenCalledWithOnAndNonReversedStatus_SetsGPIOPinToOne(self):
        with mock.patch('storage.redisclient.set') as mocked_redis, mock.patch('RPi.GPIO.output') as mocked_rpi:
            cfg = self.testConfigLocalControl1
            c = control('test1', cfg)
            c.set('on')
            mocked_redis.assert_called_with('test1', 'on')
            mocked_rpi.assert_called_with(28, 1)

    def test_set_WhenCalledWithOnAndReversedStatus_SetsGPIOPinToZero(self):
        with mock.patch('storage.redisclient.set') as mocked_redis, mock.patch('RPi.GPIO.output') as mocked_rpi:
            cfg = self.testConfigLocalControl3
            c = control('test1', cfg)
            c.set('on')
            mocked_redis.assert_called_with('test1', 'on')
            mocked_rpi.assert_called_with(28, 0)

    def test_set_WhenCalledWithOffAndNonReversedNoStatusItem_SetsGPIOPinToZeroAndStatusPinToZero(self):
        with mock.patch('storage.redisclient.set') as mocked_redis, mock.patch('RPi.GPIO.output') as mocked_rpi:
            cfg = self.testConfigLocalControl2
            c = control('test1', cfg)
            c.set('off')
            mocked_redis.assert_called_with('test1', 'off')
            mocked_rpi.assert_any_call(28, 0)
            mocked_rpi.assert_any_call(14, 0)


if __name__ == '__main__':
    unittest.main()
