""" This module is reading from file with Facility/ResourceGroup/Resource xml similar to the one can download from OIM.

"""

import sys
import xml.dom.minidom

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



infile = open('shortsample_resourcegroup.xml', 'r')
document = infile.readlines()
d = xml.dom.minidom.parseString(''.join(document))

for element in d.getElementsByTagName('ResourceGroup'):
    print element.childNodes[0].data.strip()



infile.close()






