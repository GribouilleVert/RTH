from enum import Enum
from RoutingTablesCalculator.core.errors import NetworkUnreachable
from RoutingTablesCalculator.virtual_building.utils import *


class AntState(Enum):
    Alive = 0
    Dead = 1


class Ant:
    """
    The main Ant class.
    This class is used for a blind discovery through the virtual network we created, to see links between subnets and
    routers.

    Below,
        - Iteration is the move to the next router or subnet,
        - Explored is the fact a router or network has already been explored by any of the alive ants.
        - Possibility is an existing subnet or router that has already been explored or not.
    There are three cases each Iteration:
        - One Possibility, not Explored: the ant moves to the possibility and explores it, storing data into its history
        - One or several Possibilities, all Explored: the ant dies and leaves no children.
        - Several Possibilites, one or more not Explored: the ant dies and leaves as many children as there are
            Possibilites to explore. It also gives them the same history plus the possibility, meaning the child will
            "spawn" on the possibility the mother could not explore; Children may then continue exploring normally.
    """

    def __init__(self, state: AntState, pos: dict):
        self.__state = state
        self.__pos = pos
        # { "subnets": [], "routers": [] }
        self._history = {"subnets": [pos["subnet"]], "routers": [pos["router"]]}

    @property
    def router(self):
        return self.__pos["router"]

    @property
    def subnet(self):
        return self.__pos["subnet"]

    @property
    def dead(self):
        return self.__state == AntState.Dead

    def kill(self):
        self.__state = AntState.Dead

    def move_to(self, pos):
        hop_type = self.next_hop_type()
        self.__pos[hop_type] = pos
        self._history[f"{hop_type}s"].append(self.__pos[hop_type])

    def get_history(self):
        return self._history

    def feed_history(self, hist):
        self._history["routers"][0:0] = hist["routers"]
        self._history["subnets"][0:0] = hist["subnets"]

    def next_hop_type(self):
        sub = self._history['subnets']
        rout = self._history['routers']

        if len(sub) > len(rout):
            # we expect to hop to a router
            return 'router'
        elif len(sub) == len(rout):
            # we expect to hop to a subnet
            return 'subnet'
        else:
            raise Exception("FindAnt history: Router length seems to be greater than subnets length; impossible")


class SweepAnt(Ant):
    """
    The Sweep Ant. Its particularity is to check if all the subnets are reachable.
    To verify this condition, we always start from the router which possesses internet connection, so we are sure
    that the network is reachable this way.
    """

    def __init__(self, state: AntState, pos: dict):
        super().__init__(state, pos)

    def check_next_move(self, next_):
        hop_type = self.next_hop_type()

        return next_ not in self._history[f"{hop_type}s"]


class FindAnt(Ant):
    """
    The Find Ant. Its objective is discover step-by-step each network until it finds the network it is looking for.
    """

    def __init__(self, state: AntState, pos: dict, objective):
        super().__init__(state, pos)
        self.__objective = objective

    def check_next_move(self, next_):
        hop_type = self.next_hop_type()

        if next_ not in self._history[f"{hop_type}s"]:
            if hop_type == 'subnet' and next_ == self.__objective:
                # means we are going to jump on the good subnet
                return [True, True]
            else:
                return [True, False]
        else:
            return [False, False]


