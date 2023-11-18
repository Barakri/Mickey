import threading


class MickeyConfiguration:
    def __init__(self,
                 min_mickeys=15,
                 max_mickeys=100,
                 min_time_between_iterations=10 * 60,
                 max_time_between_iterations=60 * 60,
                 engine_rate=140,
                 volume=80):
        self._locks = {}  # type: dict

        self._min_mickeys = min_mickeys
        self._max_mickeys = max_mickeys
        self._min_time_between_iterations = min_time_between_iterations
        self._max_time_between_iterations = max_time_between_iterations

        self._engine_rate = engine_rate
        self._volume = volume

    @staticmethod
    def _lock_value(func):
        def inner(self, *args, **kwargs):
            lock_name = func.__name__
            if lock_name not in self._locks.keys():
                self._locks[lock_name] = threading.Lock()
            self._locks[lock_name].acquire()
            ret_val = func(self, *args, **kwargs)
            self._locks[lock_name].release()
            return ret_val
        return inner

    @property
    @_lock_value
    def min_mickeys(self):
        return self._min_mickeys

    @min_mickeys.setter
    @_lock_value
    def min_mickeys(self, value: int):
        self._min_mickeys = value

    def set_min_mickeys(self, value: int):
        self.min_mickeys = value

    @property
    @_lock_value
    def max_mickeys(self):
        return self._max_mickeys

    @max_mickeys.setter
    @_lock_value
    def max_mickeys(self, value: int):
        self._max_mickeys = value

    def set_max_mickeys(self, value: int):
        self.max_mickeys = value

    @property
    @_lock_value
    def min_time_between_iterations(self):
        return self._min_time_between_iterations

    @min_time_between_iterations.setter
    @_lock_value
    def min_time_between_iterations(self, value_in_seconds: int):
        self._min_time_between_iterations = value_in_seconds

    def set_min_time_between_iterations(self, value_in_seconds: int):
        self.min_time_between_iterations = value_in_seconds

    @property
    @_lock_value
    def max_time_between_iterations(self):
        return self._max_time_between_iterations

    @max_time_between_iterations.setter
    @_lock_value
    def max_time_between_iterations(self, value_in_seconds: int):
        self._max_time_between_iterations = value_in_seconds

    def set_max_time_between_iterations(self, value_in_seconds: int):
        self.max_time_between_iterations = value_in_seconds

    @property
    @_lock_value
    def engine_rate(self):
        return self._engine_rate

    @engine_rate.setter
    @_lock_value
    def engine_rate(self, value: int):
        self._engine_rate = value

    def set_engine_rate(self, value: int):
        self.engine_rate = value

    @property
    @_lock_value
    def volume(self):
        return self._volume

    @volume.setter
    @_lock_value
    def volume(self, value):
        if value < 0 or value > 100:
            raise ValueError("volume must be between 0 and 100")
        self._volume = value

    def set_volume(self, value):
        self.volume = value

    def update_configuration(self, other):
        self.min_mickeys = other.min_mickeys
        self.max_mickeys = other.max_mickeys
        self.min_time_between_iterations = other.min_time_between_iterations
        self.max_time_between_iterations = other.max_time_between_iterations

        self.engine_rate = other.engine_rate
        self.volume = other.volume

    @classmethod
    def from_other_config(cls, other):
        ret_val = cls()
        ret_val.update_configuration(other)
        return ret_val
