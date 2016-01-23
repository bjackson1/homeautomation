import unittest
import mock
from mock import patch, call, mock_open

from config import config


class configunittests(unittest.TestCase):

    def test_get_WhenCalledWithMockedFile_ReturnsInputDataAsStructure(self):
        with mock.patch('builtins.open', new_callable=mock_open, read_data='---\nconfig:\n  test: 123\n') as mocked_file:
            cfg = config().get()
            self.assertEqual(123, cfg['config']['test'])


if __name__ == '__main__':
    unittest.main()
