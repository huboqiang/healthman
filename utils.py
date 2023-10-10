"""
utils for helping data analysis and plotting.
"""
import pickle
import warnings
import pandas as pd
import numpy as np
from scipy import stats

warnings.filterwarnings("ignore")

def parse_default_num(x: str) -> np.float32:
    if x is None:
        return np.nan

    l_val = x.split(";")
    l_res = []
    for val in l_val:
        val = "".join(val.split("<"))
        val = "".join(val.split(">"))
        val = "".join(val.split("+"))
        val = ".".join(val.split(".."))
        val = "".join(val.split("已复核"))
        val = "".join(val.split("复查"))
        val = "".join(val.split("已复"))
        l_res.append(val)

    try:
        x_new = np.nanmean([float(x) for x in l_res])
        return x_new
    except:
        # print("\t",x)
        return np.nan


def _parse_age_groups(age):
    if age < 30:
        return "<30"
    if age < 45:
        return "30-45"
    if age < 60:
        return "45-60"
    return ">60"


def parse_dict_with_default(val, default_dict=None):
    if default_dict is None:
        default_dict = {}

    if val in default_dict:
        return default_dict[val]

    return val


def _parse_period(line, na_val=pd.NA):
    month = line["month"]
    year = line["year"]
    if (year == 2023 and month < 7) or(year == 2022 and month >= 11):
        return "Test-2023"

    if (year == 2022 and month < 7) or(year == 2021 and month >= 11):
        return "Control-2022"

    if (year == 2021 and month < 7) or(year == 2020 and month >= 11):
        return "Control-2021"

    if isinstance(na_val, str):
        return f"{na_val}-{year}"
    
    return na_val


def extend_table1plus_data(infile):
    df_table1plus = pd.read_csv(infile, index_col=[0])

    df_table1plus["age"] = df_table1plus.apply(
                                lambda x: int(x["year"])-int(x["birthday"].split("-")[0]), axis=1
    )

    df_table1plus_q4q1 = df_table1plus.copy()
    df_table1plus_q4q1["date_column"] = df_table1plus_q4q1.apply(
                lambda x: pd.Timestamp(f"{x['year']:04d}-{x['month']:02d}-{x['day']:02d}"), axis=1
    )

    start_date0 = pd.Timestamp('2020-11-01')
    end_date0 = pd.Timestamp('2021-06-30')
    start_date1 = pd.Timestamp('2021-11-01')
    end_date1 = pd.Timestamp('2022-06-30')
    start_date2 = pd.Timestamp('2022-11-01')
    end_date2 = pd.Timestamp('2023-06-30')

    df_p0 = df_table1plus_q4q1[(df_table1plus_q4q1['date_column'] >= start_date0) &
                       (df_table1plus_q4q1['date_column'] <= end_date0)]
    df_p0["period"] = df_p0["gender"].apply(lambda x: f"20-21_{x}")

    df_p1 = df_table1plus_q4q1[(df_table1plus_q4q1['date_column'] >= start_date1) &
                       (df_table1plus_q4q1['date_column'] <= end_date1)]
    df_p1["period"] = df_p1["gender"].apply(lambda x: f"21-22_{x}")

    df_p2 = df_table1plus_q4q1[(df_table1plus_q4q1['date_column'] >= start_date2) &
                       (df_table1plus_q4q1['date_column'] <= end_date2)]
    df_p2["period"] = df_p2["gender"].apply(lambda x: f"22-23_{x}")

    df_p = pd.concat([df_p0, df_p1, df_p2])
    df_p_pvt = df_p.pivot_table(index="sample_id", values="period", aggfunc=lambda x: len(set(x)))
    l_consecute_man2p = list(df_p_pvt[df_p_pvt["period"]>1].index)
    l_consecute_man3p = list(df_p_pvt[df_p_pvt["period"]>2].index)
    return parse_man_info(df_table1plus), l_consecute_man2p, l_consecute_man3p



def parse_man_info(df_input, na_val=pd.NA):
    df = df_input.copy()
    df["age"] = df.apply(lambda x: int(x["year"])-int(x["birthday"].split("-")[0]), axis=1)
    df["year-month"] = [ f"{x:04d}-{y:02d}" for x,y in zip(df["year"], df["month"])]
    df["age_groups"] = df["age"].apply(_parse_age_groups)
    if sum(df.columns.isin(["period"])) == 0:
        df["period"] = df.apply(lambda x: _parse_period(x, na_val), axis=1)

    df["gender"] = df["gender"].apply(
            lambda x: parse_dict_with_default(x, default_dict={1:"male", 2:"female"})
    )
    df = df[~df["period"].isna()]
    df["period_age"] = df.apply(lambda x: f"{x['period']}_{x['age_groups']}", axis=1)
    return df


