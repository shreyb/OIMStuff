""" This module is reading from file with Facility/ResourceGroup/Resource xml similar to the one can download from OIM.

"""

import sys
from xml.dom import minidom
from ast import literal_eval

__author__ = "Tanya Levshina"
__email__ = "tlevshin@fnal.gov"


class Facility(object):
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.sites = {}
        self.facility = {}

    def parse(self, parent_elt):
        facilityelt = parent_elt.getElementsByTagName('Facility')[0]
        self.id = int(facilityelt.getElementsByTagName('ID')[0].firstChild.data)
        return

    def build_dict(self):
        self.facility['Name'] = self.name
        self.facility['ID'] = self.id
        self.facility['Sites'] = self.sites
        return self.facility



class Site:
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.resourcegroups = {}
        self.supportcenter = {}
        self.site = {}

    def parse(self, parent_elt):
        siteelt = parent_elt.getElementsByTagName('Site')[0]
        self.id = int(siteelt.getElementsByTagName('ID')[0].firstChild.data)
        self.supportcenter = self.get_support_center_dict(parent_elt)
        return

    def get_support_center_dict(self, parent_elt):
        self.supportcenter = {}
        supportcenterelt = parent_elt.getElementsByTagName('SupportCenter')[0]
        supportcentername = supportcenterelt.getElementsByTagName('Name')[0].firstChild.data
        supportcenterid = supportcenterelt.getElementsByTagName('ID')[0].firstChild.data
        self.supportcenter['Name'] = supportcentername
        self.supportcenter['ID'] = supportcenterid
        return self.supportcenter

    def build_dict(self):
        self.site['Name'] = self.name
        self.site['ID'] = self.id
        self.site['SupportCenter'] = self.supportcenter
        self.site['ResourceGroups'] = self.resourcegroups
        return self.site


class ResourceGroup:
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.resources = {}
        self.rg = {}

    def parse(self, parent_elt):
        self.id = parent_elt.getElementsByTagName('GroupID')[0].firstChild.data
        return

    def build_dict(self):
        self.rg['Name'] = self.name
        self.rg['ID'] = self.id
        self.rg['Resources'] = self.resources
        return self.rg


class Resource:
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.fqdn = ''
        self.resource = {}

    def parse(self, parent_elt):
        self.id = parent_elt.getElementsByTagName('ID')[0].firstChild.data
        self.fqdn = parent_elt.getElementsByTagName('FQDN')[0].firstChild.data
        self.resource['VOOwnership'] = self.get_vo_ownership_dict(parent_elt)
        self.resource['WLCG'] = self.get_wlcg_info(parent_elt)
        self.resource['Contacts'] = self.get_contact_info(parent_elt)
        return

    def get_vo_ownership_dict(self, parent_elt):
        # VO Ownership
        self.vo_ownership = {}
        ownershiplist = parent_elt.getElementsByTagName('VOOwnership')[0].getElementsByTagName('Ownership')
        for ownership in ownershiplist:
            self.vo_ownership[str(ownership.getElementsByTagName('VO')[0].firstChild.data)] = float(
                ownership. \
                    getElementsByTagName('Percent')[0].firstChild.data)
        return self.vo_ownership

    def get_wlcg_info(self, parent_elt):
        # WLCG information
        self.wlcg = {}
        wlcgelt = parent_elt.getElementsByTagName('WLCGInformation')[0]
        if wlcgelt.firstChild.nodeValue == "(Information not available)":
            self.wlcg['Available'] = False
        else:
            self.wlcg['Available'] = True
            try:
                self.wlcg['AccountingName'] = str(wlcgelt.getElementsByTagName('AccountingName')[0].firstChild.data)
            except AttributeError:
                self.wlcg['AccountingName'] = None
        return self.wlcg

    def get_contact_info(self, parent_elt):
        self.contacts = {}
        contactlistselt = parent_elt.getElementsByTagName('ContactLists')[0]

        # We only care about the Resource Report Contact list
        clelt_list = contactlistselt.getElementsByTagName('ContactList')
        for clelt in clelt_list:
            if clelt.getElementsByTagName('ContactType')[0].firstChild.data == 'Resource Report Contact':
                contactselt = clelt.getElementsByTagName('Contacts')[0]
                celts = contactselt.getElementsByTagName('Contact')

                for celt in celts:
                    name = celt.getElementsByTagName('Name')[0].firstChild.data
                    self.contacts[name] = {}
                    contact = self.contacts[name]

                    contact['Email'] = None
                    contact['ContactRank'] = str(
                        celt.getElementsByTagName('ContactRank')[0].firstChild.data)

        return self.contacts

    def build_dict(self):
        self.resource['Name'] = str(self.name)
        self.resource['ID'] = int(self.id)
        self.resource['FQDN'] = str(self.fqdn)
        self.resource['VOOwnership'] = self.vo_ownership
        self.resource['WLCG'] = self.wlcg
        self.resource['Contacts'] = self.contacts
        return self.resource




