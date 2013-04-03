'''
usage: cloudseed init
'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    import pdb; pdb.set_trace()
    foo = 1
