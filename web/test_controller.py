import unittest
import mock
from mock import patch, call, mock_open

from controller import controller


class configunittests(unittest.TestCase):

    def test_reload_WhenCalledWithMockedFile_ReturnsInputDataAsStructure(self):
        with mock.patch('builtins.open', new_callable=mock_open, read_data='---\nconfig:\n  test: 123\ntempsensors:\n  test1:\n    host: 127.0.0.1\n    id: 28-000000000001\n    name: Test 1\ncontrols:\n  landinglight:\n    host: 192.168.1.12\n    controlpin: 21\n    name: Landing Light') as mocked_file, mock.patch('storage.redisclient.get', return_value=19) as mocked_redis:
            ctl = controller()
            ctl.reload()
            self.assertEqual(19, ctl.sensors['test1'].get())
            self.assertEqual(21, ctl.controls['landinglight'].controlpin)


if __name__ == '__main__':
    unittest.main()