def _period_month_to_year(x):
    year = int(x["period"].split("-")[1])
    if x["month"] > 6:
        year -= 1

    return year


def _get_df_3periods(df_table1plus, l_consecute_man3p, main_period, l_col_all, l_col_cat, l_cols):
    df_tmp = df_table1plus[df_table1plus["sample_id"].isin(l_consecute_man3p) &
                              df_table1plus["period"].isin([main_period])].\
                pivot_table(index="sample_id", values="month", aggfunc=np.min).reset_index()

    month_dict = { k:v for k,v in zip(df_tmp["sample_id"], df_tmp["month"]) }
    df_table1plus_3periods = df_table1plus[
                        df_table1plus["sample_id"].isin(l_consecute_man3p)].copy()
    df_table1plus_3periods['month'] = [ month_dict[x] for x in df_table1plus_3periods['sample_id'] ]
    df_table1plus_3periods["year"] = df_table1plus_3periods.apply(
                    _period_month_to_year, axis=1
    )
    df_table1plus_3periods_pvt = pd.melt(df_table1plus_3periods[l_cols + l_col_all],
                                         id_vars=l_cols).\
                    pivot_table(index=l_cols, columns="variable", values="value",
                                aggfunc=np.nanmean).reset_index()

    return parse_man_info(df_table1plus_3periods_pvt)


# def update_liuzhong_health_check_data(
#         file_data="/cluster/home/bqhu_jh/projects/healthman/analysis/tableOnePlusData-final.csv",
#         file_meta="/cluster/home/bqhu_jh/projects/healthman/analysis/feature_groups_en_v3.csv"
#     ):
#     df_table1plus, l_consecute_man2p, l_consecute_man3p = extend_table1plus_data(file_data)
#     kwargs = {
#         "l_col_all" : list(df_table1plus.columns[6:-5]),
#         "l_col_cat" : list(df_table1plus.columns[-24:-5]),
#         "l_cols" : ["gender", "sample_id", "period", "month", "birthday"]
#     }

#     df_table1plus.loc[
#             df_table1plus["sample_id"]=="Mzi4RtCk8Er3epHz17cxM8ytDzhxZ9ZxW1K5NNZKUwt3ug==", "birthday"
#     ] = "1977-05-27"

#     df_table1plus_3p_rev_month = _get_df_3periods(df_table1plus, l_consecute_man3p, 
#                                                     main_period="Test-2023", **kwargs)
#     df_meta_group = pd.read_csv(file_meta)
#     df_meta_group.index = df_meta_group["item_id"]
#     rename_dict = df_meta_group["item_name_en"].to_dict()

#     output_dir = "/cluster/home/bqhu_jh/projects/healthman/analysis"
#     dict_obj = {
#         "rename_dict" : rename_dict,
#         "l_consecute_man2p" : l_consecute_man2p,
#         "l_consecute_man3p" : l_consecute_man3p
#     }
#     with open(f"{output_dir}/man_info.pickle", "wb") as f_out:
#         pickle.dump(dict_obj, f_out)

#     df_table1plus.to_parquet(f"{output_dir}/tableOnePlusData-final.parquet")
#     df_table1plus_3p_rev_month.to_parquet(f"{output_dir}/tableOnePlusData-final_3p.parquet")
#     df_meta_group.to_parquet(f"{output_dir}/feature_groups_en_v3.parquet")
#     return df_table1plus, l_consecute_man2p, l_consecute_man3p, df_table1plus_3p_rev_month,\
#                 df_meta_group, rename_dict

def quick_load_liuzhong_health_check_data(output_dir = "/cluster/home/bqhu_jh/projects/healthman/analysis"):
    df_table1plus = pd.read_parquet(f"{output_dir}/tableOnePlusData-final.parquet")
    df_meta_group = pd.read_parquet(f"{output_dir}/feature_groups_en_v3.parquet")
    df_table1plus_3p_rev_month = pd.read_parquet(f"{output_dir}/tableOnePlusData-final_3p.parquet")
    with open(f"{output_dir}/man_info.pickle", "rb") as f:
        dict_man = pickle.load(file=f)

    l_consecute_man2p = dict_man["l_consecute_man2p"]
    l_consecute_man3p = dict_man["l_consecute_man3p"]
    rename_dict = dict_man["rename_dict"]
    return df_table1plus, l_consecute_man2p, l_consecute_man3p, df_table1plus_3p_rev_month,\
                df_meta_group, rename_dict


