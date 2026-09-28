spanning_by_k={}
for k in range(1,N_int+1):
    in_col=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    spanning_by_k[k]=in_col
    print(f'V_{k} column-space candidates:')
    for vector in in_col:
        print('  '+labels_by_id[id(vector)])