class OIMTopology:

    xml_file = 'resource_group_TEST.xml'

    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.facilities = {}

    def parse(self):
        d = minidom.parse(self.xml_file)
        resourcegroupselts = d.getElementsByTagName('ResourceGroup')

        for rgelt in resourcegroupselts:
            facilityelt = rgelt.getElementsByTagName('Facility')[0]
            facilityname = facilityelt.getElementsByTagName('Name')[0].firstChild.data

            if facilityname not in self.facilities:
                facility = Facility(facilityname)
                facility.parse(rgelt)
                self.facilities[facilityname] = facility.build_dict()

            facility = self.facilities[facilityname]
            sites = facility['Sites']

            siteelt = rgelt.getElementsByTagName('Site')[0]
            sitename = siteelt.getElementsByTagName('Name')[0].firstChild.data

            if sitename not in sites:
                site = Site(sitename)
                site.parse(rgelt)
                sites[sitename] = site.build_dict()

            site = sites[sitename]
            resourcegroups = site['ResourceGroups']

            groupname = rgelt.getElementsByTagName('GroupName')[0].firstChild.data

            if groupname not in resourcegroups:
                rg = ResourceGroup(groupname)
                rg.parse(rgelt)
                resourcegroups[groupname] = rg.build_dict()

            rg = resourcegroups[groupname]
            resourceelts = rgelt.getElementsByTagName('Resources')[0].getElementsByTagName('Resource')

            resources = {}
            for relt in resourceelts:
                # Don't care about disabled resources
                if literal_eval(relt.getElementsByTagName('Disable')[0].firstChild.data):
                    continue

                # Don't care about resources that don't have CE or Connect Services.  Once we see that one of those
                # is there at a facility, call it a Resource, get the info, and move onto the next resource
                services = relt.getElementsByTagName('Services')[0].getElementsByTagName('Service')

                for service in services:
                    if service.getElementsByTagName('Name')[0].firstChild.data in ['CE', 'Connect']:
                        resourcename = relt.getElementsByTagName('Name')[0].firstChild.data

                        if resourcename in resources:
                            continue

                        resource = Resource(resourcename)
                        resource.parse(relt)
                        resources[resourcename] = resource.build_dict()
                        break


            rg['Resources'] = resources





#Test
def test(facilities):

    for key, facility in facilities.iteritems():
        print "Facility: {}".format(facility['Name'])

        for key, site in facility['Sites'].iteritems():
            print "\tSite: {}".format(site['Name'])

            for key, resourcegroup in site['ResourceGroups'].iteritems():
                print '\t\tResource Group: {}'.format(resourcegroup['Name'])

                for key, resource in resourcegroup['Resources'].iteritems():
                    print '\t\t\tResource Name: {}'.format(resource['Name'])
                    print '\t\t\tID: {}'.format(resource['ID'])
                    print '\t\t\tWLCG: {}'.format(resource['WLCG'])
                    print '\t\t\tContacts: {}'.format(resource['Contacts'])
                    print '\t\t\tVOOwnership: {}'.format(resource['VOOwnership'])


def main():
    infile = 'shortsample_resourcegroup.xml'
    #infile = 'resource_group_TEST.xml'
    topology = OIMTopology(infile)
    topology.parse()

    print topology.facilities

    test(topology.facilities)


main()