def _get_consecute_3p(df_table1plus_final):
    df_main_q4q1 = pd.melt(df_table1plus_final, 
            id_vars=["sample_id", "year", "month", "day", "gender"]).\
        pivot_table(index=["sample_id", "year", "month", "day", "gender"],
            columns="variable", values="value"
    ).reset_index()


    df_main_q4q1["date_column"] = df_main_q4q1.apply(
                lambda x: pd.Timestamp(f"{x['year']:04d}-{x['month']:02d}-{x['day']:02d}"), axis=1
    )
    ### 测试用例：+5Or4aEsNrAnrlX7vIZ9PMytDz1xZdZxW1e4MNVNUAl3vg==
    start_date0 = pd.Timestamp('2020-11-01')
    end_date0 = pd.Timestamp('2021-10-31')
    start_date1 = pd.Timestamp('2021-11-01')
    end_date1 = pd.Timestamp('2022-10-31')
    start_date2 = pd.Timestamp('2022-11-01')
    end_date2 = pd.Timestamp('2023-06-30')

    df_p0 = df_main_q4q1[(df_main_q4q1['date_column'] >= start_date0) &
                       (df_main_q4q1['date_column'] <= end_date0)]
    df_p0["period"] = df_p0["gender"].apply(lambda x: f"20-21_{x}")

    df_p1 = df_main_q4q1[(df_main_q4q1['date_column'] >= start_date1) &
                       (df_main_q4q1['date_column'] <= end_date1)]
    df_p1["period"] = df_p1["gender"].apply(lambda x: f"21-22_{x}")

    df_p2 = df_main_q4q1[(df_main_q4q1['date_column'] >= start_date2) &
                       (df_main_q4q1['date_column'] <= end_date2)]
    df_p2["period"] = df_p2["gender"].apply(lambda x: f"22-23_{x}")

    df_p = pd.concat([df_p0, df_p1, df_p2])
    df_p_pvt = df_p.pivot_table(index="sample_id", values="period", aggfunc=lambda x: len(set(x)))
    l_consecute_man3p = list(df_p_pvt[df_p_pvt["period"]>2].index)
    l_consecute_man2p = list(df_p_pvt[df_p_pvt["period"]>1].index)
    return l_consecute_man3p, l_consecute_man2p


def _get_rev_month_3periods(df_table1plus_final, l_consecute_man3p, kwargs):

    df_table1plus_3p_rev_month = _get_df_3periods(df_table1plus_final, l_consecute_man3p, 
                                                        main_period="Test-2023", **kwargs)

    df_cnt = df_table1plus_3p_rev_month["sample_id"].value_counts().reset_index()
    l_debug = list(df_cnt[df_cnt["count"]==3]["sample_id"])

    df_table1plus_3p_rev_month = df_table1plus_3p_rev_month[
        df_table1plus_3p_rev_month["sample_id"].isin(l_debug)][
            kwargs["l_cols"]+kwargs["l_col_all"]
    ].reset_index().drop(["index"], axis=1)
    return parse_man_info(df_table1plus_3p_rev_month)


def get_3periods(df_table1plus_final, l_high_lighted, l_text_columns):
    kwargs = {
        "l_col_all" : l_high_lighted,
        "l_col_cat" : l_text_columns,
        "l_cols" : ["birthday", "year", "month", "period", "gender", "sample_id"]
    }

    l_consecute_man3p_tmp,l_consecute_man2p = _get_consecute_3p(
            df_table1plus_final[["sample_id", "year", "month", "day", "gender"]+l_high_lighted]
    )

    # fix data error to confirm "same people"
    df_table1plus_final.loc[
        df_table1plus_final["sample_id"]=="Mzi4RtCk8Er3epHz17cxM8ytDzhxZ9ZxW1K5NNZKUwt3ug==", "birthday"
    ] = "1977-05-27"
    df_table1plus_3p_rev_month = _get_rev_month_3periods(
                                    df_table1plus_final, l_consecute_man3p_tmp, kwargs
    )
    l_consecute_man3p = list(set(df_table1plus_3p_rev_month["sample_id"]))
    df_table1plus_3p_rev_month = df_table1plus_3p_rev_month[
                    df_table1plus_3p_rev_month["sample_id"].isin(l_consecute_man3p)
    ].sort_values(["gender", "sample_id"])

    df_table1plus_3p_rev_month.loc[:, l_text_columns] = df_table1plus_3p_rev_month[l_text_columns].applymap(
                                                        lambda x: 1 if x> 0 else 0
    )

    return df_table1plus_3p_rev_month, l_consecute_man2p, l_consecute_man3p

