class ComputedValue:
    def __init__(self, store, dependencies: list, compute_fn):
        self.store = store
        self.dependencies = dependencies
        self.compute_fn = compute_fn
        self.value = None
        self.update()

    def update(self):
        args = [self.store.get(dep) for dep in self.dependencies]
        old_value = self.value
        self.value = self.compute_fn(*args)
        return self.value, old_value


class Store:
    def __init__(self, initial_state: dict):
        self._state = initial_state.copy()
        self._listeners = {}
        self._computeds = {}

    def get(self, key):
        if key in self._computeds:
            return self._computeds[key].value
        return self._state.get(key)

    def set(self, key, value):
        old_value = self._state.get(key)
        if old_value != value:
            self._state[key] = value
            self._notify(key, value, old_value)

    def derive(self, key, dependencies: list, compute_fn):
        computed = ComputedValue(self, dependencies, compute_fn)
        self._computeds[key] = computed
        
        for dep in dependencies:
            self.subscribe(dep, lambda new, old: self._update_computed(key))
            
        return computed.value

    def _update_computed(self, key):
        computed = self._computeds[key]
        new_value, old_value = computed.update()
        if new_value != old_value:
            self._notify(key, new_value, old_value)

    def subscribe(self, key, callback):
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)

    def _notify(self, key, new_val, old_val):
        if key in self._listeners:
            for callback in self._listeners[key]:
                callback(new_val, old_val)

__all__ = ["Store"]