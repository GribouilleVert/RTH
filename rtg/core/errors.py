# NetworkBasic-specific errors
class OverlappingError(Exception):

    def __init__(self, type_, net_range, ip_or_range, mask=None):
        self.type = type_
        self.range = f"{net_range['start']} - {net_range['end']}"

        if type_ == 'start':
            self.ip = ip_or_range
            self.mask = mask
            if isinstance(mask, int):
                self.mask_display = f"/{self.mask}"
            else:
                self.mask_display = f" (with mask {self.mask})"
        elif type_ == 'end':
            self.ip = f"{ip_or_range['start']} - {ip_or_range['end']}"

    def __str__(self):
        if self.type == 'start':
            return f"IP {self.ip}{self.mask_display} is overlapping range {self.range}"
        elif self.type == 'end':
            return f"Range {self.ip} is overlapping range {self.range}"


class IPOffRangeError(Exception):

    def __str__(self):
        return "IP off range"


class NetworkLimitError(Exception):

    def __init__(self, type_):
        self.type = type_
        if type_ == 'bottom':
            self.display = "0.0.0.0"
        elif type_ == 'top':
            self.display = "255.255.255.255"

    def __str__(self):
        return f"Network {self.type} limit ({self.display}) reached"


# Parameters possibilities errors
class NoDelayAllowed(Exception):

    def __str__(self):
        return f"No delay allowed when equitemporality is set to True. " \
               f"Pass equitemporality=False when instancing NetworkCreator"


# Provided data errors
class IPAlreadyAttributed(Exception):
    def __init__(self, subnet_name, ip, attributed, tried_to_attribute):
        self.name = subnet_name
        self.ip = ip
        self.attributed = attributed
        self.tried = tried_to_attribute

    def __repr__(self):
        return f"The IP {self.ip} on the subnet {self.name} is already attributed to router {self.attributed}; " \
               f"Tried to give it to router {self.tried}"


class NameAlreadyExists(NameError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Name '{self.name}' already exists"


class NetworkUnreachable(Exception):

    def __init__(self, name, cidr, total):
        self.name = name
        self.cidr = cidr
        self.total = total

    def __str__(self):
        return f"The subnet {self.name} (CIDR {self.cidr}) is unreachable from master router. " \
               f"Total unreachable: {self.total}"


class WrongFileFormat(Exception):

    def __init__(self, ext):
        self.ext = ext

    def __str__(self):
        return f"Allowed formats: YAML (.yml), JSON (.json). Found: .{self.ext}"


# YAML adapter errors
class WrongYAMLTag(Exception):

    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"Unknown YAML tag: {self.tag}"


class MissingYAMLTag(Exception):

    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"Missing YAML tag: {self.tag}"


class MissingYAMLInfo(Exception):

    def __init__(self, cat, name, info):
        self.category = cat
        self.name = name
        self.info = info

    def __str__(self):
        return f"{self.category}: missing {self.info} in {self.category.lower()} {self.name}"


# JSON adapter errors
class WrongJSONTag(Exception):

    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"Unknown YAML tag: {self.tag}"


class MissingJSONTag(Exception):

    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return f"Missing YAML tag: {self.tag}"


class MissingJSONInfo(Exception):

    def __init__(self, cat, name, info):
        self.category = cat
        self.name = name
        self.info = info

    def __str__(self):
        return f"{self.category}: missing {self.info} in {self.category.lower()} {self.name}"
