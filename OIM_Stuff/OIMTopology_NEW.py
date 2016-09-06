""" This module is reading from file with Facility/ResourceGroup/Resource xml similar to the one can download from OIM.

"""

import sys

__author__ = "Tanya Levshina"
__email__ = "tlevshin@fnal.gov"


class Facility:
    """Facility class holds information about OSG Facility,  information
    is pulled from OIM"""

    def __init__(self, facility_name):
        """Facility class holds information about OSG Facility

        Args:
            facility_name(str) - name of a facility
        """
        self.name = facility_name
        self.resource_groups = []
        self.rank = 0
        self.old_rank = 0
        self.old_hours = 0
        self.contacts = []
        self.total = 0

    def add_contact(self):
        """Consolidates contacts from all resource groups"""
        for resource_group in self.resource_groups:
            for email in resource_group.contacts:
                if email not in self.contacts:
                    self.contacts.append(email)

    def get_resource_group_by_resource(self, resource_name):
        """Tries to do reverse engineering and find facility by resource name.
        Problem is HostDescription in Gratia is setup by site admins and could be
        really different from Resource name registered in OIM.

        Args:
            resource_name(str) - resource group name in OIM

        Returns:
            ResourceGroup: resource group that contained a specified resource, None is not found
        """
        for resource_group in self.resource_groups:
            # sometimes resource in gratia matches resource group in OIM
            if resource_group.name.lower() == resource_name.lower():
                return resource_group
            # sometimes resource is a fqdn of the node where CE is running
            for fqdns in resource_group.fqdns:
                if fqdns.find(resource_name.lower()) >= 0:
                    return resource_group

            for resource in resource_group.resources:
                # sometimes resource has addition as CE or a number , e.g BNL_ATLAS - Resource Group
                # BNL_ATALAS_1 - Resource
                if resource.name.lower() == resource_name.lower()\
                        or resource.name.lower().find(resource_name.lower()) >= 0:
                    return resource_group
        return None

    def get_sorted(self):
        """Sorts resource groups by used wall hours"""
        self.resource_groups.sort(key=lambda x: x.total, reverse=True)


class ResourceGroup:
    """Resource Group class holds information about OSG Resource Group,  information
    is pulled from OIM"""
    def __init__(self, rgname, rgdescription, rgsite):
        """
        Args:
            rgname(str) - resource group name
            rgdescription(str) - resource group description
        """
        self.name = rgname
        self.description = rgdescription
        self.resources = []
        self.contacts = []
        self.projects = []
        self.fqdns = []
        self.site = rgsite

        self.total = 0
        self.old_hours = 0
        self.rank = 0
        self.old_rank = 0

    def add_contact(self, contacts):
        """add a new contact to the contact list"""
        for con in contacts:
            if con not in self.contacts:
                self.contacts.append(con)

    def get_resource(self, resource_name):
        """Return Resource by resource name.

        Args:
            resource_name(str) - resource group name in OIM

        Returns:
            Resource: resource group that contained a specified resource, None is not found
        """
        for resource in self.resources:
            # sometimes resource in gratia matches resource group in OIM
            if resource.name.lower() == resource_name.lower():
                return resource
            # sometimes resource is a fqdn of the node where CE is running
            for fqdns in self.fqdns:
                if fqdns.find(resource_name.lower()) >= 0:
                    return resource
            # sometimes resource has addition as CE or a number , e.g BNL_ATLAS - Resource Group
            # BNL_ATALAS_1 - Resource
            if resource.name.lower() == resource_name.lower() or resource.name.lower().find(resource_name.lower()) >= 0\
                    or resource_name.lower().find(resource.name.lower()):
                return resource
        if self.name.lower() == resource_name.lower():
            return self.resource[0]
        return None

    def get_sorted(self):
        """Sorts resource by used wall hours"""
        self.projects.sort(key=operator.attrgetter('hours'), reverse=True)


