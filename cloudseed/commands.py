import os
#import saltcloud


class Initialize(object):

    def start(self, **kwargs):
        cwd = os.getcwd()
        project_dir = '{0}/{1}'.format(cwd, '.cloudseed')

        try:
            os.mkdir(project_dir)
        except OSError:
            return

        with open('{0}/{1}'.format(project_dir, 'config'), 'w') as config:
            pass

        with open('{0}/{1}'.format(project_dir, 'development'), 'w') as dev:
            pass

        with open('{0}/{1}'.format(project_dir, 'production'), 'w') as prod:
            pass


class Bootstrap(object):
    def start(self, **kwargs):
        import pdb; pdb.set_trace()
        foo = 1
