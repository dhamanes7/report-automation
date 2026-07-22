"""
Builds the Monthly Accrual Master sheet, its HC pivot, and the full set of
regional output files (including the multi-tab sub-split for the region
whose config entry defines a "sub_split").

All mappings, the dept-id split rule, and the regional filter lists come
from config — nothing region/name-specific is hardcoded here.
"""
import pandas as pd


def split_dept_id(value: str, delimiter: str):
    if not isinstance(value, str) or delimiter not in value:
        return "", value
    dept_id, _, dept_name = value.partition(delimiter)
    return dept_id.strip(), dept_name.strip()


def build_master(comp_roster: pd.DataFrame, distribution_list: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    ma = cfg["monthly_accrual"]
    rename_map = ma["comp_roster_rename"]

    # Keep only the source columns we care about, then rename
    source_cols = list(rename_map.keys())
    df = comp_roster[source_cols].rename(columns=rename_map)

    # Derive Dept ID / Department Name from the combined field
    split_cfg = ma["dept_id_split"]
    ids, names = zip(*df[split_cfg["source_column"]].map(
        lambda v: split_dept_id(v, split_cfg["delimiter"])
    ))
    df[split_cfg["id_target_column"]] = ids
    df[split_cfg["name_target_column"]] = names

    # VLOOKUP-equivalent: Region + Distributee from the distribution list
    join_key = ma["distribution_list_join_key"]
    dist_lookup = distribution_list.set_index("Legislation")[["Region", "Distributee"]]
    df = df.join(dist_lookup, on=join_key)

    return df[ma["master_column_order"]]


def build_hc_pivot(master: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    hc = cfg["monthly_accrual"]["hc_pivot"]
    pivot = (
        master.groupby(hc["row_fields"] + [hc["filter_field"]])[hc["value_field"]]
        .count()
        .reset_index()
        .rename(columns={hc["value_field"]: "Headcount"})
    )
    return pivot.sort_values(hc["row_fields"])


def build_regional_outputs(master: pd.DataFrame, cfg: dict) -> dict:
    """
    Returns: { file_name: { "Master": df, "HC": df, [sub-tab name]: df, [sub-tab name + ' HC']: df, ... } }
    """
    ma = cfg["monthly_accrual"]
    results = {}

    for region_cfg in ma["regional_outputs"]:
        file_name = region_cfg["file_name"]
        distributees = region_cfg["distributees"]

        filtered = master if distributees is None else master[master["Distributee"].isin(distributees)]

        sheets = {"Master": filtered, "HC": build_hc_pivot(filtered, cfg)}

        sub_split = region_cfg.get("sub_split")
        if sub_split:
            field, values = sub_split["field"], sub_split["values"]
            for val in values:
                sub_df = filtered[filtered[field] == val]
                sheets[val] = sub_df
                sheets[f"{val} HC"] = build_hc_pivot(sub_df, cfg)

        results[file_name] = sheets

    return results
