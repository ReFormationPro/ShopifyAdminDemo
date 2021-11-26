# This Python file uses the following encoding: utf-8

class Store():
    def __init__(self, id, active, name, brand_name, api_version, domain, api_key, api_password):
        self.id = id
        self.active = active
        self.name = name
        self.brand_name = brand_name
        self.api_version = api_version
        self.domain = domain
        self.api_key = api_key
        self.api_password = api_password

    def to_dict(self):
        return self.__dict__

    def fromDict(d):
        return Store(d.get("id"), d.get("active"), d.get("name"), d.get("brand_name"),
                d.get("api_version"), d.get("domain"), d.get("api_key"), d.get("api_password"))

    def toList(self):
        return [self.active, self.name, self.brand_name, self.api_version, self.domain,
                self.api_key, self.api_password]


