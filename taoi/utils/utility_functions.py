import csv
from sys import stdout as sys_stdout

###############################################################################
############################################################# utility functions

def cat(*args):
    return ''.join([str(i) for i in args])

def csv_key_value_dict(input_dict, key_name='key', value_name='value',
        out=sys_stdout):
    w = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
    w.writerow([key_name, value_name])
    for k,v in input_dict.iteritems():
        w.writerow([k,v])


