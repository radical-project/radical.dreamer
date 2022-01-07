
__author__    = 'RADICAL-Cybertools Team'
__copyright__ = 'Copyright 2021-2022, The RADICAL-Cybertools Team'
__license__   = 'MIT'

# ------------------------------------------------------------------------------
#
# We provide a base class for all kinds of dict-like data objects in the RCT
# stack: resource configs, agent configs, job descriptions, task descriptions,
# pilot descriptions, workload descriptions etc.  That class provides:
#
#   - dict like API
#   - public dict keys exposed as attributes
#   - schema based type definitions
#   - optional runtime type checking
#

import copy
import sys

from radical.utils import as_list, as_tuple, is_string


# ------------------------------------------------------------------------------
#
class TDError(Exception):

    # --------------------------------------------------------------------------
    #
    def __init__(self, msg=None, level=1):

        f = sys._getframe(level)
        if 'self' in f.f_locals:
            cls_name = f.f_locals['self'].__class__.__name__
        elif 'cls' in f.f_locals:
            cls_name = f.f_locals['cls'].__name__
        else:
            cls_name = '<>'

        super().__init__('%s.%s%s' % (cls_name,
                                      f.f_code.co_name,
                                      msg and ' - %s' % msg or ''))


# ------------------------------------------------------------------------------
#
class TypedDictMeta(type):

    # --------------------------------------------------------------------------
    #
    def __new__(mcs, name, bases, namespace):

        # guaranteed class attributes
        _base_namespace = {
            '_schema'      : {},
            '_defaults'    : {},
            '_self_default': False,  # convert unschemed-dict into class itself
            '_check'       : False,  # attribute type checking on set
            '_cast'        : True    # attempt to cast on type mismatch
        }

        for _cls in bases:
            for k in _base_namespace:
                _cls_v = getattr(_cls, k, None)
                if _cls_v is not None:
                    if   k == '_schema':
                        _base_namespace[k].update(_cls_v)
                    elif k == '_defaults':
                        _base_namespace[k].update(copy.deepcopy(_cls_v))
                    else:
                        _base_namespace[k] = _cls_v

        for k, v in _base_namespace.items():
            if isinstance(v, dict):
                v.update(namespace.get(k, {}))
                namespace[k] = v
            elif k not in namespace:
                namespace[k] = v

        return super().__new__(mcs, name, bases, namespace)


