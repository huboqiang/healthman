"""
utils for helping data analysis and plotting.
"""
import pickle
import warnings
import pandas as pd
import numpy as np

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


def _parse_period(line):
    month = line["month"]
    year = line["year"]
    if (year == 2023 and month < 7) or(year == 2022 and month >= 11):
        return "Test-2023"

    if (year == 2022 and month < 7) or(year == 2021 and month >= 11):
        return "Control-2022"

    if (year == 2021 and month < 7) or(year == 2020 and month >= 11):
        return "Control-2021"

    return pd.NA


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



def parse_man_info(df):
    # df["year", "month", "birthday", "gender"]
    df["age"] = df.apply(lambda x: int(x["year"])-int(x["birthday"].split("-")[0]), axis=1)
    df["year-month"] = [ f"{x:04d}-{y:02d}" for x,y in zip(df["year"], df["month"])]
    df["age_groups"] = df["age"].apply(_parse_age_groups)
    if sum(df.columns.isin(["period"])) == 0:
        df["period"] = df.apply(_parse_period, axis=1)

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
#         file_meta="/cluster/home/bqhu_jh/projects/healthman/analysis/feature_groups_en_v2.csv"
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
#     df_meta_group.to_parquet(f"{output_dir}/feature_groups_en_v2.parquet")
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

    start_date0 = pd.Timestamp('2020-11-01')
    end_date0 = pd.Timestamp('2021-06-30')
    start_date1 = pd.Timestamp('2021-11-01')
    end_date1 = pd.Timestamp('2022-06-30')
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
    l_consecute_man3p = list(set(df_table1plus_3p_rev_month["sample_id"])-set([
        'Y+M9pyDDUb/O3lAx+N7Q1cytDz5zY9ZxWlO5MNZNUwZ1tw==',
        'duz34LQLja8FwtfyygH8/MytDzhxZdZxWV25MNZLUwh0vw==',
        'ht5uJZVXoxYJzr6KdEAmnsytDzlxY9ZxWla5NdROUwpyvA==',
        'qz++/ZdSuOE7PVjMWJDwCsytDzhxY9ZxVFa4MNRJUg50uA==',
        'hCqkUaauIIIDhnHFiczO+sytDz5xZtZxW1K5ONVNUg53vw==',
        'FrVD7wxSL3iF8kHspI9DNcytDTpxZdZxWlS4MNVJUg50uQ==',
        '7jPoASQAbYjLorgnF8LRgsyvDz5zZNZxWlC5NNVEUwx1ug==',
        'DHAkEPIRf5/38Pdh6Ki7uMytDzlxYtZxWlG5N9ZFWg5xuQ==',
        'dlfiLvydqIewAvQ+Io6KnsyqDTZxYNZxW124MdVNUgp3vg==',
        'C4MlkVn8L/a4cV98SVx0Q8ytDTpxY9ZxVVS5OdZIWwt2vQ==',
        'HJAqe9Dx8TNQpUFSh62QHsytBj9yYNZxW1O4M9RMVQZ01g==',
        'O71fadyWKYsKEHm//a4Q88ytDTpxZdZxWlW5NtZKUg53uA==',
        'LD7yAYFSExov51hFO3VjDMytDz5zYtZxVFy5OdRIUg53ug==',
        'PN/uDmSQYba7y0Afo4YCysytBj9zZNZxVFy4M9ROVQ91vQ==',
        'Z6bmlmH53Oi9ao/5yLplfcytDz57YtZxVFO5NdZNUg5+tw==',
        'OW+dEJRskMCjPNRun5LTccytDz5zZNZxVFa5NdZFUAtwvA==',
        '/3N8RjrsxFJyjahmMN8v5MytDzxxZ9ZxWlG4MNREUgl3vw==',
        'MUAtoIFxTwGB/ygmDINslMytDzx7Y9ZxVFG4MdRMUgd/ug==',
        'iQUFce3p0qJ05NbzsA6yWsuvDztxYNZxVVS5NdRIUg50vg=='
    ]))

    df_table1plus_3p_rev_month = df_table1plus_3p_rev_month[
                    df_table1plus_3p_rev_month["sample_id"].isin(l_consecute_man3p)
    ].sort_values(["gender", "sample_id"])

    df_table1plus_3p_rev_month.loc[:, l_text_columns] = df_table1plus_3p_rev_month[l_text_columns].applymap(
                                                        lambda x: 1 if x> 0 else 0
    )

    return df_table1plus_3p_rev_month, l_consecute_man2p, l_consecute_man3p
