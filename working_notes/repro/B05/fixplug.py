import collections
DATA={'da_chocolates_path','liking_chocolates_path','cocktail_sensory_path','cocktail_composition_path','example_data_dir','bread_path','choc_path'}
res=[]
def pytest_collection_modifyitems(session, config, items):
    c=collections.Counter(); tot=collections.Counter()
    for it in items:
        f=it.nodeid.split('::')[0]; tot[f]+=1
        if DATA & set(getattr(it,'fixturenames',[])): c[f]+=1; res.append(it.nodeid)
    open('/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B05/datadep.txt','w').write('\n'.join(res))
    print('\nTOTAL items',sum(tot.values()),'data-dependent',sum(c.values()))
    for f in sorted(tot): print(f, tot[f], c[f])
