'''
usage:
  cloudseed agent

options:
  -h, --help               Show this screen.

'''
import sys
import salt.utils.event
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)


    sys.stdout.write('Listening for events from Salt\n')

    event = salt.utils.event.MasterEvent('/var/run/salt/master')
    for data in event.iter_events(tag='auth'):
        print(data)


