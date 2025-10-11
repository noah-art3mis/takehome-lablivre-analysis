import pandas as pd


def check_duplicates(df: pd.DataFrame) -> None:
    """
    Check for duplicates in a DataFrame that contains list columns.
    Creates copies with and without list columns to analyze duplicates.

    Args:
        df: DataFrame to check for duplicates
    """
    # Find columns containing lists
    list_cols = [
        col for col in df.columns if df[col].apply(lambda x: isinstance(x, list)).any()
    ]
    print(f"Columns with lists: {list_cols}")

    # Check duplicates ignoring list columns
    df_no_lists = df.copy()
    df_no_lists.drop(columns=list_cols, inplace=True)
    dup_count = df_no_lists.duplicated().sum()
    print(f"Number of duplicate rows (not considering list columns): {dup_count}")

    # Check duplicates with stringified lists
    df_str = df.copy()
    for col in list_cols:
        df_str[col] = df_str[col].apply(lambda x: str(x) if isinstance(x, list) else x)

    duplicates = df_str.duplicated()
    print(f"Number of duplicate rows: {duplicates.sum()}")


def analyze_false_duplicates(df: pd.DataFrame, output_file: str) -> None:
    """
    Analyze records that appear as duplicates in scalar columns but have differences in list columns.
    Writes findings to duplicate_records_report.txt

    Args:
        df: DataFrame containing the records to analyze
    """
    # Create copy with no list columns to check scalar duplicates
    list_cols = [
        col for col in df.columns if df[col].apply(lambda x: isinstance(x, list)).any()
    ]
    df_no_lists = df.copy()
    df_no_lists.drop(columns=list_cols, inplace=True)

    # Create copy with stringified lists to check full duplicates
    df_str = df.copy()
    for col in list_cols:
        df_str[col] = df_str[col].apply(lambda x: str(x) if isinstance(x, list) else x)

    # Find the "false duplicates" - duplicate in scalar columns but different in list columns
    false_dup_mask = df_no_lists.duplicated(keep=False) & ~df_str.duplicated(keep=False)
    false_dups = df[false_dup_mask]

    print(f"Number of 'false duplicate' rows: {len(false_dups)}")
    print(
        f"Unique idUnico values in false duplicates: {false_dups['idUnico'].nunique()}"
    )

    report_rows = []

    # For each unique idUnico value
    for id_unico in false_dups["idUnico"].unique():
        # Get all rows with this idUnico
        example_rows = df[df["idUnico"] == id_unico]

        # Check which list columns differ
        list_cols = [
            "tomadores",
            "executores",
            "repassadores",
            "eixos",
            "tipos",
            "subTipos",
            "fontesDeRecurso",
        ]

        differing_cols = []
        col_values = {}

        for col in list_cols:
            unique_values = example_rows[col].apply(str).unique()
            if len(unique_values) > 1:
                differing_cols.append(col)
                col_values[col] = []
                for i, row in example_rows.iterrows():
                    col_values[col].append({"row_index": i, "value": row[col]})

        report_rows.append(
            {
                "idUnico": id_unico,
                "differing_columns": differing_cols,
                "values": col_values,
            }
        )

    # Write report to file
    with open(f"{output_file}.txt", "w") as f:
        f.write("Report of Records with Differing List Values\n")
        f.write("==========================================\n\n")

        for row in report_rows:
            f.write(f"idUnico: {row['idUnico']}\n")
            f.write(
                "Differing columns: " + ", ".join(row["differing_columns"]) + "\n\n"
            )

            for col in row["differing_columns"]:
                f.write(f"{col}:\n")
                for val in row["values"][col]:
                    f.write(f"  Row {val['row_index']}: {val['value']}\n")
            f.write("\n" + "=" * 50 + "\n\n")

    print(f"Report written to duplicate_records_report.txt")
