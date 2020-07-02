from nettools.core.ipv4_network import IPv4Network
from nettools.utils.ip_class import FourBytesLiteral
from nettools.utils.utils import Utils
from nettools.utils.errors import IPOffNetworkRangeException

from rtg.core.errors import *


class NetworkCreator:
    """
    This class is the virtual environment which contains everything for the program to run.

    This is the base everything is built on.

    The Network class is the virtual network existing in this environment.
    The Router class is the virtual router existing in this environment.

    WARNING: Every link is supposed virtual, and is actually not an instance of any type. Links will be
        considered and discovered by the Ants system.
        Neither the Network or the Router class stock instances of "links", and only the master program
        can process and understand these connections.

    :ivar subnetworks: Format: {uid => {"instance": instance, "range": network_range}, ...}
    :ivar routers: Format: {uid => instance, ...}

    :ivar subnets_names: Used solely for checking if the name already exists, so under list format.
    :ivar routers_names: Used solely for checking if the name already exists, so under list format.

    :ivar ranges: Networks ranges. Format: [{'start': start, 'end': end}, ...}
    :ivar equitemporality: Boolean variable to set equitemporality to True or False. If set to false,
        a post-calculus will be executed to choose the fastest route instead of the smallest one.
    """

    subnetworks, routers = None, None
    subnets_names, routers_names = None, None
    ranges = None
    equitemporality = None

    #
    # DUNDERS
    #
    def __init__(self, equitemporality=True):
        self.equitemporality = equitemporality

        self.subnetworks, self.routers = {}, {}
        self.subnets_names, self.routers_names = [], []
        self.ranges = []

    #
    # CLASSES
    #
    class Network:
        """
        This class stands for the virtual network in the environment created for the calculus

        The class can stock informations about the routers connected to it.

        :ivar routers: The dict of the connected routers. Format: [{'uid': router_uid, 'ip': router_ip}, ...]
        """

        network_range, addresses, mask_length = {}, 0, 0
        routers = None
        uid, name = -1, None

        def __init__(self, starting_ip, mask, uid, name=None):

            inst_ = IPv4Network().init_from_couple(starting_ip, mask)

            self.uid = uid
            self.name = name if name else None
            self.cidr = f"{starting_ip}/{inst_.mask_length}"

            self.routers = []

            self.network_range = inst_.network_range
            self.mask_length = inst_.mask_length
            self.addresses = inst_.addresses

        def connect(self, router_uid, router_ip):
            self.routers.append({'uid': router_uid, 'ip': router_ip})

        def disconnect(self, router_uid):
            for i in range(len(self.routers)):
                if self.routers[i]['uid'] == router_uid:
                    del self.routers[i]

    class Router:
        """
        This class is a virtual representation of a router, in the environment of calculus setup here

        This class can stock informations on the subnets it is connected to.

        :ivar connected_networks: The dict of the connected subnets. Format: [{'uid': net_uid, 'ip': router_ip}, ...]
        """

        uid, name = -1, None
        connected_networks, internet = None, False

        def __init__(self, uid, internet=False, name=None, delay=None):
            self.uid = uid
            self.name = name if name else None
            self.internet = internet
            if not NetworkCreator.equitemporality and delay:
                raise NoDelayAllowed()
            else:
                self.delay = delay
            self.connected_networks = []

        def connect(self, subnet_uid, router_ip):
            if self.internet and self.connected_networks:
                raise Exception('Master router cannot accept more than one connection')

            self.connected_networks.append({'uid': subnet_uid, 'ip': router_ip})

        def disconnect(self, subnet_uid):
            for i in range(len(self.connected_networks)):
                if self.connected_networks[i]['uid'] == subnet_uid:
                    del self.connected_networks[i]

    #
    # Converters
    #
    def name_to_uid(self, cat, name):
        list_ = self.subnets_names if cat == 'subnet' else self.routers_names
        id_ = 0

        for i in range(len(list_)):
            if list_[i] == str(name):
                id_ = i
                break

        return id_

    def uid_to_name(self, cat, uid):
        name_ = 0

        if cat == 'subnet':
            for id_ in self.subnetworks:
                if id_ == uid:
                    name_ = self.subnetworks[id_]['instance'].name
                    break
        else:
            for id_ in self.routers:
                if id_ == uid:
                    name_ = self.routers[id_].name
                    break

        return str(name_)

    #
    # Testers
    #
    def is_name_existing(self, type_, name):
        list_ = self.subnets_names if type_ == 'subnet' else self.routers_names
        return name in list_

    def router_has_internet_connection(self, router_uid):
        return self.routers[router_uid].internet

    #
    # Creators
    #
    def create_network(self, ip, mask_length, name=None):
        """
        Function used to create a virtual network using Network class

        :param ip:
        :param mask_length:
        :param name: The possible name of the network
        :return uid: the uid of the newly created network
        """

        uid = len(self.subnetworks)

        # Name correspondency
        if name:
            result = self.is_name_existing('subnet', name)
            if result:
                raise NameAlreadyExists(name)
        else:
            name = f"<Untitled Network#ID:{uid}>"

        if self.ranges:
            # we check for starting ip
            for range_ in self.ranges:
                result = Utils.ip_in_range(range_, ip)
                if result:
                    raise OverlappingError('start', range_, ip, mask_length)

            inst_ = self.Network(ip, mask_length, uid, name)
            self.subnetworks[uid] = {'instance': inst_, 'range': inst_.network_range}

            # then we check last ip of range to check nothing is overlapping
            for range_ in self.ranges:
                result = Utils.ip_in_range(range_, inst_.network_range['end'])
                if result:
                    raise OverlappingError('end', range_, Utils.netr_to_literal(inst_.network_range))
        else:
            inst_ = self.Network(ip, mask_length, uid, name)
            self.subnetworks[uid] = {'instance': inst_, 'range': inst_.network_range}

        # adding to network ranges
        self.ranges.append(inst_.network_range)
        # also adding name if defined
        if name:
            self.subnets_names.append(name)

        return uid

    def create_router(self, internet_connection=False, name=None):
        """
        Function used to create a virtual Router by using its class

        :param internet_connection: boolean for whether the router is a connexion to the outer world (internet)
        :param name: The eventual name of the router
        :return uid: The uid of the newly created router
        """

        uid = len(self.routers)

        if name:
            result = self.is_name_existing('router', name)
            if result:
                raise NameAlreadyExists(name)
        else:
            name = f"<Untitled Router#ID:{uid}>"

        inst_ = self.Router(uid, internet_connection, name)

        self.routers_names.append(name)

        self.routers[uid] = inst_

        return uid

    #
    # Executers
    #
    def connect_router_to_networks(self, router_name, subnets_ips):
        """
        Connects router to given subnets

        :param router_name: the name of the router, will be converted to its internal uid for processing
        :param subnets_ips: the ip that will take the router for each network it is going to connect to
            format: {network_name => new_router_ip, ...}
        """

        def check_ip_availability(subnet_inst_, ip_):
            """
            This function is a suicider: it will die if any of the tests fail

            :param subnet_inst_: the subnet instance
            :param ip_: the ip that has to be checked
            :raise:
                NetworkUtilities.core.errors.IPOffNetworkRangeException
                or
                rtg.core.errors.IPAlreadyAttributed
            """

            # Checking that ip is effectively in range of the subnet
            if isinstance(ip_, str):
                ip_ = FourBytesLiteral().set_from_string_literal(ip_)

            mask = FourBytesLiteral().set_from_string_literal(Utils.mask_length_to_literal(subnet_inst_.mask_length))
            inst = IPv4Network().init_from_fbl(ip_, mask)

            if inst.address_type != 1:
                # means the address is either a network or a broadcast address
                raise IPOffNetworkRangeException(str(ip))

            # then we check that ip is not used by any of the current routers
            routers = subnet_inst_.routers
            for r in routers:
                if str(r['ip']) == str(ip_):
                    raise IPAlreadyAttributed(name, ip_, self.uid_to_name('router', r['uid']), str(router_name))

        router_uid = self.name_to_uid('router', router_name)

        for name in subnets_ips:
            subnet_uid = self.name_to_uid('subnet', name)
            subnet_inst = self.subnetworks[subnet_uid]['instance']
            router_inst = self.routers[router_uid]

            subnet_ip = subnets_ips[name]

            # we want to attribute a "personalised" IP
            if subnet_ip:
                check_ip_availability(subnet_inst, subnet_ip)
                ip = subnet_ip
            # we will let the program set it for us
            else:

                ip = subnet_inst.network_range['end']
                while True:
                    ip = Utils.ip_before(ip)
                    try:
                        check_ip_availability(subnet_inst, ip)
                        break
                    except IPAlreadyAttributed:
                        continue

            subnet_inst.connect(router_uid, ip)
            router_inst.connect(subnet_uid, ip)

            self.subnetworks[subnet_uid]['instance'] = subnet_inst
            self.routers[router_uid] = router_inst

    #
    # Displayers
    #
    def display_network(self):
        for i in self.subnetworks:
            inst = self.subnetworks[i]['instance']

            print(
                f"Network {inst.network_range['start']} - {inst.network_range['end']}"
                f"  ID: {inst.uid}"
                f"  Name: {inst.name if inst.name else '<unnamed>'}"
                "\n"
            )

    def network_raw_output(self):
        final = {'subnets': {}, 'routers': {}}

        for sid in self.subnetworks:
            subnet = self.subnetworks[sid]['instance']

            displayable_connected_routers = subnet.routers.copy()
            for i in range(len(displayable_connected_routers)):
                displayable_connected_routers[i] = {
                    'uid': displayable_connected_routers[i]['uid'],
                    'ip': str(displayable_connected_routers[i]['ip'])
                }
            
            final['subnets'][sid] = {
                'id': subnet.uid,
                'name': subnet.name,
                'connected_routers': displayable_connected_routers,
                'range': Utils.netr_to_literal(subnet.network_range),
                'mask': subnet.mask_length
            }
            
        for rid in self.routers:
            router = self.routers[rid]

            displayable_connected_subnets = router.connected_networks.copy()
            for i in range(len(displayable_connected_subnets)):
                displayable_connected_subnets[i] = {
                    'uid': displayable_connected_subnets[i]['uid'],
                    'ip': str(displayable_connected_subnets[i]['ip'])
                }
            
            final['routers'][rid] = {
                'id': router.uid,
                'name': router.name,
                'connected_subnets': displayable_connected_subnets,
                'internet': router.internet
            }

        return final
