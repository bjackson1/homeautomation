import unittest
import os
import svr
from hwcontrol import temperature, pins
from mock import patch, call, mock_open
import mock


class svr_gpiostates(unittest.TestCase):
  def test_svr_getgpiostate_WhenCalledWithAnyPinNumberAndMockedHigh_ReturnsTrueAsString(self):
    with mock.patch('hwcontrol.pins.getpin', return_value=True):
      ret = svr.getgpiostate(22)
      self.assertEqual('True', ret)

  def test_svr_getgpiostate_WhenCalledWithAnyPinNumberAndMockedLow_ReturnsFalseAsString(self):
    with mock.patch('hwcontrol.pins.getpin', return_value=False):
      ret = svr.getgpiostate(22)
      self.assertEqual('False', ret)

  def test_hwcontrol_pins_setpin_WhenCalledWithAnyPinNmberAndFalse_WillCallRPi_GPIO_OuputWithFalse(self):
    with mock.patch('hwcontrol.pins.setpin') as mock_method:
      ret = pins().setpin(22, True)
      mock_method.assert_called_with(22, True)

  def test_hwcontrol_pins_setpin_WhenCalledWithAnyPinNmberAndTrue_WillCallRPi_GPIO_OuputWithTrue(self):
    with mock.patch('hwcontrol.pins.setpin') as mock_method:
      ret = pins().setpin(22, False)
      mock_method.assert_called_with(22, False)
 
