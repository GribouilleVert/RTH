import unittest
from rth.virtual_building.network_creator import NetworkCreator
from rth.core.errors import NameAlreadyExists, OverlappingError
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
        self.assertEqual({}, net.routers, msg="Network connected routers")

    def test_verify_lone_router(self):
        i = NetworkCreator()
        i.create_router(True)

        r = i.routers[0]

        self.assertEqual(0, r.uid, msg="Router UID")
        self.assertEqual("<Untitled Router#ID:0>", r.name, msg="Router name")

        self.assertEqual(True, r.internet, msg="Router internet connection")
        self.assertEqual({}, r.connected_networks, msg="Router connected networks")

    #
    # Name
    #
    def test_name_networks(self):
        i = NetworkCreator()

        i.create_network('192.168.1.0', 24, name="My network")
        self.assertEqual("My network", i.subnetworks[0]['instance'].name, msg="First network name")

        # everything should go fine here, name is different
        i.create_network('192.168.2.0', 24, name="My second network")
        self.assertEqual("My second network", i.subnetworks[1]['instance'].name, msg="Second network name")

        # this one should raise a NameAleadyExists exception
        self.assertRaises(NameAlreadyExists, lambda: i.create_network('192.168.3.0', 24, name="My network"))

        # final check to see both names have been registered
        self.assertEqual(['My network', 'My second network'], i.subnets_names, msg="Global network names list")

        self.assertEqual(1, i.name_to_uid('subnet', "My second network"))
        self.assertEqual("My network", i.uid_to_name('subnet', 0))

    def test_name_routers(self):
        i = NetworkCreator()

        i.create_router(False, name="My router")
        self.assertEqual("My router", i.routers[0].name, msg="First router name")

        # everything should go fine here, name is different
        i.create_router(False, name="My second router")
        self.assertEqual("My second router", i.routers[1].name, msg="Second router name")

        # this one should raise a NameAleadyExists exception
        self.assertRaises(NameAlreadyExists, lambda: i.create_router(False, name="My router"))

        # final check of the global router names list
        self.assertEqual(['My router', 'My second router'], i.routers_names, msg="Global router names list")

        self.assertEqual(1, i.name_to_uid('router', "My second router"))
        self.assertEqual("My router", i.uid_to_name('router', 0))

    #
    # Make it crash!
    #
    def test_network_overlap(self):
        i = NetworkCreator()
        i.create_network('10.5.1.0', 24)

        # Same CIDR
        self.assertRaises(OverlappingError, lambda: i.create_network('10.5.1.0', 24))

        # Smaller mask
        self.assertRaises(OverlappingError, lambda: i.create_network('10.5.1.128', 28))

        # Bigger mask
        self.assertRaises(OverlappingError, lambda: i.create_network('10.0.0.0', 8))
        self.assertRaises(OverlappingError, lambda: i.create_network('10.5.0.0', 16))
        self.assertRaises(OverlappingError, lambda: i.create_network('10.5.1.0', 19))

    def test_master_router_multiple_connections(self):
        i = NetworkCreator()
        network_1_id = i.create_network("10.5.1.0", 24)
        master_router_id = i.create_router(True)
        network_2_id = i.create_network("10.5.2.0", 24)

        # Should raise an exception because at the current state of the RTG, only one subnetwork is allowed to connect
        # to the master router (the one having the internet connection). This will be changed later on.
        self.assertRaises(Exception,
                          lambda: i.connect_router_to_networks(
                              i.uid_to_name("router", master_router_id),
                              {
                                  i.uid_to_name("subnet", network_1_id): None,
                                  i.uid_to_name("subnet", network_2_id): None
                              }
                          )
                          )


if __name__ == '__main__':
    unittest.main()
