from rth.virtual_building.network_creator import NetworkCreator
from rth.virtual_building.ants import AntsDiscovery
from rth.virtual_building.routing_tables_generator import RoutingTablesGenerator
from .errors import WronglyFormedSubnetworksData, WronglyFormedRoutersData, WronglyFormedLinksData
from nettools.utils.ip_class import FourBytesLiteral


class Dispatcher:
    """
    This is the dispatcher class. Which everything comes from and where everything goes.
    We could call that a hub, I call that a good way to handle a complex program.
    """

    __virtual_network_instance = None
    __executed = None

    subnetworks, routers, links = None, None, None
    equitemporality = None

    gend_subnetworks, gend_routers, gend_routers_names = None, None, None
    hops = None
    routing_tables = None
    formatted_raw_routing_tables = None

    #
    # DUNDERS
    #
    def __init__(self, debug=False):
        self.__virtual_network_instance = NetworkCreator()
        self.debug = debug
        self.__executed = False

    #
    # Class execution flow
    #
    def execute(self, subnetworks, routers, links, equitemporality=True):
        self.subnetworks = subnetworks
        self.routers = routers
        self.links = links

        self.equitemporality = equitemporality
        self.__flow()
        self.__executed = True

    def __flow(self):
        self.__checks()
        self.__build_virtual_network()
        self.__discover_hops()
        self.__calculate_routing_tables()

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
        return self.__virtual_network_instance.network_raw_output() if self.__executed else None

    #
    # Ants Discovery
    #
    def __discover_hops(self):

        ants_inst = AntsDiscovery(self.gend_subnetworks, self.gend_routers, self.equitemporality, debug=self.debug)

        ants_inst.sweep_network()
        ants_inst.calculate_hops()

        self.links = ants_inst.links
        self.hops = ants_inst.hops

    #
    # Routing Tables Generator
    #
    def __calculate_routing_tables(self):
        """
        This is the main function.
            It will pass the low-level processing (discovering the links that are virtually created by the program)
        to the virtual_building category.
            Its objective is also to handle the different parameters in order to pass certain unit tests.

        :return: returns final result if raw is True, else displays it.
            In further versions, the raw option should disappear to leave room for more useful things.
            The results, sent to another process, won't need to be displayed anymore, so raw will be implied.
        """

        if not self.links or self.hops:
            self.__discover_hops()

        rtg_inst = RoutingTablesGenerator(self.__virtual_network_instance, self.gend_subnetworks, self.gend_routers,
                                          self.links, self.hops, equitemporality=self.equitemporality)

        # getting routing tables
        routing_tables = []
        for i in range(len(self.routers)):
            routing_tables.append(rtg_inst.get_routing_table(i))

        self.routing_tables = routing_tables

        # formatting them to be displayed
        final = {}
        for i in range(len(self.routers)):
            name = self.gend_routers_names[i]
            final[name] = routing_tables[i]

        # reformatting final table to print in strings the router IP instead of having a FBL instance
        for router in final:
            for key in final[router]:
                final[router][key]['gateway'] = str(final[router][key]['gateway'])
                final[router][key]['interface'] = str(final[router][key]['interface'])

        self.formatted_raw_routing_tables = final

    def display_routing_tables(self):
        if self.__executed:
            # Hops
            print("----- HOPS -----")
            for tup in self.hops:
                s, e = tup
                path = self.hops[tup]
                string = f"From subnetwork {self.__virtual_network_instance.uid_to_name('subnet', s)} " \
                         f"to subnetwork {self.__virtual_network_instance.uid_to_name('subnet', e)}: "

                if len(path) == 1:
                    string += f"router {self.__virtual_network_instance.uid_to_name('router', path[0])}"
                else:
                    for i in range(len(path)):
                        if i > 0:
                            string += " > "
                        string += f"router {self.__virtual_network_instance.uid_to_name('router', path[i])}"

                print(string)

            # Routing tables
            print("\n\n----- ROUTING TABLES -----")
            for name in self.formatted_raw_routing_tables:
                print(f"Router {name}")
                for subnet in self.formatted_raw_routing_tables[name]:
                    print(f"  - {subnet}", ''.join([' ' for _ in range(18 - len(subnet))]),
                          f": {self.formatted_raw_routing_tables[name][subnet]['gateway']} "
                          f"via {self.formatted_raw_routing_tables[name][subnet]['interface']}")

    def output_routing_tables(self, file_path):
        if self.__executed:
            with open(file_path, encoding="utf-8", mode="w") as f:
                # Hops
                f.write("----- HOPS -----\n")
                for tup in self.hops:
                    s, e = tup
                    path = self.hops[tup]
                    string = f"Subnet {self.__virtual_network_instance.uid_to_name('subnet', s)} " \
                             f"to subnet {self.__virtual_network_instance.uid_to_name('subnet', e)}: "

                    if len(path) == 1:
                        string += f"router {self.__virtual_network_instance.uid_to_name('router', path[0])}"
                    else:
                        for i in range(len(path)):
                            if i > 0:
                                string += " > "
                            string += f"router {self.__virtual_network_instance.uid_to_name('router', path[i])}"

                    f.write(string + '\n')

                # Routing tables
                f.write("\n\n----- ROUTING TABLES -----\n")
                for name in self.formatted_raw_routing_tables:
                    f.write(f"\nRouter {name}\n")
                    for subnet in self.formatted_raw_routing_tables[name]:
                        f.write(f"  - {subnet} {''.join([' ' for _ in range(18 - len(subnet))])} : "
                                f"{self.formatted_raw_routing_tables[name][subnet]['gateway']} "
                                f"via {self.formatted_raw_routing_tables[name][subnet]['interface']}\n")
