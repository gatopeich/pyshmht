#!python3.7
# Rough multi-process dictionary test for redis & pyshmht library by gatopeich
# Observed performance does not seem to be worth further exploration

from itertools import islice
import shmht
from multiprocessing import Process
import sys
from time import monotonic as clock


def cmdline_args(impl='dict', processes=3, worksize=1e5):
    return impl, int(processes), float(worksize)
impl, processes, worksize = cmdline_args(*sys.argv[1:])
print('Testing %s on %d processes X %g items...' % (impl, processes, worksize))


def worker(d, id):
    my_mark = (id*10)[:10]
    for i in range(int(worksize/processes)):
        d[id+str(i)] = my_mark


if impl == 'dict':
    d = dict()

elif impl == 'shmt':
    class ShmhtDict(object):
        """ Just enough to run this test """

        def __init__(self, name, capacity=300000, force_init=1):
            self.fd = shmht.open(name, int(capacity), force_init)

        def __getitem__(self, key):
            return shmht.getval(self.fd, key)

        def __setitem__(self, key, value):
            return shmht.setval(self.fd, key, value)

        def __len__(self):
            self.l = 0
            def cb(*_): self.l += 1
            shmht.foreach(self.fd, cb)
            return self.l

        def keys(self):
            keys = []
            def cb(k, v): keys.append(k)
            shmht.foreach(self.fd, cb)
            return keys
    d = ShmhtDict('/tmp/TestShmht', worksize)

elif impl == 'redis':
    import redis

    class RedisDict(redis.Redis):
        def __init__(self, socket='/tmp/testRedisDict'):
            super().__init__(unix_socket_path=socket, db=0)
            self.flushdb()
        __getitem__ = redis.Redis.get
        __setitem__ = redis.Redis.set
        __len__ = redis.Redis.dbsize
    d = RedisDict()

bg_processes = processes-1
bg_procs = [Process(target=worker, args=(d, id))
            for id in 'abcdefghijklnmo'[:bg_processes]]

t0 = clock()
worker(d, 'Foreground')
for p in bg_procs:
    p.start()
for p in bg_procs:
    p.join()
elapsed = clock() - t0
print('Elapsed %g seconds' % elapsed)
print('d[%d]:' % len(d), *('%s:%s,'%(k, d[k]) for k in islice(d.keys(), 9)))
