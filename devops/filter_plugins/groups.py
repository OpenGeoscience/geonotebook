def cidr_list_to_rules(values):
    return [{'proto': 'all', 'cidr_ip': v} for v in values]

class FilterModule(object):
    def filters(self):
        return {
            'cidr_whitelist': cidr_whitelist
        }
