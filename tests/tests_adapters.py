import unittest
from rtg.adapters.json_adapter import JSONAdapter


class AdaptersTests(unittest.TestCase):

    def setUp(self) -> None:
        self.results = {
            1: {
                "192.168.0.0/24": "192.168.0.254",
                "192.168.1.0/24": "192.168.1.254",
                "10.0.0.0/24": "192.168.0.253",
                "10.0.1.0/24": "192.168.1.253",
                "0.0.0.0/0": "192.168.1.253"
            },
            2: {
                "192.168.0.0/24": "192.168.0.253",
                "10.0.0.0/24": "10.0.0.254",
                "0.0.0.0/0": "192.168.0.254",
                "192.168.1.0/24": "192.168.0.254",
                "10.0.1.0/24": "192.168.0.254"
            },
            3: {
                "192.168.1.0/24": "192.168.1.253",
                "10.0.1.0/24": "10.0.1.253",
                "0.0.0.0/0": "10.0.1.254",
                "192.168.0.0/24": "192.168.1.254",
                "10.0.0.0/24": "192.168.1.254"
            },
            4: {
                "10.0.1.0/24": "10.0.1.254",
                "0.0.0.0/0": "10.0.1.254",
                "192.168.0.0/24": "10.0.1.253",
                "192.168.1.0/24": "10.0.1.253",
                "10.0.0.0/24": "10.0.1.253"
            }
        }

    def test_json_adapter(self):
        inst = JSONAdapter(file_path="files/test.json")
        dispatcher = inst.evaluate()

        result = dispatcher.formatted_raw_routing_tables

        for router in self.results:
            res = result[str(router)]
            expected = self.results[router]

            self.assertEqual(expected, res, f'JSON : Table : router {router}')


if __name__ == '__main__':
    unittest.main()
