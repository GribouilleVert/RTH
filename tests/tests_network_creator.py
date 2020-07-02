import unittest
from rtg.virtual_building.network_creator import NetworkCreator
from nettools.utils.ip_class import FourBytesLiteral
from nettools.utils.utils import Utils


class NetworkCreatorTests(unittest.TestCase):

    #
    # Create
    #
    def test_create_network(self):
        i = NetworkCreator()
        i.create_network('192.168.1.0', 24)

        # also test for alternate option using mask literal
        NetworkCreator().create_network('192.168.1.0', '255.255.255.0')
        # it is not meant to be verified, just crash if it is not handled properly

        s = i.subnetworks

        self.assertEqual(1, len(s))
        self.assertIsInstance(s[0]['instance'], NetworkCreator.Network, msg="Instance is a Network")
        self.assertIsInstance(s[0]['range'], dict, msg="Range is dict")
        self.assertIsInstance(s[0]['range']['start'], FourBytesLiteral, msg="Range start is a FBL")
        self.assertIsInstance(s[0]['range']['end'], FourBytesLiteral, msg="Range end is a FBL")

    def test_create_router(self):
        i = NetworkCreator()
        i.create_router(True)

        r = i.routers

        self.assertEqual(1, len(r))
        self.assertIsInstance(r[0], NetworkCreator.Router)

    #
    # Verify
    #
    def test_verify_lone_network(self):
        i = NetworkCreator()
        i.create_network('192.168.1.0', 24)

        net = i.subnetworks[0]['instance']

        # Basic info
        self.assertEqual(0, net.uid, msg="Network UID")
        self.assertEqual("<Untitled Network#ID:0>", net.name, msg="Network name")

        # Virtual net info
        self.assertEqual(254, net.addresses, msg="Network available addresses")
        self.assertEqual({"start": "192.168.1.0", "end": "192.168.1.255"}, Utils.netr_to_literal(net.network_range),
                         msg="Network range")
        self.assertEqual(24, net.mask_length, msg="Network mask length")

    def test_verify_lone_router(self):
        i = NetworkCreator()
        i.create_router(True)

        r = i.routers[0]

        self.assertEqual(0, r.uid, msg="Router UID")
        self.assertEqual("<Untitled Router#ID:0>", r.name, msg="Router name")
        self.assertEqual(True, r.internet, msg="Router internet connection")
