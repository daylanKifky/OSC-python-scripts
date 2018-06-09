# OSC-python-scripts
Some small python OSC applications

### Using pyOSC and python-osc
[**pyOSC**](https://trac.v2.nl/wiki/pyOSC) for python2

 and
[**python-osc**](https://pypi.python.org/pypi/python-osc) for python3

### Blender OSC-server Operator

Inside the Blender folder there's an example of an operator receiving 4 floating numbers at an specific OSC address and rotating an object with those values as a quaternion.

In order to use it you need to put the [python-osc](https://pypi.python.org/pypi/python-osc) module inside the Blender scripts/modules folder. The exact location depends on your system and version, for example:

```bash
~/.config/blender/2.77/scripts/modules/
```

Inside blender you have to run `run_in_blender.py` to register the operator.
Then you can invoke the operator from the spacebar menu, with the name `receive OSC`.
It assumes that there is an scene called 'Scene' and an object called 'Cube'.
To close the server press ESC or RMB