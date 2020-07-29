import unittest
from rth.core.dispatcher import Dispatcher


class ProcessTests(unittest.TestCase):

    def setUp(self) -> None:

        self.debug_print = False

        self.networks = {
            # Basic network configuration
            1: {
                'name': "Basic",
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
                'instance': None,
                'expected_network': {
                    'subnets': {
                        0: {
                            'id': 0,
                            'name': 'A',
                            'connected_routers': {1: '10.0.0.254'},
                            'range': {'start': '10.0.0.0', 'end': '10.0.0.255'},
                            'mask': 24
                        },
                        1: {
                            'id': 1,
                            'name': 'B',
                            'connected_routers': {0: '192.168.0.254', 1: '192.168.0.253'},
                            'range': {'start': '192.168.0.0', 'end': '192.168.0.255'},
                            'mask': 24
                        },
                        2: {
                            'id': 2,
                            'name': 'C',
                            'connected_routers': {0: '192.168.1.254', 2: '192.168.1.253'},
                            'range': {'start': '192.168.1.0', 'end': '192.168.1.255'},
                            'mask': 24
                        },
                        3: {
                            'id': 3,
                            'name': 'D',
                            'connected_routers': {3: '10.0.1.254', 2: '10.0.1.253'},
                            'range': {'start': '10.0.1.0', 'end': '10.0.1.255'},
                            'mask': 24
                        }
                    },
                    'routers': {
                        0: {
                            'id': 0,
                            'name': '1',
                            'connected_subnets': {1: '192.168.0.254', 2: '192.168.1.254'},
                            'internet': False
                        },
                        1: {
                            'id': 1,
                            'name': '2',
                            'connected_subnets': {0: '10.0.0.254', 1: '192.168.0.253'},
                            'internet': False
                        },
                        2: {
                            'id': 2,
                            'name': '3',
                            'connected_subnets': {2: '192.168.1.253', 3: '10.0.1.253'},
                            'internet': False
                        },
                        3: {
                            'id': 3,
                            'name': '4',
                            'connected_subnets': {3: '10.0.1.254'},
                            'internet': True
                        }
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

                },
                'expected_result': {
                    1: {
                        "192.168.0.0/24": {'gateway': '192.168.0.254', 'interface': '192.168.0.254'},
                        "192.168.1.0/24": {'gateway': '192.168.1.254', 'interface': '192.168.1.254'},
                        "10.0.0.0/24": {'gateway': '192.168.0.253', 'interface': '192.168.0.254'},
                        "10.0.1.0/24": {'gateway': '192.168.1.253', 'interface': '192.168.1.254'},
                        "0.0.0.0/0": {'gateway': '192.168.1.253', 'interface': '192.168.1.254'}
                    },
                    2: {
                        "192.168.0.0/24": {'gateway': '192.168.0.253', 'interface': '192.168.0.253'},
                        "10.0.0.0/24": {'gateway': '10.0.0.254', 'interface': '10.0.0.254'},
                        "0.0.0.0/0": {'gateway': '192.168.0.254', 'interface': '192.168.0.253'},
                        "192.168.1.0/24": {'gateway': '192.168.0.254', 'interface': '192.168.0.253'},
                        "10.0.1.0/24": {'gateway': '192.168.0.254', 'interface': '192.168.0.253'}
                    },
                    3: {
                        "192.168.1.0/24": {'gateway': '192.168.1.253', 'interface': '192.168.1.253'},
                        "10.0.1.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.253'},
                        "0.0.0.0/0": {'gateway': '10.0.1.254', 'interface': '10.0.1.253'},
                        "192.168.0.0/24": {'gateway': '192.168.1.254', 'interface': '192.168.1.253'},
                        "10.0.0.0/24": {'gateway': '192.168.1.254', 'interface': '192.168.1.253'}
                    },
                    4: {
                        "10.0.1.0/24": {'gateway': '10.0.1.254', 'interface': '10.0.1.254'},
                        "0.0.0.0/0": {'gateway': '10.0.1.254', 'interface': '10.0.1.254'},
                        "192.168.0.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'},
                        "192.168.1.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'},
                        "10.0.0.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'}
                    }
                }
            },
            # Now with personalised IPs to routers
            2: {
                'name': "Personalised IPs",
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
                        "A": "10.0.0.45",
                        "B": "192.168.0.253"
                    },
                    4: {'D': "10.0.1.254"},
                    3: {
                        "C": "192.168.1.253",
                        "D": "10.0.1.253"
                    }
                },
                'instance': None,
                'expected_network': {
                    'subnets': {
                        0: {
                            'id': 0,
                            'name': 'A',
                            'connected_routers': {1: '10.0.0.45'},
                            'range': {'start': '10.0.0.0', 'end': '10.0.0.255'},
                            'mask': 24
                        },
                        1: {
                            'id': 1,
                            'name': 'B',
                            'connected_routers': {0: '192.168.0.26', 1: '192.168.0.253'},
                            'range': {'start': '192.168.0.0', 'end': '192.168.0.255'},
                            'mask': 24
                        },
                        2: {
                            'id': 2,
                            'name': 'C',
                            'connected_routers': {0: '192.168.1.250', 2: '192.168.1.253'},
                            'range': {'start': '192.168.1.0', 'end': '192.168.1.255'},
                            'mask': 24
                        },
                        3: {
                            'id': 3,
                            'name': 'D',
                            'connected_routers': {3: '10.0.1.254', 2: '10.0.1.253'},
                            'range': {'start': '10.0.1.0', 'end': '10.0.1.255'},
                            'mask': 24
                        }
                    },
                    'routers': {
                        0: {
                            'id': 0,
                            'name': '1',
                            'connected_subnets': {1: '192.168.0.26', 2: '192.168.1.250'},
                            'internet': False
                        },
                        1: {
                            'id': 1,
                            'name': '2',
                            'connected_subnets': {0: '10.0.0.45', 1: '192.168.0.253'},
                            'internet': False
                        },
                        2: {
                            'id': 2,
                            'name': '3',
                            'connected_subnets': {2: '192.168.1.253', 3: '10.0.1.253'},
                            'internet': False
                        },
                        3: {
                            'id': 3,
                            'name': '4',
                            'connected_subnets': {3: '10.0.1.254'},
                            'internet': True
                        }
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

                },
                'expected_result': {
                    1: {
                        "192.168.0.0/24": {'gateway': '192.168.0.26', 'interface': '192.168.0.26'},
                        "192.168.1.0/24": {'gateway': '192.168.1.250', 'interface': '192.168.1.250'},
                        "10.0.0.0/24": {'gateway': '192.168.0.253', 'interface': '192.168.0.26'},
                        "10.0.1.0/24": {'gateway': '192.168.1.253', 'interface': '192.168.1.250'},
                        "0.0.0.0/0": {'gateway': '192.168.1.253', 'interface': '192.168.1.250'}
                    },
                    2: {
                        "192.168.0.0/24": {'gateway': '192.168.0.253', 'interface': '192.168.0.253'},
                        "10.0.0.0/24": {'gateway': '10.0.0.45', 'interface': '10.0.0.45'},
                        "0.0.0.0/0": {'gateway': '192.168.0.26', 'interface': '192.168.0.253'},
                        "192.168.1.0/24": {'gateway': '192.168.0.26', 'interface': '192.168.0.253'},
                        "10.0.1.0/24": {'gateway': '192.168.0.26', 'interface': '192.168.0.253'}
                    },
                    3: {
                        "192.168.1.0/24": {'gateway': '192.168.1.253', 'interface': '192.168.1.253'},
                        "10.0.1.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.253'},
                        "0.0.0.0/0": {'gateway': '10.0.1.254', 'interface': '10.0.1.253'},
                        "192.168.0.0/24": {'gateway': '192.168.1.250', 'interface': '192.168.1.253'},
                        "10.0.0.0/24": {'gateway': '192.168.1.250', 'interface': '192.168.1.253'}
                    },
                    4: {
                        "10.0.1.0/24": {'gateway': '10.0.1.254', 'interface': '10.0.1.254'},
                        "0.0.0.0/0": {'gateway': '10.0.1.254', 'interface': '10.0.1.254'},
                        "192.168.0.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'},
                        "192.168.1.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'},
                        "10.0.0.0/24": {'gateway': '10.0.1.253', 'interface': '10.0.1.254'}
                    }
                }
            }
        }

        for nid in self.networks:
            net = self.networks[nid]
            inst = Dispatcher()
            inst.execute(net['subnets'], net['routers'], net['links'])
            self.networks[nid]['instance'] = inst

    def test_1_network_check(self):
        if self.debug_print:
            print(f"Configuration [network]")

        for number in self.networks:
            n = self.networks[number]
            inst = n['instance']

            result = inst.network_raw_output()

            # testing hops
            self.assertEqual(n['expected_network'], result, f'{n["name"]} : Network')
            if self.debug_print:
                print(f'Passed : {n["name"]}')

    def test_2_hops(self):
        if self.debug_print:
            print(f"\n\nConfiguration [hops]")

        for number in self.networks:
            n = self.networks[number]
            inst = n['instance']

            hops = inst.hops

            # testing hops
            for matrix in n['expected_hops']:
                expected = n['expected_hops'][matrix]
                res = hops[matrix]

                self.assertEqual(expected, res, f'{n["name"]} : Ants : tuple {matrix}')

            if self.debug_print:
                print(f"Passed : {n['name']}")

    def test_3_routing_tables(self):
        if self.debug_print:
            print(f"\n\nConfiguration [table]")

        for number in self.networks:

            n = self.networks[number]
            inst = n['instance']

            # grab the result
            result = inst.formatted_raw_routing_tables

            for router in n['expected_result']:
                res = result[str(router)]
                expected = n['expected_result'][router]

                self.assertEqual(expected, res, f'{n["name"]} : Table : router {router}')

            if self.debug_print:
                print(f'Passed {n["name"]}')


if __name__ == '__main__':
    unittest.main()