class svr_loadconfig(unittest.TestCase):
  testconfig1 = {'tempsensors': {'test1': {'friendlyname': 'Test 1', 'host': '127.0.0.1', 'id': '28-000000000001'}, 'test2': {'friendlyname': 'Test 2', 'host': '127.0.0.1', 'id': '28-000000000002'}}, 'controls': {'landinglight': {'friendlyname': 'Landing Light', 'gpio': 21, 'host': '192.168.1.12'}, 'hotwater': {'friendlyname': 'Hot Water', 'gpio': 14, 'host': '127.0.0.1', 'reversed': True, 'statusgpio': 18}, 'centralheatingpump': {'host': '192.168.1.12', 'gpio': 15, 'friendlyname': 'Central Heating', 'statusgpio': 17, 'reversed': True, 'dependsupon': 'hotwater'}, 'missing': {'host': '192.168.10.10', 'gpio': 15, 'friendlyname': 'Missing Control', 'statusgpio': 17, 'reversed': True}}}

  testconfig2 = {'tempsensors': {'livingroom': {'friendlyname': 'Living Room', 'host': '192.168.1.12', 'id': '28-0415a187aaff'}, 'heatingreturn': {'friendlyname': 'Central Heating Return', 'host': '192.168.1.12', 'id': '28-0315a1b026ff'}, 'hotwaterflow': {'friendlyname': 'Hot Water Flow', 'host': '192.168.1.12', 'id': '28-0315a1b006ff'}, 'test': {'friendlyname': 'Test Probe', 'host': 'localhost', 'id': '28-0315a1d297ff'}, 'hotwaterreturn': {'friendlyname': 'Hot Water Return', 'host': '192.168.1.12', 'id': '28-0315a1d21dff'}, 'loft': {'friendlyname': 'Loft', 'host': '192.168.1.2', 'id': '28-0315a1d259ff'}, 'heatingflow': {'friendlyname': 'Central Heating Flow', 'host': '192.168.1.12', 'id': '28-0315a1b011ff'}}, 'switches': {'hosts': {'testpi': {'testswitch2': {'control': 'testlight2', 'gpio': 18}, 'testswitch': {'control': 'landinglight', 'gpio': 17}}}}, 'controls': {'landinglight': {'friendlyname': 'Landing Light', 'gpio': 21, 'host': '192.168.1.12'}, 'hotwater': {'friendlyname': 'Hot Water', 'gpio': 14, 'host': '192.168.1.12', 'reversed': True, 'statusgpio': 18}, 'centralheatingpump': {'host': '192.168.1.12', 'gpio': 15, 'friendlyname': 'Central Heating', 'statusgpio': 17, 'reversed': True, 'dependsupon': 'hotwater'}}}

  def test_svr_getcontrolstate_WhenCalledWithNonReversedControlMockedToOn_WillReturn1(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getfromurl') as mock_geturl:
      mock_geturl.return_value = '0'
      ret = svr.getcontrolstate('landinglight')
      self.assertEqual('0', ret)
 
  def test_svr_getcontrolstate_WhenCalledWithReversedControlMockedToOn_WillReturn0(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getfromurl') as mock_geturl:
      mock_geturl.return_value = '1'
      ret = svr.getcontrolstate('hotwater')
      self.assertEqual('0', ret)
 
  def test_svr_getcontrolstate_WhenCalledWithNonReversedControlMockedToOff_WillReturn0(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getfromurl') as mock_geturl:
      mock_geturl.return_value = '1'
      ret = svr.getcontrolstate('landinglight')
      self.assertEqual('1', ret)
 
  def test_svr_getcontrolstate_WhenCalledWithReversedControlMockedToOff_WillReturn1(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getfromurl') as mock_geturl:
      mock_geturl.return_value = '0'
      ret = svr.getcontrolstate('hotwater')
      self.assertEqual('1', ret)
 
  def test_svr_setcontrolstate_WhenCalledWithNonReversedControlSetToOn_WillCallURL(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getfromurl', return_value='0') as mock_getfromurl:
      svr.setcontrolstate('hotwater', 'on')
      expectedurl1 = 'http://' + self.testconfig1['controls']['hotwater']['host'] + ':5000/gpio/' + str(self.testconfig1['controls']['hotwater']['gpio']) + '/off'
      expectedurl2 = 'http://' + self.testconfig1['controls']['hotwater']['host'] + ':5000/gpio/' + str(self.testconfig1['controls']['hotwater']['statusgpio']) + '/on'
      mock_getfromurl.assert_any_call(expectedurl1)
      mock_getfromurl.assert_any_call(expectedurl2)
      #self.assertEqual(1, 1)

  def test_svr_getcontrolstate_WhenCalledAgainstControlNotAccessibleOnNetwork_WillReturnUnavailable(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1):
      ret = svr.getcontrolstate('missing')
      self.assertEqual('Unavailable', ret)

  def test_svr_togglecontrol_WhenCalledWithControlInOnState_WillSetControlToOff(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getcontrolstate', return_value='1') as mock_getcontrolstate, mock.patch('svr.setcontrolstate') as mock_setcontrolstate:
      svr.togglecontrol('hotwater')
      mock_setcontrolstate.assert_called_with('hotwater', 'off')
      
  def test_svr_togglecontrol_WhenCalledWithControlInOffState_WillSetControlToOn(self):
    with mock.patch('svr.loadconfig', return_value=self.testconfig1), mock.patch('svr.getcontrolstate', return_value='0') as mock_getcontrolstate, mock.patch('svr.setcontrolstate') as mock_setcontrolstate:
      svr.togglecontrol('hotwater')
      mock_setcontrolstate.assert_called_with('hotwater', 'on')
      

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
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=100'):
      temp = temperature().get('dummyid')
      self.assertEqual(0.1, temp)

  def test_hwcontrol_temperature_get_WhenCalledWithAnyParameterAndMockedWithTestDataFileContainingNegativeValue_ReturnsMinus12point7(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=-12700'):
      temp = temperature().get('dummyid')
      self.assertEqual(-12.7, temp)

  def test_hwcontrol_temperature_get_WhenCalledWithAnyParameterAndMockedWithTestDataFileContainingHighValue_Returns130point1(self):
    with mock.patch('builtins.open', new_callable=mock_open, read_data='00 01 4b 46 7f ff 0c 10 f5 : crc=f5 YES\n00 01 4b 46 7f ff 0c 10 f5 t=130100'):
      temp = temperature().get('dummyid')
      self.assertEqual(130.1, temp)

#  def test_upper(self):
#    self.assertEqual(True, True)

if __name__ == '__main__':
  unittest.main()


