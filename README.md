pyshmht
=======

**Sharing memory based** Hash Table extension for Python

Python 3.7 port by gatopeich

For examples, see test cases in python files (pyshmht/Cacher.py, pyshmht/HashTable.py), where you can find performance tests as well.


Multi-Process Performance
=========================

**Long story short: Performance-wise, this library does not seem to be usable.**

See multiprocess-test.py for details. Roughly it does 3 runs over the whole dict, 1 X setting and 2 X "foreach".
The speed for ~1M ops is over 10 times worse compared to regular python dict on a single process.
Used CPU expense acounts for half of it, and the other half is spent on I/O wait so the inter-process contention seems high.
Behaviour does not seem very reliable, with some keys apparently missing at the foreach loop.

**Reference Python 3.7 native dict (single process)**
```$ time python3.7 multiprocess-test.py 1 333333
1 processes X 333333 items...
d[333333]: ('0A', 'AAAAAAA') ('1A', 'AAAAAAA') ('2A', 'AAAAAAA') ('3A', 'AAAAAAA') ('4A', 'AAAAAAA') ('5A', 'AAAAAAA') ('6A', 'AAAAAAA') ('7A', 'AAAAAAA') ('8A', 'AAAAAAA')

real	0m0.429s
user	0m0.369s
sys	0m0.060s
```

**pyshmht x 2 processes sharing the same load**
```$ time python3.7 multiprocess-test.py 2 333333
2 processes X 333333 items...
d[333327]: (b'113780a', b'aaaaaaa') (b'76930a', b'aaaaaaa') (b'76930b', b'bbbbbbb') (b'113780b', b'bbbbbbb') (b'130769a', b'aaaaaaa') (b'93919a', b'aaaaaaa') (b'93919b', b'bbbbbbb') (b'164056b', b'bbbbbbb') (b'130769b', b'bbbbbbb')

real	0m6.782s
user	0m1.547s
sys	0m4.005s
```

**pyshmht x 3 processes sharing the same load**
```$ time python3.7 multiprocess-test.py 3 333333
3 processes X 333333 items...
d[333327]: (b'76930a', b'aaaaaaa') (b'76930b', b'bbbbbbb') (b'76930c', b'ccccccc') (b'93919a', b'aaaaaaa') (b'93919b', b'bbbbbbb') (b'93919c', b'ccccccc') (b'26520a', b'aaaaaaa') (b'26520b', b'bbbbbbb') (b'26520c', b'ccccccc')
  
real	0m4.407s
user	0m1.710s
sys	0m4.708s
```

**Finally, the resulting mapped file is HUGE, expanding to 1GB for just 333333 key-values with <20 chars each**
```$ ls -lh /tmp/TestShmht
-rw------- 1 agustin agustin 961M Mar  2 00:22 /tmp/TestShmht
```

Performance
===========

capacity=200M, 64 bytes key/value tests, tested on (Xeon E5-2670 0 @ 2.60GHz, 128GB ram)

* hashtable.c (raw hash table in c, tested on `malloc`ed memory)
> set: 0.93 Million iops;  
> get: 2.35 Million iops;

* performance\_test.py (raw python binding)
> set: 451k iops;  
> get: 272k iops;

* HashTable.py (simple wrapper, no serialization)
> set: 354k iops;  
> get: 202k iops;

* Cacher.py (cached wrapper, with serialization)
> set: 501k iops (cached), 228k iops (after write\_back);  
> get: 560k iops (cached), 238k iops (no cache);

* python native dict
> set: 741k iops;  
> get: 390k iops;

Notice
======

In hashtable.c, default max key length is `256 - 4`, max value length is `1024 - 4`; you can change `bucket_size` and `max_key_size` manually, but bear in mind that increasing these two arguments will result in larger memory consumption.

If you find any bugs, please submit an issue or send me a pull request, I'll see to it ASAP :)

p.s. `hashtable.c` is independent (i.e. has nothing to do with python), you can use it in other projects if needed. :P
