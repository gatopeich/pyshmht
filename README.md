pyshmht
=======

Multi-process Hash Table library for Python

Python 3.7 port by gatopeich

For examples, see test cases in python files (pyshmht/Cacher.py, pyshmht/HashTable.py), where you can find performance tests as well.


Multi-Process Performance
=========================

** Long story short: Faster than Redis at the cost of 100X memory usage, unsuitable for big tables **

See multiprocess-test.py for details. Roughly it does 3 runs over the whole dict, 1 X setting and 2 X "foreach".
The speed for ~1M ops is over 10 times worse compared to regular python dict on a single process.
Used CPU expense acounts for half of it, and the other half is spent on I/O wait so the inter-process contention seems high.
Behaviour does not seem very reliable, with some keys apparently missing at the foreach loop.

**Reference Python 3.7 native dict (single process)**
```$ python3.7 multiprocess-test.py dict 1
Testing dict on 1 processes X 100000 items...
Elapsed 0.142365 seconds
d[100000]: Foreground0:Foreground, Foreground1:Foreground, Foreground2:Foreground, Foreground3:Foreground, Foreground4:Foreground, Foreground5:Foreground, Foreground6:Foreground, Foreground7:Foreground, Foreground8:Foreground,
```

**pyshmht x 1 process**
```$ python3.7 multiprocess-test.py shmt 1
Testing shmt on 1 processes X 100000 items...
Elapsed 1.26777 seconds
d[100000]: b'Foreground75060':b'Foreground', b'Foreground75061':b'Foreground', b'Foreground75062':b'Foreground', b'Foreground75063':b'Foreground', b'Foreground75064':b'Foreground', b'Foreground75065':b'Foreground', b'Foreground75066':b'Foreground', b'Foreground75067':b'Foreground', b'Foreground75068':b'Foreground',
```

**pyshmht, splitting the load among 5 processes**
```$ python3.7 -O multiprocess-test.py shmt 5
Testing shmt on 5 processes X 100000 items...
Elapsed 0.223148 seconds
d[100000]: b'Foreground9700':b'Foreground', b'Foreground9701':b'Foreground', b'Foreground9702':b'Foreground', b'Foreground9703':b'Foreground', b'Foreground9704':b'Foreground', b'Foreground9705':b'Foreground', b'Foreground9706':b'Foreground', b'Foreground9707':b'Foreground', b'Foreground9708':b'Foreground',
```

**On the bad side, the resulting mapped file is >100X the memory required by stored objects**
```$ ll -h /tmp/TestShmht 
-rw------- 1 agustin agustin 481M Mar  2 17:15 /tmp/TestShmht
```

**Redis x 1 process**
```$ python3.7 multiprocess-test.py redis 1
Testing redis on 1 processes X 100000 items...
Elapsed 11.5978 seconds
d[100000]: b'Foreground39532':b'Foreground', b'Foreground52618':b'Foreground', b'Foreground63907':b'Foreground', b'Foreground26341':b'Foreground', b'Foreground36973':b'Foreground', b'Foreground61439':b'Foreground', b'Foreground54588':b'Foreground', b'Foreground63412':b'Foreground', b'Foreground87660':b'Foreground',
```
**Redis, splitting the load among 5 processes**
```$ python3.7 -O multiprocess-test.py redis 5
Testing redis on 5 processes X 100000 items...
Elapsed 5.59841 seconds
d[100000]: b'a10806':b'aaaaaaaaaa', b'c5713':b'cccccccccc', b'c17103':b'cccccccccc', b'c12491':b'cccccccccc', b'b9337':b'bbbbbbbbbb', b'a15722':b'aaaaaaaaaa', b'd11828':b'dddddddddd', b'Foreground18869':b'Foreground', b'Foreground12667':b'Foreground',
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