class AntsDiscovery:

    #
    # DUNDERS
    #
    def __init__(self, subnets, routers, equitemporality=True):
        # given basics
        self.subnets = subnets
        self.routers = routers
        self.equitemporality = equitemporality
        # made-up basics
        self.hops = {}
        self.links, self.subnets_table = self.prepare_matrix_and_links()
        self.master_router = get_master_router(self.routers)

    #
    # Executers
    #
    def prepare_matrix_and_links(self):
        """
        Prepares the matrix from the subnets IDs
        Also prepares the links from all the connections between subnets and routers

        :return: links, matrix
        """

        # links
        links = {'subnets': {}, 'routers': {}}

        for s in range(len(self.subnets)):
            routers = self.subnets[s]['instance'].routers

            uids = []
            for n in range(len(routers)):
                uids.append(routers[n]['uid'])
            uids.sort()

            links['subnets'][s] = uids

        for s in range(len(self.routers)):
            nets = self.routers[s].connected_networks

            uids = []
            for n in range(len(nets)):
                uids.append(nets[n]['uid'])
            uids.sort()

            links['routers'][s] = uids

        # matrix
        matrix = []
        for start in range(len(self.subnets)):
            for end in range(len(self.subnets)):
                if start != end:
                    matrix.append([start, end])

        return links, matrix

    @staticmethod
    def ants_discovery_process(discovery_type, links, subnet_start, subnet_end=None):
        """
        This function is the core of the ants process.
        The labels in comments in the code below all refer to this section:

        INIT: we initialise as many ants as there are routers connected to the starting subnet
        PROCESS:
            1. Hop to next subnets
            2. Hop to next routers

                x.1 - If there is only a subnet, we then do test to see which case is here. For cases, see the Ant class
                    docstring for a full explanation of the different cases.
                x.2 - Several possibilities, we kill the ant and generate children

            3. "Cleaning up dead bodies": we delete the dead ants from the ants list

        RESULT: we then return what has to be returned

        :param discovery_type: either 'sweep' for the sweep or anything else for the matrix process
        :param links: the links
        :param subnet_start: the subnet where the discovery will start
        :param subnet_end: the objective subnet we need to find
        :return: visited, ants_at_objective : one is to ignore, the 2nd for sweep and the 1st for find
        """

        visited = {"subnets": [], "routers": []}
        routers, subnets = links['routers'], links['subnets']
        ants = []
        ants_at_objective = []

        def not_visited(type_, pos):
            return pos not in visited[type_]

        def visit(type_, pos):
            visited[type_].append(pos)

        def type_at_pos(type_, where):
            list_ = routers if type_ == 'subnets' else subnets
            return list_[where]

        # INIT
        for r in type_at_pos('routers', subnet_start):
            if discovery_type == 'sweep':
                ant = SweepAnt(AntState.Alive, {"router": r, "subnet": subnet_start})
            else:
                ant = FindAnt(AntState.Alive, {"router": r, "subnet": subnet_start}, subnet_end)
            ants.append(ant)
            visit('routers', r)

        visit('subnets', subnet_start)

        # PROCESS
        while len(ants):

            # 1. Hop to next subnets
            for ant in ants:
                subnets_at_pos = [s_ for s_ in routers[ant.router] if not_visited('subnets', s_)]

                # 1.1: One subnet
                if len(subnets_at_pos) == 1:
                    check = ant.check_next_move(subnets_at_pos[0])

                    if discovery_type == 'sweep':
                        # Special to the sweeping ant
                        if check is True:
                            # We can proceed to next subnet
                            ant.move_to(subnets_at_pos[0])
                            visit('subnets', subnets_at_pos[0])
                        elif check is False:
                            # we already went there
                            ant.kill()
                        else:
                            raise Exception("Unexpected to happen at anytime")
                    else:
                        if check[0] is True and check[1] is True:
                            # We found the objective
                            # We stock ant history and kill the ant
                            ants_at_objective.append(ant.get_history()['routers'])
                            ant.kill()
                        elif check[0] is True and check[1] is False:
                            # We can proceed to next subnet
                            ant.move_to(subnets_at_pos[0])
                            visit('subnets', subnets_at_pos[0])
                        elif not check[0]:
                            # We went here
                            ant.kill()
                        else:
                            raise Exception("Unexpected to happen at anytime")

                # 1.2: Several subnets, kills and births
                else:
                    ant.kill()
                    for subnet_ in subnets_at_pos:
                        if discovery_type == 'sweep':
                            new_ant = SweepAnt(AntState.Alive, {"router": ant.router, "subnet": subnet_})
                        else:
                            new_ant = FindAnt(AntState.Alive, {"router": ant.router, "subnet": subnet_}, subnet_end)
                        new_ant.feed_history(ant.get_history())
                        ants.append(new_ant)

            # 2. Hop to next routers
            for ant in ants:
                routers_at_pos = [r for r in subnets[ant.subnet] if not_visited('routers', r)]

                # 2.1: One router
                if len(routers_at_pos) == 1:
                    check = ant.check_next_move(routers_at_pos[0])
                    if discovery_type == 'sweep':
                        if check is True:
                            ant.move_to(routers_at_pos[0])
                            visit('routers', routers_at_pos[0])
                        elif check is False:
                            ant.kill()
                        else:
                            raise Exception("Unexpected to happen at anytime")
                    else:
                        if check[0] is True:
                            ant.move_to(routers_at_pos[0])
                            visit('routers', routers_at_pos[0])
                        elif check[0] is False:
                            ant.kill()
                        else:
                            raise Exception("Unexpected to happen at anytime")

                # 2.2: Several routers, kills and births
                else:
                    ant.kill()
                    for router in routers_at_pos:
                        if discovery_type == 'sweep':
                            new_ant = SweepAnt(AntState.Alive, {"router": router, "subnet": ant.subnet})
                        else:
                            new_ant = FindAnt(AntState.Alive, {"router": router, "subnet": ant.subnet}, subnet_end)
                        new_ant.feed_history(ant.get_history())
                        ants.append(new_ant)

            # 3. Cleaning up dead bodies
            for ant in ants:
                if ant.dead:
                    ants.remove(ant)

        # RESULT
        return visited, ants_at_objective

    #
    # Callables
    #
    def sweep_network(self):
        """
        We sweep the network from the master router and try to reach every subnetwork.
        This function is a suicider, as to say it will die by raising an error if any subnet is unreachable; else the
        program will continue
        """

        master = self.master_router
        subnet_start = self.routers[master].connected_networks[0]['uid']

        result, _ = self.ants_discovery_process('sweep', self.links, subnet_start)

        for subnet in self.subnets:
            if subnet not in result['subnets']:
                inst = self.subnets[subnet]['instance']
                total = len(self.subnets) - len(result['subnets'])
                raise NetworkUnreachable(inst.name, inst.cidr, total)

    def calculate_hops(self):
        """
        We calculate the hops for each matrix entry, and either keep the smallest one if there is
        equitemporality, or stock each hop for further analysis and calculus by another function
        """

        for i in range(len(self.subnets_table)):
            matrix = self.subnets_table[i]
            s, e = matrix

            _, at_objective = self.ants_discovery_process('find', self.links, s, e)

            # If equitemporality is set to False, we take all the paths to calculate later
            if self.equitemporality:
                # Test if there are different paths, and pick the smaller one
                if len(at_objective) == 1:
                    # only one path found
                    self.hops[(s, e)] = at_objective[0]
                else:
                    self.hops[(s, e)] = smaller_of_list(at_objective)
            else:
                self.hops[(s, e)] = at_objective
