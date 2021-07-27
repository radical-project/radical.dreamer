
from ._base import Config


cfg_default = Config(from_dict={
    'schedule': {
        'strategy': 'smallest_to_fastest',
        'early_binding': True,
        'is_adaptive': False
    },
    'session': {
        'profile_base_name': 'rd.profile'
    }
})
