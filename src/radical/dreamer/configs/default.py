
from ._base import Config


cfg_default = Config(from_dict={
    'session': {
        'profile_base_name': './rd.profile'
    },
    'schedule': {
        'strategy': 'smallest_to_fastest',
        'early_binding': True,
        'is_adaptive': False
    }
})
