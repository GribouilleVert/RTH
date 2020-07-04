import unittest
from rtg.core.dispatcher import Dispatcher
from rtg.core.errors import UnreachableNetwork
import unittest.mock as m


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
            # Expected to crash because one network is unreachable
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
            # When ants encounter two network possibilities
            "multiple_choices_networks": {
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
                    (0, 1): [1],
                    (0, 2): [1],
                    (1, 0): [1],
                    (1, 2): [1],
                    (2, 0): [1],
                    (2, 1): [1]
                }
            },
            # When ants encounter two router possibilites
            "multiple_choices_routers": {
                'subnets': {
                    'A': "10.0.1.0/24",
                    'B': "10.0.2.0/24",
                    'C': "10.0.3.0/24"
                },
                'routers': {
                    1: True,
                    2: None,
                    3: None
                },
                'links': {
                    1: {"A": None},
                    2: {
                        "A": None,
                        "B": None
                    },
                    3: {
                        "A": None,
                        "C": None
                    }
                },
                'expected_hops': {
                    (0, 1): [1],
                    (0, 2): [2],
                    (1, 0): [1],
                    (1, 2): [1, 2],
                    (2, 0): [2],
                    (2, 1): [2, 1]
                }
            },
            # Now we test the ability of the ants to evaluate the fastest route of hops
            "multiple_paths": {
                'subnets': {
                    'A': "10.0.1.0/24",
                    'B': "10.0.2.0/24",
                    'C': "10.0.3.0/24"
                },
                'routers': {
                    0: True,
                    1: None,
                    2: None,
                    3: None
                },
                'links': {
                    0: {"A": None},
                    1: {
                        "A": None,
                        "C": None
                    },
                    2: {
                        "A": None,
                        "B": None
                    },
                    3: {
                        "B": None,
                        "C": None
                    }
                },
                'expected_hops': {
                    (0, 1): [2],
                    (0, 2): [1],
                    (1, 0): [2],
                    (1, 2): [3],
                    (2, 0): [1],
                    (2, 1): [3]
                }
            }
        }

    def prepare_run(self, dict_entry, debug=False):

        test = self.networks[dict_entry]
        inst = Dispatcher(debug=debug)
        inst.execute(test['subnets'], test['routers'], test['links'])

        return test["expected_hops"], inst.hops

    #
    # Basic test
    #
    def test_basic_hops(self):

        e, a = self.prepare_run("basic")
        self.assertEqual(e, a)

    #
    # Unreachable upon sweep
    #
    def test_crash_unreachable_network(self):

        self.assertRaises(UnreachableNetwork, lambda: self.prepare_run("unreachable"))

    #
    # Multiple choices to explore
    #
    def test_multiple_networks_to_explore(self):

        e, a = self.prepare_run("multiple_choices_networks")
        self.assertEqual(e, a)

    def test_multiple_routers_to_explore(self):

        e, a = self.prepare_run("multiple_choices_routers")
        self.assertEqual(e, a)

    def test_multiple_paths(self):

        e, a = self.prepare_run("multiple_paths")
        self.assertEqual(e, a)

    @m.patch("builtins.print")
    def test_multiple_to_explore_mocked_debug(self, _):

        # Those printed lines are supposed to be debug things, so we don't try and test them for it shouldn't be enabled
        # in production.

        test = self.networks["multiple_choices_networks"]
        inst = Dispatcher(debug=True)
        inst.execute(test['subnets'], test['routers'], test['links'])
        self.assertEqual(test["expected_hops"], inst.hops)

        test = self.networks["multiple_choices_routers"]
        inst = Dispatcher(debug=True)
        inst.execute(test['subnets'], test['routers'], test['links'])
        self.assertEqual(test["expected_hops"], inst.hops)


if __name__ == '__main__':
    unittest.main()
