"""
Builds the Addition & Deletion workbook from three source files:
functional_info, personal_info (DOB only), terminations
(+ prior_month_functional_info, used only to backfill Company Name for leavers).

All column names/mappings come from config — no hardcoded client field names.
"""
import pandas as pd


def _filter_by_date_range(df: pd.DataFrame, column: str, date_from, date_to) -> pd.DataFrame:
    if date_from is None and date_to is None:
        return df

    dates = pd.to_datetime(df[column])
    mask = pd.Series(True, index=df.index)
    if date_from is not None:
        mask &= dates >= pd.Timestamp(date_from)
    if date_to is not None:
        mask &= dates <= pd.Timestamp(date_to)

    return df[mask].reset_index(drop=True)


def build_addition_sheet(
    functional_info: pd.DataFrame,
    personal_info: pd.DataFrame,
    cfg: dict,
    date_from=None,
    date_to=None,
) -> pd.DataFrame:
    ad = cfg["addition_deletion"]
    mapping = ad["addition_mapping"]

    # Filter to the requested Hire Date range before anything else, so the DOB
    # join and mismatch check below only ever see the filtered subset.
    functional_info = _filter_by_date_range(functional_info, "Hire Date", date_from, date_to)

    out = pd.DataFrame()
    for target_col, source_col in mapping.items():
        out[target_col] = functional_info[source_col]

    # DOB comes from a separate source file, joined on person number
    dob_cfg = ad["dob_source"]
    dob_lookup = personal_info.set_index(dob_cfg["join_key"])[dob_cfg["column"]]
    out[dob_cfg["target_column"]] = functional_info[dob_cfg["join_key"]].map(dob_lookup)

    # QA check: Business Unit Name vs Legal Employer Name mismatch flag
    mm = ad["company_mismatch_check"]
    if mm["column_a"] in functional_info.columns and mm["column_b"] in functional_info.columns:
        out[mm["flag_column"]] = (
            functional_info[mm["column_a"]] != functional_info[mm["column_b"]]
        ).map({True: "MISMATCH", False: ""})

    return out[ad["addition_output_columns"] + ([mm["flag_column"]] if mm["flag_column"] not in ad["addition_output_columns"] else [])]


def build_deletion_sheet(
    terminations: pd.DataFrame,
    prior_month_functional_info: pd.DataFrame,
    cfg: dict,
    date_from=None,
    date_to=None,
) -> pd.DataFrame:
    ad = cfg["addition_deletion"]
    mapping = ad["deletion_mapping"]

    # Filter to the requested Last day in service range before anything else,
    # so the Company Name backfill below only ever sees the filtered subset.
    terminations = _filter_by_date_range(terminations, "Last day in service", date_from, date_to)

    out = pd.DataFrame()
    for target_col, source_col in mapping.items():
        out[target_col] = terminations[source_col]

    out["Comments"] = ""

    # Company Name backfilled from prior month's functional info (terminations report has no company field)
    lk = ad["deletion_company_lookup"]
    lookup = prior_month_functional_info.set_index(lk["join_key"])[lk["column"]]
    out[lk["target_column"]] = terminations[lk["join_key"]].map(lookup)

    return out[ad["deletion_output_columns"]]


def build_addition_deletion_workbook(
    functional_info,
    personal_info,
    terminations,
    prior_month_functional_info,
    cfg,
    date_from=None,
    date_to=None,
):
    addition = build_addition_sheet(functional_info, personal_info, cfg, date_from=date_from, date_to=date_to)
    deletion = build_deletion_sheet(terminations, prior_month_functional_info, cfg, date_from=date_from, date_to=date_to)
    return {"Addition": addition, "Deletion": deletion}
