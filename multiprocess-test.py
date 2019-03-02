#!python3.7
# Rough concurrency test for pyshmht library by gatopeich
# Observed performance does not seem to be worth further exploration

from multiprocessing import Process
import sys
import shmht

processes = int(sys.argv[1] if len(sys.argv) > 1 else 3)
capacity  = int(sys.argv[2] if len(sys.argv) > 2 else 1e5)

print('%d processes X %g items...'%(processes, capacity))

def worker(d, id):
    my_mark = id*7
    for i in range(int(capacity/processes)):
        d[str(i)+id] = my_mark


class ShmhtDict(object):
    """ Just enough to compare shmht with a regular dict """

    def __init__(self, name, capacity=300000, force_init=0):
        self.fd = shmht.open(name, capacity, force_init)
    def __getitem__(self, key):
        return shmht.getval(self.fd, key)
    def __setitem__(self, key, value):
        return shmht.setval(self.fd, key, value)
    def __len__(self):
        self.l = 0
        def cb(*_): self.l += 1
        shmht.foreach(self.fd, cb)
        return self.l
    def items(self):
        items = []
        def cb(*kv): items.append(kv)
        shmht.foreach(self.fd, cb)
        return items


if processes < 2:
    # Single process, use regular dict
    d = dict()
    worker(d, 'A')
else:
    d = ShmhtDict('/tmp/TestShmht', capacity)
    procs = [Process(target=worker, args=(d,id)) for id in 'abcdefghijkl'[:processes]]
    for p in procs: p.start()
    for p in procs: p.join()

print('Done.')
print('d[%d]:'%len(d), *(i for r,i in zip(range(9),d.items())))
