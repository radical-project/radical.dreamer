
from .enum import EnumTypes
from .rabbitmq import RabbitMQ

try:
    from radical.utils import TypedDict, as_dict
except ImportError:
    # for consistency with older releases (< 1.12)
    from radical.utils import Munch as TypedDict, demunch as as_dict