class Resource:
    """Resource Group class holds information about OSG Resource,  information
    is pulled from OIM"""
    def __init__(self, rname, rid, fqdns, vo_ownership):
        """
        Args:
            rname(str) - resource name
        """
        self.name = rname
        self.projects = []
        self.fqdns = fqdns
        self.rid = rid
        self.total = 0
        self.vo_ownership = vo_ownership

    def add_project(self, project_name, vo_name, project_id, principal_investigator, sh, field_of_science, wall_hours):
        """Instantiate Project and add it to project list
        Args:
            project_name(str)
            vo_name(str)
            project_id(str)
            principal_investigator(str)
            sh(str)
            field_of_science(str)
            wall_hours(float)
        """
        self.total += wall_hours
        for p in self.projects:
            if project_name == p.name:
                p.hours += wall_hours
                return
        self.projects.append(Project(project_name, vo_name, project_id, principal_investigator, sh,
                                     field_of_science, wall_hours))

    def get_sorted(self):
        """Sorts projects by used wall hours"""
        self.projects.sort(key=operator.attrgetter('hours'), reverse=True)


class Project:
    """Auxiliary class to hold information about Open Facility project
    """

    def __init__(self, pname, pid, principal_investigator, vo_name, sh, field_of_science, wall_hours):
        """
        Args:
            pname(str)
            pid(str)
            principal_investigator(str)
            vo_name(str)
            sh (str)
            field_of_science(str)
            wall_hours (float)
        """
        self.vo = vo_name
        self.name = pname
        self.sh = sh
        self.fos = field_of_science
        self.hours = wall_hours
        self.link = "https://oim.grid.iu.edu/oim/project?id = %s" % (pid,)
        self.pi = principal_investigator
        self.rank = 0
        self.old_rank = "NR"


class OIMTopology:
    """Builds OIM hierarchy from OIM xml file (facility and contacts)"""
    def __init__(self, filename, resource_topology):
        """
        Args:
            filename(str) - xml file name
            resource_topology - OIMResourceToplogy
        """
        self.filename = filename
        self.r_topology = resource_topology
        self.r_topology.parse()
        self.facilities = {}

    def parse(self):
        """Parses the contact information that is hardcoded in contact.txt file. Ideally this information should
        come from OIM but currently OIM is missing readable description information and doesn't have site PI contacts.
        The xml structure of contact file is preserved.
        """
        import xml.dom.minidom
        document = open(self.filename).readlines()
        d = xml.dom.minidom.parseString(''.join(document))
        self.facilities = {}
        for resource_group_element in d.getElementsByTagName("ResourceGroup"):
            if resource_group_element.getElementsByTagName("Disable")[0].childNodes[0].data.strip() == "True":
                continue
            site = resource_group_element.getElementsByTagName("Site")[0].childNodes[1].childNodes[0].data.strip()
            group_name = resource_group_element.getElementsByTagName("GroupName")[0].childNodes[0].data.strip()
            description = group_name
            resource_group = ResourceGroup(group_name, description, site)
            facility_element = resource_group_element.getElementsByTagName("Facility")[0]
            n = facility_element.getElementsByTagName("Name")[0].childNodes[0].data.strip().replace("  ", " ")
            if n not in self.facilities:
                facility = Facility(n)
                self.facilities[n] = facility
            else:
                facility = self.facilities[n]

            for r in resource_group_element.getElementsByTagName("Resource"):
                # we need to know if this is an active CE resource
                resource_id = r.getElementsByTagName("ID")[0].childNodes[0].data.strip()
                rn = self.r_topology.get_resource(resource_id)
                if rn is None:
                    continue
                resource_group.resources.append(rn)
                fqdn = r.getElementsByTagName("FQDN")[0].childNodes[0].data.strip()
                resource_group.fqdns.append(fqdn)
            # we don't find any active CE in this resource_group
            if len(resource_group.resources) == 0:
                continue
            facility.resource_groups.append(resource_group)
            contact_list = resource_group_element.getElementsByTagName("ContactList")
            for cl in contact_list:
                if cl.getElementsByTagName("ContactType")[0].childNodes[0].data == "Resource Report Contact":
                    for c in cl.getElementsByTagName("Contact"):
                        for e in c.getElementsByTagName("Email"):
                            resource_group.add_contact([e.childNodes[0].data])
            facility.add_contact()
        for fname in self.facilities.keys():
            f = self.facilities[fname]
            if len(f.resource_groups) == 0:
                del self.facilities[fname]

        return self.facilities

    # noinspection PyIncorrectDocstring
    def get_facility_by_resource(self, resource_name):
        """Finds facility by resource name
        Args:
            resource_name(str)
        Returns:
            facility(Facility) - if finds it , otherwise returns None
        """
        for fn, facility in self.facilities.items():
            for resource_group in facility.resource_groups:
                if resource_group.name.lower() == resource_name.lower():
                    return facility
                for fqdns in resource_group.fqdns:
                    if fqdns.find(resource_name.lower()) >= 0:
                        return facility
                for resource in resource_group.resources:
                    if resource.name.lower() == resource_name.lower()\
                            or resource.name.lower().find(resource_name.lower()) >= 0:
                        return facility
        return None


