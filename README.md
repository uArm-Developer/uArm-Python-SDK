### The new python library for UFACTORY

Currently only support Swift / Swift PRO,
and it's python3 only.

There are two ways to use this library:

- Using the API wrapper just like the old `pyuarm` library,
  reference to [Swift API document](doc/swift_api.md), and scripts under `examples/fashion_api/` folder.
- Using the [Modular Programming](doc/modular.md) prototype, and checkout scripts under `examples/fashion_modular/` folder.

#### Attention

Make sure you move the device head to a safe position and completely quit uArm Studio
before running the tests.

#### Installation

```
python3 setup.py install
```

Install is not necessary, you can run examples without installation.
