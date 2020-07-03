import unittest
from rtg.core.dispatcher import Dispatcher
from rtg.core.errors import UnreachableNetwork


class MyTestCase(unittest.TestCase):
    """
    These ants tests are based on an already-existing Dispatcher instance to simplify things.
    """

    def setUp(self) -> None:
        self.networks = {
            # Basic network configuration
            "basic": {
                'subnets': {
                    'A': "10.0.0.0/24",
                    'B': "192.168.0.0/24",
                    'C': "192.168.1.0/24",
                    'D': "10.0.1.0/24"
                },
                'routers': {
                    1: None,
                    2: None,
                    3: None,
                    4: True
                },
                'links': {
                    1: {
                        'B': None,
                        'C': None
                    },
                    2: {
                        "A": None,
                        "B": None
                    },
                    4: {'D': None},
                    3: {
                        "C": None,
                        "D": None
                    }
                },
                'expected_hops': {
                    (0, 1): [1],
                    (0, 2): [1, 0],
                    (0, 3): [1, 0, 2],
                    (1, 0): [1],
                    (1, 2): [0],
                    (1, 3): [0, 2],
                    (2, 0): [0, 1],
                    (2, 1): [0],
                    (2, 3): [2],
                    (3, 0): [2, 0, 1],
                    (3, 1): [2, 0],
                    (3, 2): [2]

                }
            },
            # Crashes because one network is unreachable
            "unreachable": {
                'subnets': {
                    'A': "10.0.0.0/24",
                    'B': "192.168.0.0/24",
                    'C': "192.168.1.0/24",
                    'D': "10.0.1.0/24"
                },
                'routers': {
                    1: None,
                    2: None,
                    3: None,
                    4: True
                },
                'links': {
                    1: {
                        'B': "192.168.0.26",
                        'C': "192.168.1.250"
                    },
                    2: {
                        "B": "192.168.0.253"
                    },
                    4: {'D': "10.0.1.254"},
                    3: {
                        "C": "192.168.1.253",
                        "D": "10.0.1.253"
                    }
                },
                'expected_hops': {
                    (0, 1): [1],
                    (0, 2): [1, 0],
                    (0, 3): [1, 0, 2],
                    (1, 0): [1],
                    (1, 2): [0],
                    (1, 3): [0, 2],
                    (2, 0): [0, 1],
                    (2, 1): [0],
                    (2, 3): [2],
                    (3, 0): [2, 0, 1],
                    (3, 1): [2, 0],
                    (3, 2): [2]

                }
            },
            "multiple_choices": {
                'subnets': {
                    'A': "10.0.1.0/24",
                    'B': "10.0.2.0/24",
                    'C': "10.0.3.0/24"
                },
                'routers': {
                    1: True,
                    2: None
                },
                'links': {
                    1: {"A": None},
                    2: {
                        "A": None,
                        "B": None,
                        "C": None
                    }
                },
                'expected_hops': {

                }
            }
        }

    def test_basic_hops(self):

        test = self.networks["basic"]
        inst = Dispatcher(debug=True)
        inst.execute(test['subnets'], test['routers'], test['links'])

        self.assertEqual(test['expected_hops'], inst.hops)

    def test_crash_unreachable_network(self):

        test = self.networks["unreachable"]
        inst = Dispatcher()

        self.assertRaises(UnreachableNetwork, lambda: inst.execute(test['subnets'], test['routers'], test['links']))

    def test_multiple_to_explore(self):

        test = self.networks["multiple_choices"]
        inst = Dispatcher(debug=True)
        inst.execute(test['subnets'], test['routers'], test['links'])

        self.assertEqual(test["expected_hops"], inst.hops)


if __name__ == '__main__':
    unittest.main()
