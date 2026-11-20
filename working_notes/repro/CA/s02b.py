exec(open('/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/s02.py').read().split('dis=tot=0')[0])
d=sim(0); L=compute_liking_lmm(d,cm,1,9); pooled=math.sqrt(L['lmm_result'].scale)
m=methods[2]
print(compute_liking_cld(L['lmm_summary'],L['cov_lsmeans'],L['df_satterthwaite'],0.05,m))
c=compute_contrast(d,cm,L['lmm_summary'],reference_product='P1',comparison_products=['P2','P3','P4','P5','P6'],alpha=0.05,module='Liking',post_hoc_method=m,lmm_cov_params=L['cov_lsmeans'],df_satterthwaite=L['df_satterthwaite'],liking_pooled_sd=pooled)
print(c[['comparison','raw_diff','se_diff','p_value','significant','out_of_spec']])
for df_ in (4,18,45):
    print(df_, [round(2*ss.t.sf(abs(x)/s,df_),4) for x,s in zip(c.raw_diff,c.se_diff)])