# ------------------------------------------------------------------------------
#
class TypedDict(metaclass=TypedDictMeta):

    # --------------------------------------------------------------------------
    #
    def __init__(self, from_dict=None):
        """
        Create a typed dictionary (tree) from `from_dict`.

        from_dict: data to be used for initialization

        NOTE: the names listed below are valid keys when used via the
              dictionary API, and can also be *set* via the property API, but
              they cannot be *queried* via the property API as their names
              conflict with the class method names:

                  as_dict
                  clear
                  get
                  items
                  iterkeys
                  itervalues
                  keys
                  popitem
                  setdefault
                  update
                  values
                  verify

              Names with a leading underscore are not supported.
        """
        self.__dict__['_data'] = {}
        self.update(copy.deepcopy(self._defaults))
        self.update(from_dict)

    # --------------------------------------------------------------------------
    #
    def update(self, other):
        """
        Overload `dict.update()`: the call is used to ensure that sub-dicts are
        instantiated as their respective TypedDict-inheriting class types,
        if so specified by the respective schema.

        So, if the schema contains:

          {
            ...
            'foo': BarTypedDict
            ...
          }

        where `BarTypedDict` is a valid type in the scope of the schema
        definition, which inherits from `ru.TypedDict`, then `update()` will
        ensure that the value for key `foo` is indeed of type `ru.TypedDict`.
        An error will be raised if (a) `BarTypedDict` does not have a single
        parameter constructor like `ru.TypedDict`, or (b) the `data` value for
        `foo` cannot be used as `from_dict` parameter to the `BarTypedDict`
        constructor.
        """
        if not other:
            return

        for k, v in other.items():
            # NOTE: if an attribute is of TypedDict and is needed not replace
            #       it, but rather to update it, then uncomment the next 2 lines
            # if isinstance(v, TypedDict):
            #     v = v.as_dict()
            if isinstance(v, dict):
                t = self._schema.get(k) or \
                    (type(self) if self._self_default else TypedDict)
                if isinstance(t, type) and issubclass(t, TypedDict):
                    # cast to expected TypedDict type
                    self.setdefault(k, t()).update(v)
                    continue
            self[k] = v

    # --------------------------------------------------------------------------
    #
    def __deepcopy__(self, memo):
        # return a new instance of the same type, not an original TypedDict,
        # otherwise if an instance of TypedDict-based has an attribute of other
        # TypedDict-based type then `verify` method will raise an exception
        return type(self)(from_dict=copy.deepcopy(self._data))

    # --------------------------------------------------------------------------
    #
    # base functionality to manage items
    #
    def __getitem__(self, k):
        return self._data[k]

    def __setitem__(self, k, v):
        self._data[k] = self._verify_setter(k, v)

    def __delitem__(self, k):
        del self._data[k]

    def __contains__(self, k):
        return k in self._data

    def __len__(self):
        return len(self._data)

    def keys(self):
        return self._data.keys()

    # --------------------------------------------------------------------------
    #
    def __iter__(self):
        for k in self.keys():
            yield k

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for k in self:
            yield self[k]

    def items(self):
        for k in self:
            yield k, self[k]

    # --------------------------------------------------------------------------
    #
    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
            return default
        return self[key]

    def popitem(self):
        key = list(self.keys())[0]
        value = self[key]
        del self[key]
        return key, value

    def clear(self):
        for key in self:
            del self[key]

    # --------------------------------------------------------------------------
    #
    # base functionality for attribute access
    #
    def __getattr__(self, k):

        data   = self._data
        schema = self._schema

        if   not  schema: return data.get(k)
        elif k in schema: return data.get(k)
        else            : return data[k]

    def __setattr__(self, k, v):

        # if k.startswith('_'):
        #     return object.__setattr__(self, k, v)

        self._data[k] = self._verify_setter(k, v)

    def __delattr__(self, k):

        # if k.startswith('_'):
        #     return object.__delattr__(self, k)

        del self._data[k]

    # --------------------------------------------------------------------------
    #
    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self)

    # --------------------------------------------------------------------------
    #
    @classmethod
    def _to_dict_value(cls, v):
        return v.as_dict() if isinstance(v, TypedDict) else cls.to_dict(v)

    @classmethod
    def to_dict(cls, src):
        """
        Iterate given object and apply `TypedDict.as_dict()` to all typed
        values, and return the result (effectively a shallow copy).
        """
        if isinstance(src, (dict, TypedDict)):
            tgt = {k: cls._to_dict_value(v) for k, v in src.items()}
        elif isinstance(src, list):
            tgt = [cls._to_dict_value(x) for x in src]
        elif isinstance(src, tuple):
            tgt = tuple([cls._to_dict_value(x) for x in src])
        else:
            tgt = src
        return tgt

    def as_dict(self):
        return self.to_dict(self._data)

    # obsolete method name
    @classmethod
    def demunch(cls, src):
        return cls.to_dict(src)

    # --------------------------------------------------------------------------
    #
    @classmethod
    def __raise_attr_error(cls, k, v, t, level=4):
        raise TDError(
            'attribute "%s" - expected type %s, got %s' % (k, t, type(v)),
            level=level)

    @classmethod
    def _verify_base(cls, k, v, t, cast):
        if cast:
            try:
                return t(v)
            except (TypeError, ValueError):
                pass
        cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_bool(cls, k, v, t, cast):
        if cast:
            if str(v).lower() in ['true', 'yes', '1']:
                return True
            if str(v).lower() in ['false', 'no', '0']:
                return False
        cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_tuple(cls, k, v, t, cast):
        if cast:
            v = as_tuple(v)
            return tuple([cls._verify_kvt(k + ' tuple element', _v, t[0], cast)
                          for _v in v])
        else:
            if isinstance(v, tuple):
                return v
            cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_list(cls, k, v, t, cast):
        if cast:
            v = as_list(v)
            return [cls._verify_kvt(k + ' list element', _v, t[0], cast)
                    for _v in v]
        else:
            if isinstance(v, list):
                return v
            cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_dict(cls, k, v, t, cast):
        if cast:
            t_k = list(t.keys())[0]
            t_v = list(t.values())[0]
            return {cls._verify_kvt(_k, _k, t_k, cast):
                    cls._verify_kvt(_k, _v, t_v, cast)
                    for _k, _v in v.items()}
        else:
            if isinstance(v, dict):
                return v
            cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_typeddict(cls, k, v, t, cast):
        if cast:
            if issubclass(type(v), t): return v.verify()
            if isinstance(v, dict)   : return t(from_dict=v).verify()
        else:
            if issubclass(type(v), t):
                return v
        cls.__raise_attr_error(k, v, t)

    @classmethod
    def _verify_kvt(cls, k, v, t, cast):
        if t is None or v is None: return v
        if isinstance(t, type):
            if isinstance(v, t)        : return v
            elif t in [str, int, float]: return cls._verify_base(k, v, t, cast)
            elif t is bool             : return cls._verify_bool(k, v, t, cast)
            else: cls.__raise_attr_error(k, v, t, level=3)
        if isinstance(t, tuple)    : return cls._verify_tuple(k, v, t, cast)
        if isinstance(t, list)     : return cls._verify_list(k, v, t, cast)
        if isinstance(t, dict)     : return cls._verify_dict(k, v, t, cast)
        if issubclass(t, TypedDict): return cls._verify_typeddict(k, v, t, cast)
        if cast: return v
        raise TDError('no verifier defined for type %s' % t, level=2)

    def verify(self):

        if self._schema:
            for k, v in self._data.items():

                if k.startswith('__'):
                    continue

                if k not in self._schema:
                    raise TDError('key "%s" not in schema' % k)

                self._data[k] = self._verify_kvt(k, v, self._schema[k],
                                                 self._cast)
        self._verify()
        return self

    # --------------------------------------------------------------------------
    #
    def _verify_setter(self, k, v):

        if   not self._check : return v
        elif not self._schema: return v

        if k not in self._schema:
            raise TDError('key "%s" not in schema' % k, level=2)
        return self._verify_kvt(k, v, self._schema[k], self._cast)

    # --------------------------------------------------------------------------
    #
    def _verify(self):
        """
        Can be overloaded
        """
        pass

    # --------------------------------------------------------------------------
    #
    def query(self, key, default=None, last_key=True):
        """
        For a query like

            typeddict.query('some.path.to.key', 'foo')

        this method behaves like:

            typeddict['some']['path']['to'].get('key', default='foo')

        flag `last_key` allows getting `default` value if any sub-key is missing
        (by default only if the last key is missing then return `default` value)
        """
        if not key:
            raise TDError('empty key on query')
        key_seq = key.split('.') if is_string(key) else list(key)

        output = self
        while key_seq:

            sub_key = key_seq.pop(0)

            if sub_key in output:
                output = output[sub_key]
                # if there are more sub-keys in a key sequence
                if key_seq and not isinstance(output, (dict, TypedDict)):
                    raise TDError(
                        'value for sub-key "%s" is not of dict type' % sub_key)

            elif not key_seq or not last_key:
                output = default
                break

            else:
                raise TDError('intermediate key "%s" missed' % sub_key)

        return output


# ------------------------------------------------------------------------------

to_dict = TypedDict.to_dict
# keep old name(s) for previously set calls
demunch = TypedDict.to_dict

# ------------------------------------------------------------------------------
#
# Comments:
#   - removed method `write`, which saved dict-date into JSON file
#   - removed method `merge`, which consisted of methods `ru.expand_env` and
#     `ru.dict_merge`, and which should be applied on top of TypedDict instance
#     and not to be part of it:
#
#     """
#     def merge(self, src, expand=True, env=None, policy='overwrite', log=None):
#         if expand:
#             ru.expand_env(src, env=env)
#         ru.dict_merge(self, src, policy=policy, log=log)
#     """
#
# ------------------------------------------------------------------------------