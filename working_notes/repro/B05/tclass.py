import ast,glob,re,collections
NUM=re.compile(r'approx|isclose|allclose|assert_frame_equal|assert_series_equal|assert_array|abs\(|< ?1e-|<= ?1e-|==\s*-?\d+\.\d|\b0\.\d+\b|== ?\d+\b')
tot=collections.Counter()
for tf in sorted(glob.glob('tests/test_*.py')):
    src=open(tf).read(); tree=ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'):
            s=ast.get_source_segment(src,n)
            a=[l.strip() for l in s.splitlines() if re.search(r'\bassert\b|pytest.raises',l)]
            k='NUM' if any(NUM.search(l) for l in a) else ('STRUCT' if a else 'NOASSERT')
            tot[k]+=1
            print(k, tf, n.name, len(a))
print(tot)