def _get_fc_pvalue_tag(tag, m_beg=1, m_end=6, l_months=None, df_meta_group=None, df_table1plus=None):
    if df_meta_group is None or df_table1plus is None:
        df_table1plus, l_consecute_man2p, l_consecute_man3p, df_table1plus_3p_revMM, df_meta_group, rename_dict =\
                                                          quick_load_liuzhong_health_check_data()

    hue = "period"
    hue_t = "Test-2023"
    hue_c1 = "Control-2022"
    hue_c2 = "Control-2021"
    month = 1
    print(df_meta_group.loc[tag]["item_name_en"])
    if m_beg == -1 or m_end == -1:
        df_p_plot = df_table1plus[[tag, "month", hue]].dropna()
        subset_t  = df_p_plot[(df_p_plot[hue] == hue_t) ][tag].dropna()
        subset_c1 = df_p_plot[(df_p_plot[hue] == hue_c1)][tag].dropna()
        subset_c2 = df_p_plot[(df_p_plot[hue] == hue_c2)][tag].dropna()

        pval = stats.ttest_ind(subset_t.values, subset_c1.values).pvalue
        print(f"All, 2023 vs 2022, fold change {subset_t.mean() / subset_c1.mean():.2f}, p={pval:.2e}, n={len(subset_t)}, {len(subset_c1)}")
        pval = stats.ttest_ind(subset_c1.values, subset_c2.values).pvalue
        print(f"All, 2022 vs 2021, fold change {subset_c1.mean() / subset_c2.mean():.2f}, p={pval:.2e}, n={len(subset_c1)}, {len(subset_c2)}")
    
    if l_months is not None:
        df_p_plot = df_table1plus[[tag, "month", hue]].dropna()
        subset_t  = df_p_plot[(df_p_plot[hue] == hue_t)  & (df_p_plot["month"].isin(l_months))][tag].dropna()
        subset_c1 = df_p_plot[(df_p_plot[hue] == hue_c1) & (df_p_plot["month"].isin(l_months))][tag].dropna()
        subset_c2 = df_p_plot[(df_p_plot[hue] == hue_c2) & (df_p_plot["month"].isin(l_months))][tag].dropna()

        pval = stats.ttest_ind(subset_t.values, subset_c1.values).pvalue
        print(f"month {l_months}, 2023 vs 2022, fold change {subset_t.mean() / subset_c1.mean():.2f}, p={pval:.2e}, n={len(subset_t)}, {len(subset_c1)}")
        pval = stats.ttest_ind(subset_c1.values, subset_c2.values).pvalue
        print(f"month {l_months}, 2022 vs 2021, fold change {subset_c1.mean() / subset_c2.mean():.2f}, p={pval:.2e}, n={len(subset_c1)}, {len(subset_c2)}")
        return
        
    for month in range(m_beg, m_end):
        df_p_plot = df_table1plus[[tag, "month", hue]].dropna()
        subset_t  = df_p_plot[(df_p_plot[hue] == hue_t)  & (df_p_plot["month"] == month)][tag].dropna()
        subset_c1 = df_p_plot[(df_p_plot[hue] == hue_c1) & (df_p_plot["month"] == month)][tag].dropna()
        subset_c2 = df_p_plot[(df_p_plot[hue] == hue_c2) & (df_p_plot["month"] == month)][tag].dropna()

        pval = stats.ttest_ind(subset_t.values, subset_c1.values).pvalue
        print(f"month {month}, 2023 vs 2022, fold change {subset_t.mean() / subset_c1.mean():.2f}, p={pval:.2e}, n={len(subset_t)}, {len(subset_c1)}")
        pval = stats.ttest_ind(subset_c1.values, subset_c2.values).pvalue
        print(f"month {month}, 2022 vs 2021, fold change {subset_c1.mean() / subset_c2.mean():.2f}, p={pval:.2e}, n={len(subset_c1)}, {len(subset_c2)}")