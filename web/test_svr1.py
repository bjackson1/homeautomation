import unittest
import os
from hwcontrol import temperature, pins
from mock import patch, call, mock_open
import mock
#import RPi.GPIO



class hwcontrol_pin_tests(unittest.TestCase):
  def test_hwcontrol_pins_getpin_WhenCalledWithAnyPinNumberAndMockedHigh_ReturnsTrue(self):
    with mock.patch('RPi.GPIO.input', return_value=True):
      ret = pins().getpin(22)
      self.assertEqual(True, ret)

  def test_hwcontrol_pins_getpin_WhenCalledWithAnyPinNumberAndMockedLow_ReturnsFalse(self):
    with mock.patch('RPi.GPIO.input', return_value=False):
      ret = pins().getpin(22)
      self.assertEqual(False, ret)

  def test_hwcontrol_pins_setpin_WhenCalledWithAnyPinNmberAndFalse_WillCallRPi_GPIO_OuputWithFalse(self):
    with mock.patch('RPi.GPIO.output') as mock_method:
      ret = pins().setpin(22, 'on')
      mock_method.assert_called_with(22, True)

  def test_hwcontrol_pins_setpin_WhenCalledWithAnyPinNmberAndTrue_WillCallRPi_GPIO_OuputWithTrue(self):
    with mock.patch('RPi.GPIO.output') as mock_method:
      ret = pins().setpin(22, 'off')
      mock_method.assert_called_with(22, False)




class hwcontrol_temperature_tests(unittest.TestCase):
  def test_hwcontrol_temperature_get_WhenCalledWithAnyParameterAndMockedWithTestDataFileContainingLowValue_Returns0point1(self):
    with mock.patch('__builtin__.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=100'):
      temp = temperature().get('dummyid')
      self.assertEqual(0.1, temp)

  def test_hwcontrol_temperature_get_WhenCalledWithAnyParameterAndMockedWithTestDataFileContainingNegativeValue_ReturnsMinus12point7(self):
    with mock.patch('__builtin__.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=-12700'):
      temp = temperature().get('dummyid')
      self.assertEqual(-12.7, temp)

  def test_hwcontrol_temperature_get_WhenCalledWithAnyParameterAndMockedWithTestDataFileContainingHighValue_Returns130point1(self):
    with mock.patch('__builtin__.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=130100'):
      temp = temperature().get('dummyid')
      self.assertEqual(130.1, temp)

#  def test_upper(self):
#    self.assertEqual(True, True)

if __name__ == '__main__':
  unittest.main()


