import json
from RoutingTablesCalculator.core.errors import MissingJSONTag, WrongJSONTag, MissingJSONInfo
from RoutingTablesCalculator.virtual_building.network_creator import NetworkCreator


class JSONAdapter:
    def __init__(self, file_path):
        self.file_path = file_path

    def __call__(self, *args, **kwargs):
        with open(self.file_path, 'r') as file:
            decoded = json.load(file)

        found_networks, found_routers, found_links, links_or_connections = False, False, False, 'Links'
        for part in decoded:
            print(part)
            if part == 'Networks':
                found_networks = True
            elif part == 'Routers':
                found_routers = True
            elif part == 'Links' or part == 'Connections':
                links_or_connections = 'Links' if part == 'Links' else 'Connections'
                found_links = True
            else:
                raise WrongJSONTag(part)

        if not found_routers:
            raise MissingJSONTag('Routers')
        if not found_networks:
            raise MissingJSONTag('Networks')
        if not found_links:
            raise MissingJSONTag('Links')

        # we init the instance
        inst = NetworkCreator()

        # we register all subnets
        for name in decoded['Networks']:
            net = decoded['Networks'][name]

            if "cidr" in net:
                # we found a CIDR, so we split it and return the network
                ip, mask = net['cidr'].split('/')
                inst.create_network(ip, mask, str(name))
            elif "ip" in net and "mask" in net:
                # we found an IP and a mask
                ip, mask = net['ip'], net['mask']
                inst.create_network(ip, mask, str(name))
            else:
                # missing a cidr tag or a couple IP/mask
                raise MissingJSONInfo('Networks', str(name), "CIDR or IP/mask couple")

        # then we register all routers
        for name in decoded['Routers']:
            router = decoded['Routers'][name]

            if router and "internet" in router:
                inst.create_router(name=str(name), internet_connection=True)
            else:
                inst.create_router(name=str(name))

        # finally, we link all things between them
        list_ = decoded['Links'] if links_or_connections == 'Links' else decoded['Connections']
        for link in list_:
            subnets = list_[link]
            inst.connect_router_to_networks(link, subnets)

        return inst
