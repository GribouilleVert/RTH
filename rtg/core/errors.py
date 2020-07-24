# Passed base-data errors
class WronglyFormedSubnetworksData(Exception):

    def __str__(self):
        return "The subnetworks data given is wrongly formed or missing information. Please verify said data."


class WronglyFormedRoutersData(Exception):

    def __str__(self):
        return "The routers data given is wrongly formed or missing information. Please verify said data."


class WronglyFormedLinksData(Exception):

    def __str__(self):
        return "The link data given is wrongly formed or missing information. Please verify said data."


class MissingDataParameter(Exception):

    def __str__(self):
        return "Missing one of the required data (subnetworks, routers or links) and could not find an " \
               "already-existing network instance"


# NetworkCreator-specific errors
class OverlappingError(Exception):

    def __init__(self, new, existing):
        self.new_range = f"{new['start']} - {new['end']}"
        self.existing_range = f"{existing['start']} - {existing['end']}"

    def __str__(self):
        return f"Range {self.new_range} is overlapping range {self.existing_range}"


# Parameters possibilities errors
class NoDelayAllowed(Exception):

    def __str__(self):
        return "No delay allowed when equitemporality is set to True. " \
               "Pass equitemporality=False when instancing NetworkCreator"


# Process errors
class IPAlreadyAttributed(Exception):
    def __init__(self, subnet_name, ip, attributed, tried_to_attribute):
        self.name = subnet_name
        self.ip = ip
        self.attributed = attributed
        self.tried = tried_to_attribute

    def __str__(self):
        return f"The IP {self.ip} on the subnetwork '{self.name}' is already attributed to router " \
               f"'{self.attributed}'; Tried to give it to router '{self.tried}'"


class NameAlreadyExists(NameError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Name '{self.name}' already exists"


class UnreachableNetwork(Exception):

    def __init__(self, name, cidr, total):
        self.name = name
        self.cidr = cidr
        self.total = total

    def __str__(self):
        return f"The subnetwork '{self.name}' (CIDR {self.cidr}) is unreachable from master router. " \
               f"Total unreachable: {self.total}"


class MasterRouterError(Exception):

    def __init__(self, no_internet=False):
        if no_internet:
            self.text = "There is no connection to the internet on this network. Please connect one router."
        else:
            self.text = "An exception occured during master router definition. " \
                        "Please verify ONE (and only one) router is connected to internet"

    def __str__(self):
        return self.text
