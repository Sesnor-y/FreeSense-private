import sys, time, resource, io, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
from core.data import load_data
class U(io.BytesIO): name='bomb.xlsx'
data=open(sys.argv[1],'rb').read()
fn=getattr(load_data,"__wrapped__",None) or load_data._info.func
t=time.time(); df=fn(U(data)); dt=time.time()-t
print('shape', df.shape, f'{dt:.1f}s', 'peak RSS MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
