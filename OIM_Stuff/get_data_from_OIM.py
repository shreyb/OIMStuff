import subprocess

# Note:  URL needs to take into account current date!


try:
    subprocess.check_call(['wget',
                       'http://myosg.grid.iu.edu/rgsummary/xml?summary_attrs_showhierarchy=on&summary_attrs_showwlcg=on&summary_attrs_showservice=on&summary_attrs_showfqdn=on&summary_attrs_showvoownership=on&summary_attrs_showcontact=on&gip_status_attrs_showtestresults=on&downtime_attrs_showpast=&account_type=cumulative_hours&ce_account_type=gip_vo&se_account_type=vo_transfer_volume&bdiitree_type=total_jobs&bdii_object=service&bdii_server=is-osg&start_type=7daysago&start_date=08%2F31%2F2016&end_type=now&end_date=08%2F31%2F2016&all_resources=on&facility_sel%5B%5D=10009&gridtype=on&gridtype_1=on&active=on&active_value=1&disable_value=1',
                       '-O', 'resource_group_TEST.xml'])
except:
    print "NOPE!"



