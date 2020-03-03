from RoutingTablesCalculator.virtual_building.utils import *


class RoutingTablesGenerator:

    #
    # DUNDERS
    #
    def __init__(self, subnets, routers, links, hops, equitemporality=True):
        # given basics
        self.subnets = subnets
        self.routers = routers
        self.equitemporality = equitemporality
        self.hops = hops
        self.links = links
        self.master_router = get_master_router(self.routers)

    #
    # Checkers
    #
    @staticmethod
    def not_in_subnets_done(subnets_done, uid):
        return uid not in subnets_done

    #
    # Getters
    #
    @staticmethod
    def router_ip(instance_, provided):
        for I in range(len(instance_.routers)):
            if instance_.routers[I]['uid'] == provided:
                return instance_.routers[I]['ip']
        return False

    #
    # Executers
    #
    def build_paths_from_possibilites(self, routers_infos, outer_list, inner_list, return_as_dict=False):
        paths_ = {} if return_as_dict else []

        for end in outer_list:
            inner_paths = []
            for start in inner_list:
                # we get the previously generated hop
                check = (start != end)
                if check:
                    inner_paths.append(self.hops[(start, end)])
                else:
                    inner_paths.append([start])
            # we choose the smaller path out of every path in this list
            if (inner_paths[0] == [routers_infos[1]]) and (routers_infos[0] != routers_infos[1]):
                del inner_paths[0]
            if return_as_dict:
                paths_[end] = smaller_of_list(inner_paths)
            else:
                paths_.append(smaller_of_list(inner_paths))

        if return_as_dict:
            return paths_
        else:
            return smaller_of_list(paths_)[0]

    def try_router_connected_to_subnet(self, subnets, router_uid):
        ip_ = None
        for subnet_ in subnets:
            result = self.router_ip(self.subnets[subnet_]['instance'], router_uid)
            if result is not False:
                ip_ = result
                break
        return ip_

    #
    # Callable
    #
    def get_routing_table(self, router_id):

        routing_table = {}
        subnets_done = []
        subnets_attached = self.links['routers'][router_id]

        # starting off by listing attached subnets and getting their ip for this router
        for subnet in subnets_attached:
            inst_ = self.subnets[subnet]['instance']
            routing_table[inst_.cidr] = self.router_ip(inst_, router_id)
            subnets_done.append(subnet)

        # getting master route
        master_attached = self.links['routers'][self.master_router]

        to_master_uid = self.build_paths_from_possibilites([self.master_router, router_id],
                                                           master_attached, subnets_attached)

        to_master_ip = self.try_router_connected_to_subnet(subnets_attached, to_master_uid)
        if not to_master_ip:
            raise Exception("To-master router should have been found in at least one of the subnets")
        routing_table['0.0.0.0/0'] = to_master_ip

        # now we get each non-registered-yet subnet left
        subnets_left = [i for i in self.subnets
                        if self.not_in_subnets_done(subnets_done, self.subnets[i]['instance'].uid)]
        paths = self.build_paths_from_possibilites([self.master_router, router_id], subnets_left,
                                                   subnets_attached, return_as_dict=True)

        for subnet in subnets_left:
            router = paths[subnet][0]
            ip = self.try_router_connected_to_subnet(subnets_attached, router)
            if not ip:
                raise Exception(f"Router id {router} should have been found in at least one of the subnets")
            routing_table[self.subnets[subnet]['instance'].cidr] = ip

        return routing_table

    def calculate_better_path_from_delays(self):
        raise NotImplementedError
