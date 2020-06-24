from rtg.virtual_building.network_creator import NetworkCreator
from rtg.virtual_building.ants import AntsDiscovery
from rtg.virtual_building.routing_tables_generator import RoutingTablesGenerator
from .errors import WronglyFormedSubnetworksData, WronglyFormedRoutersData, WronglyFormedLinksData
from nettools.utils.ip_class import FourBytesLiteral


class Dispatcher:
    """
    This is the dispatcher class. Which everything comes from and where everything goes.
    We could call that a hub, I call that a good way to handle a complex program.

    If you want to provide raw data to this class, here are some explanations about how they are formed.
        Subnetworks: a dictionary of form {name: CIDR}
            ex: {
                    "A": "10.0.0.0/24",
                    'B': "192.168.0.0/24"
                }
        Routers: a dictionary of form {name: connection}
            connection is either None/False or True. Only one router per network is allowed to have an internet
            connection for now.
            ex: {
                    "1": None,
                    "2": None,
                    "3": None,
                    "4": True
                }
        Links: this one is more complicated. It is a dictionary of dictionaries of form {router_name: list_of_subnets}
            the list is a dictionary itself, with the name of the subnetwork as a key and either an IP of said
            subnetwork or None as a value (setting it to None tells RTG to assign the first free IP starting from the
            broadcast address of said subnetwork).
            ex: {
                    "1": {
                        'B': None,
                        'C': None
                    },
                    "2": {
                        "A": None,
                        "B": None
                    },
                    "4": {'D': None},
                    "3": {
                        "C": None,
                        "D": None
                    }
                }
            second ex: {
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
                }
    """

    __virtual_network_instance = None

    subnetworks, routers, links = None, None, None
    equitemporality = None

    gend_subnetworks, gend_routers, gend_routers_names = None, None, None
    hops = None
    routing_tables = None
    formatted_raw_routing_tables = None

    #
    # DUNDERS
    #
    def __init__(self):
        self.__virtual_network_instance = NetworkCreator()

    #
    # Class execution flow
    #
    def execute(self, subnetworks, routers, links, equitemporality=True):
        self.subnetworks = subnetworks
        self.routers = routers
        self.links = links
        self.equitemporality = equitemporality

        self.__flow()

    def __flow(self):
        self.__checks()
        self.__build_virtual_network()
        self.__discover_hops()
        self.__calculate_routing_tables()

        self.finished = True

    #
    # Perform all checks about data passed here
    #
    def __checks(self):
        # Subnetworks checks
        s = self.subnetworks
        if not isinstance(s, dict):
            raise WronglyFormedSubnetworksData()
        for name in s:
            v = s[name]
            try:
                ip, _ = v.split("/")
                FourBytesLiteral().set_from_string_literal(ip)
            except:
                raise WronglyFormedSubnetworksData()

        r = self.routers
        if not isinstance(r, dict):
            raise WronglyFormedRoutersData()
        for name in r:
            if r[name] is not None and not isinstance(r[name], bool):
                raise WronglyFormedRoutersData()

        li = self.links
        if not isinstance(li, dict):
            raise WronglyFormedLinksData()
        for rid in li:
            if not isinstance(li[rid], dict):
                raise WronglyFormedLinksData()
            for subnet in li[rid]:
                if not isinstance(li[rid][subnet], str) and li[rid][subnet] is not None:
                    raise WronglyFormedLinksData()

    #
    # Network Creator
    #
    def __build_virtual_network(self):

        inst = self.__virtual_network_instance

        # Create subnets
        for name in self.subnetworks:
            ip, mask = self.subnetworks[name].split('/')
            inst.create_network(ip, int(mask), str(name))

        # Create routers
        for name in self.routers:
            if self.routers[name]:
                inst.create_router(name=str(name), internet_connection=True)
            else:
                inst.create_router(name=str(name))

        # Link both
        for router_name in self.links:
            inst.connect_router_to_networks(router_name, self.links[router_name])

        self.gend_subnetworks = inst.subnetworks
        self.gend_routers = inst.routers
        self.gend_routers_names = inst.routers_names

    def network_raw_output(self):
        return self.__virtual_network_instance.network_raw_output()

    #
    # Ants Discovery
    #
    def __discover_hops(self):

        ants_inst = AntsDiscovery(self.gend_subnetworks, self.gend_routers, self.equitemporality)

        ants_inst.sweep_network()
        ants_inst.calculate_hops()

        self.links = ants_inst.links
        self.hops = ants_inst.hops

    #
    # Routing Tables Generator
    #
    def __calculate_routing_tables(self, raw=True):
        """
        This is the main function.
            It will pass the low-level processing (discovering the links that are virtually created by the program)
        to the virtual_building category.
            Its objective is also to handle the different parameters in order to pass certain unit tests.

        :param raw: boolean for whether the results are given in a table or in raw python dict format
        :return: returns final result if raw is True, else displays it.
            In further versions, the raw option should disappear to leave room for more useful things.
            The results, sent to another process, won't need to be displayed anymore, so raw will be implied.
        """

        if not self.links or self.hops:
            self.__discover_hops()

        rtg_inst = RoutingTablesGenerator(self.gend_subnetworks, self.gend_routers,
                                          self.links, self.hops, self.equitemporality)

        # getting routing tables
        routing_tables = []
        for i in range(len(self.routers)):
            routing_tables.append(rtg_inst.get_routing_table(i))

        self.routing_tables = routing_tables

        # formatting them to be displayed
        if raw is True:
            final = {}
            for i in range(len(self.routers)):
                name = self.gend_routers_names[i]
                final[name] = routing_tables[i]
            self.formatted_raw_routing_tables = final
        else:
            for i in range(len(self.routers)):
                print(f"Router {i}")
                print("---------------")

                for j in range(len(routing_tables[i])):
                    subnet = list(routing_tables[i].keys())[j]
                    subnet += ''.join([' ' for _ in range(18 - len(subnet))])
                    ip = list(routing_tables[i].values())[j]
                    print(f"{subnet}: {ip}")
                print()
