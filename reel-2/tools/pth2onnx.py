# Converte realesr-general-x4v3.pth (SRVGGNetCompact) para ONNX sem torch.
import sys, zipfile, pickle, numpy as np, onnx
from onnx import helper, TensorProto, numpy_helper
src, dst = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src); root = z.namelist()[0].split('/')[0]
DT = {'FloatStorage': np.float32, 'HalfStorage': np.float16}
class St:
    def __init__(s, kind, key): s.kind, s.key = kind, key
def rebuild(storage, offset, size, stride, *a):
    buf = np.frombuffer(z.read(f'{root}/data/{storage.key}'), DT[storage.kind])
    n = int(np.prod(size)) if size else 1
    arr = np.lib.stride_tricks.as_strided(buf[offset:], shape=size, strides=[s*buf.itemsize for s in stride]) if size else buf[offset:offset+1]
    return np.array(arr, dtype=np.float32)
class U(pickle.Unpickler):
    def find_class(s, mod, name):
        if name == '_rebuild_tensor_v2': return rebuild
        if name.endswith('Storage'): return name
        return super().find_class(mod, name)
    def persistent_load(s, pid):
        _, kind, key, loc, n = pid; return St(kind, key)
sd = U(z.open(f'{root}/data.pkl')).load()
sd = sd.get('params', sd)
idx = sorted({int(k.split('.')[1]) for k in sd})
nodes, inits = [], []
cur = 'x'
for i in idx:
    w = sd[f'body.{i}.weight']
    if w.ndim == 4:
        inits += [numpy_helper.from_array(w, f'w{i}'), numpy_helper.from_array(sd[f'body.{i}.bias'], f'b{i}')]
        nodes.append(helper.make_node('Conv', [cur, f'w{i}', f'b{i}'], [f'y{i}'], pads=[1,1,1,1], kernel_shape=[3,3])); cur = f'y{i}'
    else:
        inits.append(numpy_helper.from_array(w.reshape(-1,1,1), f'w{i}'))
        nodes.append(helper.make_node('PRelu', [cur, f'w{i}'], [f'y{i}'])); cur = f'y{i}'
nodes.append(helper.make_node('DepthToSpace', [cur], ['ps'], blocksize=4, mode='CRD'))
inits.append(numpy_helper.from_array(np.array([1,1,4,4], np.float32), 'sc'))
nodes.append(helper.make_node('Resize', ['x', '', 'sc'], ['up'], mode='nearest'))
nodes.append(helper.make_node('Add', ['ps', 'up'], ['out']))
g = helper.make_graph(nodes, 'srvgg', [helper.make_tensor_value_info('x', TensorProto.FLOAT, [1,3,None,None])],
                      [helper.make_tensor_value_info('out', TensorProto.FLOAT, [1,3,None,None])], inits)
m = helper.make_model(g, opset_imports=[helper.make_opsetid('', 17)], ir_version=8); onnx.checker.check_model(m); onnx.save(m, dst)
print('ok', len(idx), 'camadas')
