#!/usr/bin/python
#coding: utf-8

import shmht
import marshal

#basic wrapper: open, close, get, set, remove, foreach
#extended wrapper: getobj, setobj, [], to_dict, update

class HashTable(object):
    """
    Basic wrapper for shmht. For more information, see 'help(Cacher)'
    """
    def __init__(self, name, capacity=0, force_init=False, serializer=marshal):
        force_init = 1 if force_init else 0
        self.fd = shmht.open(name, capacity, force_init)
        self.loads = serializer.loads
        self.dumps = serializer.dumps

    def close(self):
        shmht.close(self.fd)

    def get(self, key, default=None):
        val = shmht.getval(self.fd, key)
        if val == None:
            return default
        return val

    def set(self, key, value):
        return shmht.setval(self.fd, key, value)

    def remove(self, key):
        return shmht.remove(self.fd, key)

    def foreach(self, callback, unserialize=False):
        if not unserialize:
            cb = callback
        else:
            loads = self.loads
            def mcb(key, value):
                return callback(key, loads(value))
            cb = mcb
        return shmht.foreach(self.fd, cb)

    def getobj(self, key, default=None):
        val = self.get(key, default)
        if val == default:
            return default
        return self.loads(val)

    def setobj(self, key, val):
        val = self.dumps(val)
        return self.set(key, val)

    def __getitem__(self, key):
        val = shmht.getval(self.fd, key)
        if val == None:
            raise KeyError(key)
        return val

    def __setitem__(self, key, value):
        return shmht.setval(self.fd, key, value)

    def __delitem__(self, key):
        if False == shmht.remove(self.fd, key):
            raise KeyError(key)

    def __contains__(self, key):
        return shmht.getval(self.fd, key) != None

    def to_dict(self, unserialize=False):
        d = {}
        def insert(k,v):
            d[k.decode()] = v
        self.foreach(insert, unserialize)
        return d

    def update(self, d, serialize=False):
        dumps = self.dumps
        if serialize:
            for k in d:
                self[k] = dumps(d[k])
        else:
            for k in d:
                self[k] = d[k]

if __name__ == "__main__":
    loads = marshal.loads
    dumps = marshal.dumps
    #test cases
    ht = HashTable('/dev/shm/test.HashTable', 1024, 1)

    #set
    ht['a'] = '1'
    ht.set('b', '2')
    c = {'hello': 'world'}
    ht.setobj('c', c)

    #get
    assert ht['b'] == b'2'
    assert ht['c'] == marshal.dumps(c)
    assert ht.getobj('c') == c
    assert ht.get('d') is None
    try:
        ht['d']
        assert False
    except: pass

    #contains
    assert 'c' in ht
    assert 'd' not in ht

    #del
    del ht['c']
    assert ht.get('c') is None
    try:
        del ht['d']
        assert False
    except: pass

    #update & to_dict & foreach
    ht.setobj('c', c)
    print(repr(ht.to_dict()))
    assert ht.to_dict() == {'a': b'1', 'b': b'2', 'c': dumps(c)}

    s = b''
    def cb(key, value):
        global s
        s += key + value
        print("key: %r, value: %r, s: %r" % (key,value, s))
    ht.foreach(cb)
    print(s)
    assert s == b'a1b2c' + dumps(c)

    ht.update({'a': 1, 'b': 2, 'c': c}, serialize=True)
    s = ''
    def cb2(key, value):
        global s
        s += key.decode() + str(value)
        print("key: %r, value: %r, s: %r" % (key,value, s))
    ht.foreach(cb2, unserialize=True)
    assert s == 'a1b2c' + str(c)

    assert ht.to_dict() == {'a':dumps(1), 'b':dumps(2), 'c':dumps(c)}
    assert ht.to_dict(unserialize=True) == {'a': 1, 'b': 2, 'c': c}

    #close
    ht.close()
    try:
        ht['a']
        assert False
    except: pass

    #simple performance test
    import time

    capacity = 300000

    #write_through
    ht = HashTable('/dev/shm/test.HashTable', capacity, True)

    begin_time = time.time()
    for i in range(capacity):
        s = str(i)
        ht[s] = s
    end_time = time.time()
    print(capacity / (end_time - begin_time), 'iops @ set')

    begin_timend_time = time.time()
    for i in range(capacity):
        s = str(i)
        assert s == ht[s].decode()
    end_time = time.time()
    print(capacity / (end_time - begin_time), 'iops @ get')

    ht.close()
