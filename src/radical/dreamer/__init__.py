__author__    = 'RADICAL-Cybertools Team'
__email__     = 'info@radical-cybertools.org'
__copyright__ = 'Copyright 2020-2023, The RADICAL-Cybertools Team'
__license__   = 'MIT'

from .configs  import Config
from .managers import Session, ResourceManager
from .units    import MultiResource, Resource, Workload

import os            as _os
import radical.utils as _ru

version, version_detail, version_base, version_branch, \
    sdist_name, sdist_path = _ru.get_version(_os.path.dirname(__file__))