class OIMResourceGroupTopology:
    """Builds OIM hierarchy from OIM xml file (active CE resources)"""
    def __init__(self, filename):
        import xml.dom.minidom
        self.filename = filename
        documents = open(self.filename).readlines()
        self.document = xml.dom.minidom.parseString(''.join(documents))
        self.resources = {}

    def parse(self):
        for r in self.document.getElementsByTagName("Resource"):
            if r.getElementsByTagName("Disable")[0].childNodes[0].data.strip() == "True":
                continue
            vo_ownership = {}
            for owner in r.getElementsByTagName("VOOwnership")[0].getElementsByTagName("Ownership"):    #Clean this up
#                print len(owner.childNodes)
#                print owner.childNodes[1].childNodes[0].data.strip('[()]')      # VO
#                print owner.childNodes[0].childNodes[0].data.strip('[()]')        # percentage
                vo_ownership[owner.childNodes[1].childNodes[0].data.strip('[()]')] = owner.childNodes[0].childNodes[0].data.strip('[()]')

#            print vo_ownership

            # WLCG
            WLCG = r.getElementsByTagName("WLCGInformation")[0].childNodes[0].nodeName  # Temp. var name
            print WLCG
            if WLCG == '#text':


            for s in r.getElementsByTagName("Service"):
                if s.getElementsByTagName("Name")[0].childNodes[0].data.strip() == "CE"\
                        or s.getElementsByTagName("Name")[0].childNodes[0].data.strip() == "Connect":
                    rid = r.getElementsByTagName("ID")[0].childNodes[0].data.strip()
                    name = r.getElementsByTagName("Name")[0].childNodes[0].data.strip()
                    fqdn = r.getElementsByTagName("FQDN")[0].childNodes[0].data.strip()
                    self.resources[rid] = Resource(name, rid, fqdn, vo_ownership)
                    break

    def get_resource(self, resource_id):
        """Searches xml doc for specific resource id
        Args:
            resource_id(str) - resource id in OIM
        Returns:
            resource_name(str) - resource name with this resource id
        """
        if resource_id in self.resources:
            return self.resources[resource_id]
        return None


# noinspection PyNoneFunctionAssignment
if __name__ == "__main__":
#    topology = OIMTopology(sys.argv[1], OIMResourceGroupTopology(sys.argv[2]))
#    topology.parse()
    facilities = OIMTopology(sys.argv[1], OIMResourceGroupTopology(sys.argv[2])).parse()
#    resource='NUMEP-OSG'
#    facility=topology.get_facility_by_resource(resource)
#    print facility.name
#    resource_group=facility.get_resource_group_by_resource(resource)
#    print resource_group.name
#    res=resource_group.get_resource(resource)
#    print res.name
    for name, f in facilities.items():
        print "Facility:", name, ", ".join(f.contacts)
        for rg in f.resource_groups:
            print "\tResource Group Name: %s" % rg.name
            print "\tSite: {}".format(rg.site)
            for r in rg.resources:
                print "\t\t%s\t%s" % (r.name, r.rid)
                print "VO OWNERSHIP: {}".format(r.vo_ownership)
