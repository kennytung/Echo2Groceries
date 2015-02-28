#!/usr/bin/python

import sys, getpass, getopt
import time, datetime, dateutil.parser, pytz
import gflags
import httplib2

import OurGroceries

# setup the PyEcho path, you will need to change this to match your
# PyEcho install directory
sys.path.append('../PyEcho')
try:
    import PyEcho
except ImportError:
    print ''
    print 'Cannot import PyEcho, please download PyEcho from'
    print 'https://github.com/scotttherobot/PyEcho'
    print ''
    print 'You will need to setup PYTHONPATH so that python can import PyEcho.'
    print 'You can also do it in code by changing sys.path.append(...)'
    sys.exit(0)

def usage() :
    print ''
    print 'Usage: ', sys.argv[0], ' -[u:p:j:d:]'
    print '   -u: Amazon username'
    print '   -p: Amazon password'
    print '   -d: delay in seconds between each check for new tasks (default 30)'
    print ''
    print '   If no username/password is given, this program will ask for them.'
    print ''
    sys.exit(0)

def main() :
    email = None
    password = None
    delay = 30


    try:
        opts, args = getopt.getopt(sys.argv[1:], 'u:p:d:')
    except getopt.GetoptError, err:
        print str(err)
        usage()

    for o, a in opts:
        if o == '-u':
            email = a
        elif o == '-p':
            password = a
        elif o == '-d':
            delay = int(a)
        else:
            usage()

    if email == None:
        email = raw_input("Amazon username: ")
    if password == None:
        password = getpass.getpass()

    # See if I can log in to amazon
    echo = PyEcho.PyEcho(email, password)

    if not echo.loginsuccess:
        print ''
        print 'Could not log in to Amazon Echo webservice'
        print 'Wrong username/password?'
        print ''
        sys.exit(0)

    # main loop, run forever
    while True:
        shoppingitems = echo.shoppingitems()
        for si in shoppingitems:
            print 'Found shopping item: '+si['text']
            og = OurGroceries.OurGroceries('ichitoe@live.com', 'enter123')
            og.smartinsert(si['text'])
            og = None
            res = echo.deleteShoppingItem(si)
            # TODO: do I need to check the responds from Amazon?
        time.sleep(delay)

if __name__ == "__main__" :
    main()
