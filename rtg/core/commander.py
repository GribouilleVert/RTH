from rtg.virtual_building.network_creator import NetworkCreator
from rtg.virtual_building.ants import AntsDiscovery
from rtg.virtual_building.routing_tables_generator import RoutingTablesGenerator


class Commander:
    """
    This is the commander class. Which everything comes from and where everything goes.
    We could call that a hub, I call that a good way to handle a complex program.
    """

    virtual_network_instance, ants_system_instance, routing_tables_generator_instance = None, None, None
    equitemporality = None
    subnetworks, routers = None, None
    routers_names = None
    links, hops = None, None

    #
    # DUNDERS
    #
    def __init__(self, equitemporality=True):
        self.virtual_network_instance = NetworkCreator()
        self.equitemporality = equitemporality

    #
    # Network Creator
    #
    def build_virtual_network(self, subnets, routers, links):

        inst = self.virtual_network_instance

        # Create subnets
        for name in subnets:
            ip, mask = subnets[name].split('/')
            inst.create_network(ip, mask, str(name))

        # Create routers
        for name in routers:
            if routers[name]:
                inst.create_router(name=str(name), internet_connection=True)
            else:
                inst.create_router(name=str(name))

        # Link both
        for router_name in links:
            inst.connect_router_to_networks(router_name, links[router_name])

        self.subnetworks = inst.subnetworks
        self.routers = inst.routers
        self.routers_names = inst.routers_names

    def network_raw_output(self):
        return self.virtual_network_instance.network_raw_output()

    #
    # Ants Discovery
    #
    def discover_hops(self):

        ants_inst = AntsDiscovery(self.subnetworks, self.routers, self.equitemporality)

        ants_inst.sweep_network()
        ants_inst.calculate_hops()

        self.links = ants_inst.links
        self.hops = ants_inst.hops

        return self.hops

    #
    # Routing Tables Generator
    #
    def calculate_routing_tables(self, raw=True):
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
            self.discover_hops()

        rtg_inst = RoutingTablesGenerator(self.subnetworks, self.routers, self.links, self.hops, self.equitemporality)

        # getting routing tables
        routing_tables = []
        for i in range(len(self.routers)):
            routing_tables.append(rtg_inst.get_routing_table(i))

        # formatting them to be displayed
        if raw is True:
            final = {}
            for i in range(len(self.routers)):
                name = self.routers_names[i]
                final[name] = routing_tables[i]
            return final
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
