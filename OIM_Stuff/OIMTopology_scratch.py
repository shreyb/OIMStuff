""" This module is reading from file with Facility/ResourceGroup/Resource xml similar to the one can download from OIM.

"""

import sys
from xml.dom import minidom
from ast import literal_eval

__author__ = "Tanya Levshina"
__email__ = "tlevshin@fnal.gov"


class Facility:
    pass


class Resource:
    pass

class ResourceGroup:
    pass

class Site:
    pass


class OIMTopology:
    pass



infile = 'shortsample_resourcegroup.xml'
#infile = 'resource_group_TEST.xml'
d = minidom.parse(infile)



facilities = {}
sites = {}
resourcegroups = {}


resourcegroupselts = d.getElementsByTagName('ResourceGroup')


for rgelt in resourcegroupselts:
    facilityelt = rgelt.getElementsByTagName('Facility')[0]
    facilityname = facilityelt.getElementsByTagName('Name')[0].firstChild.data
    facilityid = int(facilityelt.getElementsByTagName('ID')[0].firstChild.data)

    #   print facility, facilityid

    if facilityname not in facilities:
        facilities[facilityname] = {}
        facility = facilities[facilityname]
        facility['Name'] = facilityname
        facility['ID'] = facilityid
        facility['Sites'] = {}

    facility = facilities[facilityname]
    sites = facility['Sites']

    siteelt = rgelt.getElementsByTagName('Site')[0]
    sitename = siteelt.getElementsByTagName('Name')[0].firstChild.data
    siteid = siteelt.getElementsByTagName('ID')[0].firstChild.data

    if sitename not in sites:
        sites[sitename] = {}
        site = sites[sitename]
        site['Name'] = sitename
        site['ID'] = siteid

        # Support center is by site, so add it here
        site['SupportCenter'] = {}
        supcen = site['SupportCenter']

        supportcenterelt = rgelt.getElementsByTagName('SupportCenter')[0]
        supportcentername = supportcenterelt.getElementsByTagName('Name')[0].firstChild.data
        supportcenterid = supportcenterelt.getElementsByTagName('ID')[0].firstChild.data

        supcen['Name'] = supportcentername
        supcen['ID'] = supportcenterid

        site['ResourceGroups'] = {}

    site = sites[sitename]
    resourcegroups = site['ResourceGroups']

    groupname = rgelt.getElementsByTagName('GroupName')[0].firstChild.data
    groupid = rgelt.getElementsByTagName('GroupID')[0].firstChild.data

    if groupname not in resourcegroups:
        resourcegroups[groupname] = {}
        rg = resourcegroups[groupname]
        rg['Name'] = groupname
        rg['ID'] = groupid

    rg = resourcegroups[groupname]
    resourceelts = rgelt.getElementsByTagName('Resources')[0].getElementsByTagName('Resource')

    resources = {}
    for relt in resourceelts:
        # Don't care about disabled resources
        if literal_eval(relt.getElementsByTagName('Disable')[0].firstChild.data):
            continue

        # Don't care about resources that don't have CE or Connect Services.
        services = relt.getElementsByTagName('Services')[0].getElementsByTagName('Service')

        for service in services:
            if service.getElementsByTagName('Name')[0].firstChild.data in ['CE', 'Connect']:
                resourcename = relt.getElementsByTagName('Name')[0].firstChild.data
                resourceid = relt.getElementsByTagName('ID')[0].firstChild.data
                fqdn = relt.getElementsByTagName('FQDN')[0].firstChild.data

                resources[resourcename] = {}
                resource = resources[resourcename]

                resource['Name'] = str(resourcename)
                resource['ID'] = int(resourceid)
                resource['FQDN'] = str(fqdn)

                # VO Ownership
                vo_ownership = {}
                ownershiplist = relt.getElementsByTagName('VOOwnership')[0].getElementsByTagName('Ownership')
                for ownership in ownershiplist:
                    vo_ownership[str(ownership.getElementsByTagName('VO')[0].firstChild.data)] = float(ownership.\
                        getElementsByTagName('Percent')[0].firstChild.data)

                resource['VOOwnership'] = vo_ownership


#                print resource, resourceid, fqdn, vo_ownership


                # WLCG information
                wlcg = {}
                wlcgelt = relt.getElementsByTagName('WLCGInformation')[0]

#                print wlcgelt.firstChild

                if wlcgelt.firstChild.nodeValue == "(Information not available)":
                    wlcg['Available'] = False
                else:
                    wlcg['Available'] = True
                    try:
                        wlcg['AccountingName'] = str(wlcgelt.getElementsByTagName('AccountingName')[0].firstChild.data)
                    except AttributeError:
                        wlcg['AccountingName'] = None

                resource['WLCG'] = wlcg


                # Contact info
                contacts = {}
                contactlistselt = relt.getElementsByTagName('ContactLists')[0]

                # We only care about the Resource Report Contact list
                clelt_list = contactlistselt.getElementsByTagName('ContactList')
                for clelt in clelt_list:
                    if clelt.getElementsByTagName('ContactType')[0].firstChild.data == 'Resource Report Contact':
                        contactselt = clelt.getElementsByTagName('Contacts')[0]
                        celts = contactselt.getElementsByTagName('Contact')

                        for celt in celts:
                            name = celt.getElementsByTagName('Name')[0].firstChild.data
#                            print resource, name
                            contacts[name] = {}
                            contact = contacts[name]

                            contact['Email'] = None
                            contact['ContactRank'] = str(celt.getElementsByTagName('ContactRank')[0].firstChild.data)

                resource['Contacts'] = contacts

#                print resource, resourceid, fqdn, vo_ownership, wlcg, contacts
#                 print resources
                break

#    print resources

    rg['Resources'] = resources


#print facilities


#Test

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


    #print "\tItem: {}".format(item)
    #print "\n"









