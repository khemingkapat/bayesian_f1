import fastf1
import pandas as pd
import numpy as np


def get_raw_race_results(year):
    print(f"--- Fetching Data for {year} ---")
    schedule = fastf1.get_event_schedule(year)

    all_race_data = []

    for index, event in schedule.iterrows():
        if event["EventFormat"] == "testing":
            continue

        try:
            print(
                f"Loading {year} Round {event['RoundNumber']}: {event['EventName']}..."
            )

            session = fastf1.get_session(year, event["EventName"], "R")
            session.load(telemetry=False, weather=False, messages=False)

            results = session.results

            for _, driver in results.iterrows():
                all_race_data.append(
                    {
                        "Year": year,
                        "Round": event["RoundNumber"],
                        "Race_Name": event["EventName"],
                        "Driver_Code": driver["Abbreviation"],
                        "Team": driver["TeamName"],
                        "Finish_Position": driver["Position"],
                        "Points_Scored": driver["Points"],
                        "Status": driver["Status"],
                    }
                )
        except Exception as e:
            print(f"Skipping {event['EventName']} (Data not available yet)")

    return pd.DataFrame(all_race_data)


def _add_finished_flag(df):
    df["Finished"] = df["Status"].isin(["Finished", "Lapped"]).astype(int)
    return df


def _get_driver_skill(df_prior, prior_year):
    driver_team = df_prior.groupby("Driver_Code")["Team"].first().to_dict()

    team_points = df_prior.groupby("Team")["Points_Scored"].sum().to_dict()

    df = (
        df_prior.loc[df_prior["Finished"] == 1]
        .groupby("Driver_Code")["Points_Scored"]
        .mean()
        .reset_index()
        .sort_values(ascending=False, by="Points_Scored")
    )

    df["Team_Point"] = df["Driver_Code"].map(driver_team).map(team_points)

    mean_ppf, std_ppf = df["Points_Scored"].mean(), df["Points_Scored"].std()
    mean_tp, std_tp = df["Team_Point"].mean(), df["Team_Point"].std()

    df["Points_Scored_Z"] = (df["Points_Scored"] - mean_ppf) / std_ppf
    df["Team_Point_Z"] = (df["Team_Point"] - mean_tp) / std_tp

    df[f"Driver_Skill_{prior_year}"] = np.select(
        [
            df["Points_Scored_Z"] > 1.5,
            df["Points_Scored_Z"] > 0.5,
            df["Points_Scored_Z"] > -0.5,
        ],
        ["Elite", "Good", "Mid"],
        default="Low",
    )

    df[f"Team_Legacy_{prior_year}"] = np.select(
        [
            df["Team_Point_Z"] > 1.0,
            df["Team_Point_Z"] > -0.5,
        ],
        ["Top_Tier", "Midfield"],
        default="Backmarker",
    )

    return df[
        ["Driver_Code", f"Driver_Skill_{prior_year}", f"Team_Legacy_{prior_year}"]
    ]


def _get_reliability(df_current, current_year):
    df = df_current.groupby("Driver_Code")["Finished"].mean().reset_index()

    mean_val, std_val = df["Finished"].mean(), df["Finished"].std()
    df["Finished_Z"] = (df["Finished"] - mean_val) / std_val

    df[f"Reliability_{current_year}"] = np.select(
        [df["Finished_Z"] > -1.0],
        ["Solid"],
        default="Fragile",
    )

    return df[["Driver_Code", f"Reliability_{current_year}"]]


def _get_expected_race_pace(df_current, current_year):
    df = (
        df_current.dropna(subset=["Finish_Position"])
        .groupby("Driver_Code")["Finish_Position"]
        .mean()
        .reset_index()
    )

    df[f"Expected_Race_Pace_{current_year}"] = np.select(
        [
            df["Finish_Position"] <= 3.5,
            df["Finish_Position"] <= 10.5,
        ],
        ["P1_P3", "P4_P10"],
        default="Out_of_Points",
    )

    return df[["Driver_Code", f"Expected_Race_Pace_{current_year}"]]


def _get_championship_standing(df_current, current_year):
    df = (
        df_current.groupby("Driver_Code")["Points_Scored"]
        .sum()
        .reset_index()
        .sort_values(ascending=False, by="Points_Scored")
        .reset_index(drop=True)
    )

    df["Championship_Rank"] = df.index + 1

    df[f"Championship_Standing_{current_year}"] = np.select(
        [
            df["Championship_Rank"] <= 3,
            df["Championship_Rank"] <= 10,
        ],
        ["P1_P3", "P4_P10"],
        default="P11_P20",
    )

    return df[["Driver_Code", f"Championship_Standing_{current_year}"]]


def get_final_data(current_year):
    prior_year = current_year - 1

    df_current = _add_finished_flag(get_raw_race_results(current_year))
    df_prior = _add_finished_flag(get_raw_race_results(prior_year))

    df_skill = _get_driver_skill(df_prior, prior_year)
    df_reliability = _get_reliability(df_current, current_year)
    df_pace = _get_expected_race_pace(df_current, current_year)
    df_standing = _get_championship_standing(df_current, current_year)

    df_final = (
        df_skill.merge(df_reliability, on="Driver_Code", how="inner")
        .merge(df_pace, on="Driver_Code", how="left")
        .merge(df_standing, on="Driver_Code", how="left")
    )

    df_final[f"Expected_Race_Pace_{current_year}"] = df_final[
        f"Expected_Race_Pace_{current_year}"
    ].fillna("Out_of_Points")

    df_final[f"Championship_Standing_{current_year}"] = df_final[
        f"Championship_Standing_{current_year}"
    ].fillna("P11_P20")

    return df_final


def get_distributions(df):
    node_columns = df.columns

    dist_dict = {
        col: df[col].value_counts(normalize=True)
        for col in node_columns
        if col != "Driver_Code"
    }

    # 3. Concatenate the dictionary into a MultiIndex Series
    multi_index_series = pd.concat(dist_dict)

    # 4. Name the indexes for clean formatting
    multi_index_series.index.names = ["Variable_Name", "State"]

    # 5. Convert it into a DataFrame for better display (THE FIX IS HERE)
    df_distributions = multi_index_series.to_frame(name="Probability")

    return df_distributions


def get_all_data(year):
    df = get_final_data(year)
    df.to_csv(f"final_{year}.csv", index=False)

    dists = get_distributions(df)
    dists.to_csv(f"dists_{year}.csv")
    print(f"Data for {year} has been saved!")
