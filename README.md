### The new python library for UFACTORY

Currently only support Swift / Swift PRO,
and it's python3 only.

There are two ways to use this library:

- Using the API wrapper just like the old `pyuarm` library,
  reference to [Swift API document](doc/swift_api.md), and [test/test_swift_api.py](test/test_swift_api.py).
- Using the [Modular Programming](doc/modular.md) prototype, and checkout all other scripts under `test/` folder.

#### Attention

Make sure you move the device head to a safe position and completely quit uArm Studio
before running the tests.

#### Installation

```
python3 setup.py install
```

Install is not necessary, you can run test scripts without installation.
