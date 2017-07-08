### Test method

Run scripts under test/ folder.

### Installation

```
python setup.py install
```

### Usage

See `/test/` for examples.
You may have to replace `/dev/ttyACM0` in `test/__init__.py` with your device name.
You can obtain this by opening uArm Studio and looking the value next to Port.
Make sure you move the device head to a safe position and completely quit uArm Studio
before running the tests.
