import logging
import os

from invoke import Collection, task

from probe.HealthCheck import HealthCheck

logging.basicConfig(format='[%(levelname)s] %(asctime)s: %(message)s', level=os.environ.get('VERBOSITY', 50))
logger = logging.getLogger(__name__)

@task
def run(c, settings=""):
    """
    Run healthcheck
    :param c:
    :param settings:
    :return:
    """
    health_check = HealthCheck(settings_file=settings)
    health_check.check()


healthcheck = Collection('healthcheck')
healthcheck.add_task(run)
