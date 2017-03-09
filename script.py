

def mapping(df_day, df_min):
    mapping_num = []
    mapping_table = []
    for i in range(len(df_day)):

        start = df_day.ix[i].start_date
        end = df_day.ix[i].end_date
        mapping_df = df_min[
            (df_min.start_date >= start) & (
                df_min.end_date <= end)]

        if not mapping_df.empty:
            a = mapping_df.index[0]
            b = mapping_df.index[-1]
            print i

        else:
            mapping_table.append(mapping_df)
            mapping_num.append(1)
            continue

        if df_min.ix[b].bd_type == df_day.ix[i].bd_type and df_min.ix[
                a].bd_type != df_day.ix[i].bd_type:
            mapping_df = df_min.ix[a - 1:b]
        if df_min.ix[a].bd_type == df_day.ix[i].bd_type and df_min.ix[
                b].bd_type != df_day.ix[i].bd_type:
            mapping_df = df_min.ix[a:b + 1]
        if df_min.ix[a].bd_type != df_day.ix[i].bd_type and df_min.ix[
                b].bd_type != df_day.ix[i].bd_type:
            mapping_df = df_min.ix[a - 1:b + 1]

        if df_day.ix[i].bd_type == "decline":
            for j in list(mapping_df.index[:-2]):
                if j not in mapping_df.index:
                    continue
                bd = mapping_df.ix[j]
                if bd.bd_type == "decline":
                    if bd.end_price > mapping_df.end_price.ix[:j].min():
                        bdp2 = mapping_df.ix[j + 2]
                        mapping_df = mapping_df.drop(j)
                        mapping_df = mapping_df.drop(j + 1)
                        mapping_df = mapping_df.drop(j + 2)
                        mapping_df.ix[j] = {
                            'start_point': bd.start_point,
                            'end_point': bdp2.end_point,
                            'start_date': bd.start_date,
                            'end_date': bdp2.end_date,
                            'start_price': bd.start_price,
                            'end_price': bdp2.end_price,
                            'comfirmpoint': bd.comfirmpoint,
                            'prevtime': bd.prevtime,
                            'aftertime': bdp2.end_point - bd.comfirmpoint,
                            'timedelta': bdp2.end_point - bd.start_point,
                            'bd_type': 'decline',
                            'comfirm_date': bd.comfirm_date,
                            'comfirm_price': bd.comfirm_price,
                            'returns': bdp2.end_price / bd.start_price - 1,
                            'prevreturns': bd.comfirm_price / bd.start_price - 1,
                            'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                            'continue_ratio': (
                                bd.comfirm_price / bd.start_price - 1) / (
                                bdp2.end_price / bd.comfirm_price - 1)}

                        mapping_df = mapping_df.sort_index()

        elif df_day.ix[i].bd_type == "raise":
            for j in list(mapping_df.index[:-2]):
                if j not in mapping_df.index:
                    continue
                bd = mapping_df.ix[j]
                if bd.bd_type == "raise":
                    if bd.end_price < mapping_df.end_price.ix[:j].max():
                        bdp2 = mapping_df.ix[j + 2]
                        mapping_df = mapping_df.drop(j)
                        mapping_df = mapping_df.drop(j + 1)
                        mapping_df = mapping_df.drop(j + 2)
                        mapping_df.ix[j] = {
                            'start_point': bd.start_point,
                            'end_point': bdp2.end_point,
                            'start_date': bd.start_date,
                            'end_date': bdp2.end_date,
                            'start_price': bd.start_price,
                            'end_price': bdp2.end_price,
                            'comfirmpoint': bd.comfirmpoint,
                            'prevtime': bd.prevtime,
                            'aftertime': bdp2.end_point - bd.comfirmpoint,
                            'timedelta': bdp2.end_point - bd.start_point,
                            'bd_type': 'decline',
                            'comfirm_date': bd.comfirm_date,
                            'comfirm_price': bd.comfirm_price,
                            'returns': bdp2.end_price / bd.start_price - 1,
                            'prevreturns': bd.comfirm_price / bd.start_price - 1,
                            'afterreturns': bdp2.end_price / bd.comfirm_price - 1,
                            'continue_ratio': (
                                bd.comfirm_price / bd.start_price - 1) / (
                                bdp2.end_price / bd.comfirm_price - 1)}

                        mapping_df = mapping_df.sort_index()

        mapping_table.append(mapping_df)
        mapping_num.append(mapping_df.shape[0])
    return mapping_num, mapping_table

def misplace(min_boduan, day_boduan, min_close, day_close):
    deccline_after = []
    raise_after = []
    decline_prev = []
    raise_prev = []
    for i in range(min_boduan.shape[0] - 3):
        n1 = min_boduan.iloc[i]
        n3 = min_boduan.iloc[i + 2]
        n4 = min_boduan.iloc[i + 3]
        bd_type = n1.bd_type
        temp = day_boduan[day_boduan.bd_type == bd_type]
        temp = temp[temp.start_date < n1.end_date]
        if temp.empty:
            continue
        A = temp.iloc[-1].comfirm_date
        e = n4.comfirm_date
        a = n1.start_date
        c = n3.start_date
        b = n1.end_date
        d = n3.end_date
        Pb = min_close.ix[b]
        Pd= min_close.ix[d]
        Ae = day_close.ix[A:e]
        if Ae.empty:
            continue
        B1 = Ae.idxmin()
        B2 = Ae.idxmax()
        if Pb > Pd:
            if temp.iloc[-1].bd_type == "decline" and  a <= B1 <= c:
                deccline_after.append(e)

            if temp.iloc[-1].bd_type == "raise" and  c<= B2 <= e:
                raise_prev.append(e)

        if Pb < Pd:
            if temp.iloc[-1].bd_type == "decline" and c<= B1 <= e:
                decline_prev.append(e)

            if temp.iloc[-1].bd_type == "raise" and a<= B2 <= c:
                raise_after.append(e)

    return decline_prev, deccline_after, raise_prev, raise_after
