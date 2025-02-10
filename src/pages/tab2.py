from dash import Dash, html, dcc, callback, Output, Input, State, register_page
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import re
import pathlib

from data import df, dfnz2

# import dash_auth
# import dash_mantine_components as dmc

register_page(__name__, title="Data Simulation", path="/tab2")


def company_list_from_sector(sector):
    company_list = []
    dfk = df[df["GICS.Sector"].isin([sector])]
    company_list = dfk["Company.Name"].tolist()
    return company_list


def index_calculator(
    sector,
    company_list,
    governance_weight,
    goals_weight,
    performance_weight,
    firm_ind,
    new_firm_perf,
    new_firm_gov,
    new_firm_goal,
):

    emg1 = df.loc[:, ["Company.Name", "Audited.Report", "TCFD New"]]
    emg1.rename(
        columns={
            "Company.Name": "Company",
            "Audited.Report": "GHG Assurance",
            "TCFD New": "TCFD Disclosure",
        },
        inplace=True,
    )

    mask = emg1["Company"].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: "Yes", 0.5: "Partial", 0.0: "No"}
    emg1["GHG Assurance"] = emg1["GHG Assurance"].map(categorical_mapping)
    emg1["TCFD Disclosure"] = emg1["TCFD Disclosure"].map(categorical_mapping)

    emg2 = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?",
            "Is Executive Compensation tied to any ESG milestones?",
        ],
    ]
    emg2.rename(
        columns={
            "Enter the full company name": "Company",
            "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
            "Is Executive Compensation tied to any ESG milestones?": "Executive Compensation tied to ESG milestones",
        },
        inplace=True,
    )

    mask = emg2["Company"].isin(company_list)
    emg2 = emg2[mask]

    emg = emg1.merge(emg2, on="Company")

    # emg = enviromentalgovernacemetrics(sector,company_list)[1]
    emg22 = emg.copy()

    # encoding all the categorical variables with the mapping 1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'
    categorical_mapping = {"Yes": 1.0, "Partial": 0.5, "No": 0.0}
    emg22["GHG Assurance"] = emg["GHG Assurance"].map(categorical_mapping)
    emg22["TCFD Disclosure"] = emg["TCFD Disclosure"].map(categorical_mapping)
    emg22["Environmental Skill as key board competency"] = emg[
        "Environmental Skill as key board competency"
    ].map(categorical_mapping)
    emg22["Executive Compensation tied to ESG milestones"] = emg[
        "Executive Compensation tied to ESG milestones"
    ].map(categorical_mapping)

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        emg22.loc[len(emg22)] = new_firm_gov

    #################################

    # Creating a new column 'index' having the average of all the categorical variables
    emg22["index"] = emg22[
        [
            "GHG Assurance",
            "TCFD Disclosure",
            "Environmental Skill as key board competency",
            "Executive Compensation tied to ESG milestones",
        ]
    ].mean(axis=1)
    emg22 = emg22.sort_values(by="index", ascending=False)

    single_gov_score = (
        emg22.loc[emg22["Company"] == new_firm_gov[0], "index"].values[0].round(2)
    )

    egoal = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "Does the company have a Net Zero/carbon neutrality goal?",
            "Does the Net Zero goal cover Scope 1 emissions?",
            "Does the Net Zero goal cover Scope 2 emissions?",
            "Does the Net Zero goal cover all of Scope 3 emissions?",
            "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?",
            "What is the status of the company's goal with the Science Based Target Institute?",
            "Does the company have an interim goal on the way to Net Zero?",
            'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?',
        ],
    ]
    egoal.rename(
        columns={
            "Enter the full company name": "Company",
            "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
            "Does the Net Zero goal cover Scope 1 emissions?": "NZG covers Scope 1 emissions",
            "Does the Net Zero goal cover Scope 2 emissions?": "NZG covers Scope 2 emissions",
            "Does the Net Zero goal cover all of Scope 3 emissions?": "NZG covers all of Scope 3 emissions",
            "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?": "Working with the SBTI ",
            "What is the status of the company's goal with the Science Based Target Institute?": "Status of the goal with SBTI",
            "Does the company have an interim goal on the way to Net Zero?": "Has an interim goal on the way to Net Zero",
            'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?': '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement',
        },
        inplace=True,
    )

    mask = egoal["Company"].isin(company_list)
    egoal = egoal[mask].fillna("Not Applicable")

    # egoal.loc[222,'"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = 'Not Applicable'

    # egoal = environmentalgoals(sector,company_list)[1]
    egoal22 = egoal.copy()
    categorical_mapping2 = {
        "Yes": 1.0,
        "Committed": 1.0,
        "No": 0.0,
        "Not Applicable": 0.0,
        "Validated": 0.5,
    }
    egoal22["Has a Net Zero Goal (NZG)"] = egoal["Has a Net Zero Goal (NZG)"].map(
        categorical_mapping2
    )
    egoal22["NZG covers Scope 1 emissions"] = egoal["NZG covers Scope 1 emissions"].map(
        categorical_mapping2
    )
    egoal22["NZG covers Scope 2 emissions"] = egoal["NZG covers Scope 2 emissions"].map(
        categorical_mapping2
    )
    egoal22["NZG covers all of Scope 3 emissions"] = egoal[
        "NZG covers all of Scope 3 emissions"
    ].map(categorical_mapping2)
    egoal22["Working with the SBTI "] = egoal["Working with the SBTI "].map(
        categorical_mapping2
    )
    egoal22["Status of the goal with SBTI"] = egoal["Status of the goal with SBTI"].map(
        categorical_mapping2
    )
    egoal22["Has an interim goal on the way to Net Zero"] = egoal[
        "Has an interim goal on the way to Net Zero"
    ].map(categorical_mapping2)
    egoal22['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = egoal[
        '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'
    ].map(categorical_mapping2)

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        egoal22.loc[len(egoal22)] = new_firm_goal

    #################################

    egoal22["index"] = egoal22[
        [
            "Has a Net Zero Goal (NZG)",
            "NZG covers Scope 1 emissions",
            "NZG covers Scope 2 emissions",
            "NZG covers all of Scope 3 emissions",
            "Working with the SBTI ",
            "Status of the goal with SBTI",
            "Has an interim goal on the way to Net Zero",
            '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement',
        ]
    ].mean(axis=1)
    egoal22 = egoal22.sort_values(by="index", ascending=False)

    single_goal_score = (
        egoal22.loc[egoal22["Company"] == new_firm_gov[0], "index"].values[0].round(2)
    )

    envperf = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)",
            "Enter the company's Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)",
            "Enter the company's Scope 3 emissions in metric tons of CO2e.",
        ],
    ]
    envperf.rename(
        columns={
            "Enter the full company name": "Company",
            "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1",
            "Enter the company's Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
            "Enter the company's Scope 3 emissions in metric tons of CO2e.": "Total GHG3",
        },
        inplace=True,
    )

    #     envperf2 = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM10c.Response','CM10a.Response','CM9.Area.in.hectares']]
    #     envperf2 = envperf2.rename(columns={"Company.Name":"Company","CM10c.Response":"Water Consumption"
    #                                     ,"CM10a.Response":"Water Withdrawal","CM9.Area.in.hectares":"Biodiversity Areas"})
    envperf2 = df.loc[
        :,
        [
            "GICS.Sector",
            "Company.Name",
            "Revenue",
            "CM10a.Response",
            "CM9.Area.in.hectares",
        ],
    ]
    envperf2 = envperf2.rename(
        columns={
            "Company.Name": "Company",
            "CM10a.Response": "Water Withdrawal",
            "CM9.Area.in.hectares": "Biodiversity Areas",
        }
    )

    envperf_merged = envperf.merge(envperf2, on="Company", how="right")
    envperf_merged.loc[
        envperf_merged["Company"] == "Yum! Brands, Inc.", "Total GHG1"
    ] = 4291918

    mask8 = envperf_merged["Company"].isin(company_list)
    envperf_merged = envperf_merged[mask8]

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        envperf_merged.loc[len(envperf_merged)] = new_firm_perf

    #################################

    envperf_merged["Normalized GHG1"] = (
        pd.to_numeric(envperf_merged["Total GHG1"]) / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized GHG2"] = (
        envperf_merged["Total market-based GHG2"] / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized GHG3"] = (
        envperf_merged["Total GHG3"] / envperf_merged["Revenue"]
    )
    # envperf_merged['Normalized Water Consumption'] = envperf_merged['Water Consumption']/envperf_merged['Revenue']
    envperf_merged["Normalized Water Withdrawal"] = (
        envperf_merged["Water Withdrawal"] / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized Biodiversity Areas"] = (
        envperf_merged["Biodiversity Areas"] / envperf_merged["Revenue"]
    )

    envperf_prev10 = envperf_merged

    #     mask8 = envperf_merged['Company'].isin(company_list)
    #     envperf_prev10 = envperf_merged[mask8]

    envperf_prev10["GHG1 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG1"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["GHG2 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG2"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["GHG3 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG3"].rank(pct=True)
    ).fillna(0)
    # envperf_prev10['Water Consumption Percentile Rank'] = (1-envperf_prev10['Normalized Water Consumption'].rank(pct=True)).fillna(0)
    envperf_prev10["Water Withdrawal Percentile Rank"] = (
        1 - envperf_prev10["Normalized Water Withdrawal"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["Biodiversity Areas Percentile Rank"] = (
        envperf_prev10["Normalized Biodiversity Areas"].rank(pct=True)
    ).fillna(0)

    # envperf_prev10['envperfscore'] = envperf_prev10[['GHG1 Percentile Rank','GHG2 Percentile Rank','GHG3 Percentile Rank','Water Consumption Percentile Rank','Water Withdrawal Percentile Rank','Biodiversity Areas Percentile Rank']].mean(axis=1)
    envperf_prev10["envperfscore"] = envperf_prev10[
        [
            "GHG1 Percentile Rank",
            "GHG2 Percentile Rank",
            "GHG3 Percentile Rank",
            "Water Withdrawal Percentile Rank",
            "Biodiversity Areas Percentile Rank",
        ]
    ].mean(axis=1)
    envperf_prev10 = envperf_prev10.sort_values(
        by="envperfscore", axis=0, ascending=False
    )
    perfscore = envperf_prev10[["Company", "envperfscore"]]

    single_perf_score = (
        envperf_prev10.loc[
            envperf_prev10["Company"] == new_firm_perf[0], "envperfscore"
        ]
        .values[0]
        .round(2)
    )

    # joining the two dataframes emg22 and egoal22 on the column 'Company'

    emg22 = emg22.rename(columns={"index": "Environmental Governance Index"})
    egoal22 = egoal22.rename(columns={"index": "Environmental Goals Index"})

    perfscore = perfscore.set_index("Company")
    emg22 = emg22.set_index("Company")
    egoal22 = egoal22.set_index("Company")
    emg22 = emg22.join(egoal22, on="Company")
    emg22 = emg22.join(perfscore, on="Company")

    emg22 = emg22.reset_index()

    # Assigning weights to the two indexes
    #     goals_weight = 0.4
    #     governance_weight = 0.6

    # Calculating the overall index using the weights
    weight_sum = governance_weight + goals_weight + performance_weight

    emg22["Overall index"] = (
        emg22["Environmental Governance Index"] * (governance_weight / weight_sum)
        + emg22["Environmental Goals Index"] * (goals_weight / weight_sum)
        + emg22["envperfscore"] * (performance_weight / weight_sum)
    )
    emg22 = emg22.sort_values(by="Overall index", ascending=True)

    #     print(emg22.loc[emg22['Company']==new_firm_gov[0],:])
    #     print(emg22.loc[emg22['Company']==new_firm_gov[0],'Overall index'].values[0])
    #     print(emg22)

    single_overall_score = (
        emg22.loc[emg22["Company"] == new_firm_gov[0], "Overall index"]
        .values[0]
        .round(2)
    )

    return single_gov_score, single_goal_score, single_perf_score, single_overall_score


def overallindex(
    sector,
    company_list,
    governance_weight,
    goals_weight,
    performance_weight,
    firm_ind,
    new_firm_perf,
    new_firm_gov,
    new_firm_goal,
):

    emg1 = df.loc[:, ["Company.Name", "Audited.Report", "TCFD New"]]
    emg1.rename(
        columns={
            "Company.Name": "Company",
            "Audited.Report": "GHG Assurance",
            "TCFD New": "TCFD Disclosure",
        },
        inplace=True,
    )

    mask = emg1["Company"].isin(company_list)
    emg1 = emg1[mask]

    categorical_mapping = {1.0: "Yes", 0.5: "Partial", 0.0: "No"}
    emg1["GHG Assurance"] = emg1["GHG Assurance"].map(categorical_mapping)
    emg1["TCFD Disclosure"] = emg1["TCFD Disclosure"].map(categorical_mapping)

    emg2 = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?",
            "Is Executive Compensation tied to any ESG milestones?",
        ],
    ]
    emg2.rename(
        columns={
            "Enter the full company name": "Company",
            "Does the company identify an environmental skill as a key board competency (i.e. included chart with all board members and their skills)?": "Environmental Skill as key board competency",
            "Is Executive Compensation tied to any ESG milestones?": "Executive Compensation tied to ESG milestones",
        },
        inplace=True,
    )

    mask = emg2["Company"].isin(company_list)
    emg2 = emg2[mask]

    emg = emg1.merge(emg2, on="Company")

    # emg = enviromentalgovernacemetrics(sector,company_list)[1]
    emg22 = emg.copy()

    # encoding all the categorical variables with the mapping 1.0: 'Yes', 0.5: 'Partial', 0.0: 'No'
    categorical_mapping = {"Yes": 1.0, "Partial": 0.5, "No": 0.0}
    emg22["GHG Assurance"] = emg["GHG Assurance"].map(categorical_mapping)
    emg22["TCFD Disclosure"] = emg["TCFD Disclosure"].map(categorical_mapping)
    emg22["Environmental Skill as key board competency"] = emg[
        "Environmental Skill as key board competency"
    ].map(categorical_mapping)
    emg22["Executive Compensation tied to ESG milestones"] = emg[
        "Executive Compensation tied to ESG milestones"
    ].map(categorical_mapping)

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        emg22.loc[len(emg22)] = new_firm_gov

    #################################

    # Creating a new column 'index' having the average of all the categorical variables
    emg22["index"] = emg22[
        [
            "GHG Assurance",
            "TCFD Disclosure",
            "Environmental Skill as key board competency",
            "Executive Compensation tied to ESG milestones",
        ]
    ].mean(axis=1)
    emg22 = emg22.sort_values(by="index", ascending=False)

    egoal = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "Does the company have a Net Zero/carbon neutrality goal?",
            "Does the Net Zero goal cover Scope 1 emissions?",
            "Does the Net Zero goal cover Scope 2 emissions?",
            "Does the Net Zero goal cover all of Scope 3 emissions?",
            "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?",
            "What is the status of the company's goal with the Science Based Target Institute?",
            "Does the company have an interim goal on the way to Net Zero?",
            'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?',
        ],
    ]
    egoal.rename(
        columns={
            "Enter the full company name": "Company",
            "Does the company have a Net Zero/carbon neutrality goal?": "Has a Net Zero Goal (NZG)",
            "Does the Net Zero goal cover Scope 1 emissions?": "NZG covers Scope 1 emissions",
            "Does the Net Zero goal cover Scope 2 emissions?": "NZG covers Scope 2 emissions",
            "Does the Net Zero goal cover all of Scope 3 emissions?": "NZG covers all of Scope 3 emissions",
            "Is the company on the Science Based Targets Institute as working with them to develop or track it's Net Zero Goal?": "Working with the SBTI ",
            "What is the status of the company's goal with the Science Based Target Institute?": "Status of the goal with SBTI",
            "Does the company have an interim goal on the way to Net Zero?": "Has an interim goal on the way to Net Zero",
            'Does the proxy statement mention "Net Zero" or "Carbon neutral" targets?': '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement',
        },
        inplace=True,
    )

    mask = egoal["Company"].isin(company_list)
    egoal = egoal[mask].fillna("Not Applicable")

    egoal.loc[222, '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = (
        "Not Applicable"
    )

    # egoal = environmentalgoals(sector,company_list)[1]
    egoal22 = egoal.copy()
    categorical_mapping2 = {
        "Yes": 1.0,
        "Committed": 1.0,
        "No": 0.0,
        "Not Applicable": 0.0,
        "Validated": 0.5,
    }
    egoal22["Has a Net Zero Goal (NZG)"] = egoal["Has a Net Zero Goal (NZG)"].map(
        categorical_mapping2
    )
    egoal22["NZG covers Scope 1 emissions"] = egoal["NZG covers Scope 1 emissions"].map(
        categorical_mapping2
    )
    egoal22["NZG covers Scope 2 emissions"] = egoal["NZG covers Scope 2 emissions"].map(
        categorical_mapping2
    )
    egoal22["NZG covers all of Scope 3 emissions"] = egoal[
        "NZG covers all of Scope 3 emissions"
    ].map(categorical_mapping2)
    egoal22["Working with the SBTI "] = egoal["Working with the SBTI "].map(
        categorical_mapping2
    )
    egoal22["Status of the goal with SBTI"] = egoal["Status of the goal with SBTI"].map(
        categorical_mapping2
    )
    egoal22["Has an interim goal on the way to Net Zero"] = egoal[
        "Has an interim goal on the way to Net Zero"
    ].map(categorical_mapping2)
    egoal22['"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'] = egoal[
        '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement'
    ].map(categorical_mapping2)

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        egoal22.loc[len(egoal22)] = new_firm_goal

    #################################

    egoal22["index"] = egoal22[
        [
            "Has a Net Zero Goal (NZG)",
            "NZG covers Scope 1 emissions",
            "NZG covers Scope 2 emissions",
            "NZG covers all of Scope 3 emissions",
            "Working with the SBTI ",
            "Status of the goal with SBTI",
            "Has an interim goal on the way to Net Zero",
            '"Net Zero" or "Carbon neutral" mentioned in Proxy Statement',
        ]
    ].mean(axis=1)
    egoal22 = egoal22.sort_values(by="index", ascending=False)

    envperf = dfnz2.loc[
        :,
        [
            "Enter the full company name",
            "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)",
            "Enter the company's Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)",
            "Enter the company's Scope 3 emissions in metric tons of CO2e.",
        ],
    ]
    envperf.rename(
        columns={
            "Enter the full company name": "Company",
            "What is the company's current Scope 1 emissions? Enter in metric tons of CO2e. (If not reported, enter NA.)": "Total GHG1",
            "Enter the company's Scope 2 market based emissions in metric tons CO2e. (Enter NA if the company does not report a market based figure.)": "Total market-based GHG2",
            "Enter the company's Scope 3 emissions in metric tons of CO2e.": "Total GHG3",
        },
        inplace=True,
    )

    # envperf2 = df.loc[:,['GICS.Sector','Company.Name','Revenue','CM10c.Response','CM10a.Response','CM9.Area.in.hectares']]
    # envperf2 = envperf2.rename(columns={"Company.Name":"Company","CM10c.Response":"Water Consumption","CM10a.Response":"Water Withdrawal","CM9.Area.in.hectares":"Biodiversity Areas"})

    envperf2 = df.loc[
        :,
        [
            "GICS.Sector",
            "Company.Name",
            "Revenue",
            "CM10a.Response",
            "CM9.Area.in.hectares",
        ],
    ]
    envperf2 = envperf2.rename(
        columns={
            "Company.Name": "Company",
            "CM10a.Response": "Water Withdrawal",
            "CM9.Area.in.hectares": "Biodiversity Areas",
        }
    )

    envperf_merged = envperf.merge(envperf2, on="Company", how="right")
    envperf_merged.loc[
        envperf_merged["Company"] == "Yum! Brands, Inc.", "Total GHG1"
    ] = 4291918

    mask8 = envperf_merged["Company"].isin(company_list)
    envperf_merged = envperf_merged[mask8]

    #########Additional company
    # firm_ind = 0
    if firm_ind == 1:
        envperf_merged.loc[len(envperf_merged)] = new_firm_perf

    #################################

    envperf_merged["Normalized GHG1"] = (
        pd.to_numeric(envperf_merged["Total GHG1"]) / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized GHG2"] = (
        envperf_merged["Total market-based GHG2"] / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized GHG3"] = (
        envperf_merged["Total GHG3"] / envperf_merged["Revenue"]
    )
    # envperf_merged['Normalized Water Consumption'] = envperf_merged['Water Consumption']/envperf_merged['Revenue']
    envperf_merged["Normalized Water Withdrawal"] = (
        envperf_merged["Water Withdrawal"] / envperf_merged["Revenue"]
    )
    envperf_merged["Normalized Biodiversity Areas"] = (
        envperf_merged["Biodiversity Areas"] / envperf_merged["Revenue"]
    )

    envperf_prev10 = envperf_merged

    #     mask8 = envperf_merged['Company'].isin(company_list)
    #     envperf_prev10 = envperf_merged[mask8]

    envperf_prev10["GHG1 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG1"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["GHG2 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG2"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["GHG3 Percentile Rank"] = (
        1 - envperf_prev10["Normalized GHG3"].rank(pct=True)
    ).fillna(0)
    # envperf_prev10['Water Consumption Percentile Rank'] = (1-envperf_prev10['Normalized Water Consumption'].rank(pct=True)).fillna(0)
    envperf_prev10["Water Withdrawal Percentile Rank"] = (
        1 - envperf_prev10["Normalized Water Withdrawal"].rank(pct=True)
    ).fillna(0)
    envperf_prev10["Biodiversity Areas Percentile Rank"] = (
        envperf_prev10["Normalized Biodiversity Areas"].rank(pct=True)
    ).fillna(0)

    # envperf_prev10['envperfscore'] = envperf_prev10[['GHG1 Percentile Rank','GHG2 Percentile Rank','GHG3 Percentile Rank','Water Consumption Percentile Rank','Water Withdrawal Percentile Rank','Biodiversity Areas Percentile Rank']].mean(axis=1)
    envperf_prev10["envperfscore"] = envperf_prev10[
        [
            "GHG1 Percentile Rank",
            "GHG2 Percentile Rank",
            "GHG3 Percentile Rank",
            "Water Withdrawal Percentile Rank",
            "Biodiversity Areas Percentile Rank",
        ]
    ].mean(axis=1)
    envperf_prev10 = envperf_prev10.sort_values(
        by="envperfscore", axis=0, ascending=False
    )
    perfscore = envperf_prev10[["Company", "envperfscore"]]

    # print(envperf_prev10.iloc[0,:])

    # joining the two dataframes emg22 and egoal22 on the column 'Company'

    emg22 = emg22.rename(columns={"index": "Environmental Governance Index"})
    egoal22 = egoal22.rename(columns={"index": "Environmental Goals Index"})

    perfscore = perfscore.set_index("Company")
    emg22 = emg22.set_index("Company")
    egoal22 = egoal22.set_index("Company")
    emg22 = emg22.join(egoal22, on="Company")
    emg22 = emg22.join(perfscore, on="Company")

    # Assigning weights to the two indexes
    #     goals_weight = 0.4
    #     governance_weight = 0.6

    # Calculating the overall index using the weights
    weight_sum = governance_weight + goals_weight + performance_weight

    emg22["Overall index"] = (
        emg22["Environmental Governance Index"] * (governance_weight / weight_sum)
        + emg22["Environmental Goals Index"] * (goals_weight / weight_sum)
        + emg22["envperfscore"] * (performance_weight / weight_sum)
    )
    emg22 = emg22.sort_values(by="Overall index", ascending=True)

    # #     fontsize = 550/emg22.shape[0]
    # #     if (550/emg22.shape[0] > 20):
    # #         fontsize = 20
    #     fontsize = 20

    fig3 = go.Figure(
        data=go.Heatmap(
            #                         z=[emg22['Overall index']],
            #                         x=emg22.index,
            #                         y=['Overall Index'],
            z=[[value] for value in emg22["Overall index"]],
            x=["Overall Index"],
            y=emg22.index,
            colorscale="rdylgn",
        )
    )
    fig3.update_layout(
        plot_bgcolor="white",
        font_family="Helvetica",
        title_font_family="Helvetica",
        xaxis_nticks=len(company_list),
    )
    fig3.update_layout(
        title=go.layout.Title(
            text=sector,
            # xref="paper",
            x=0.5,
        )
    )
    fig3.update_xaxes(title=None, showticklabels=False)
    fig3.update_yaxes(title=None)
    # fig3.update_zaxes(title=None)
    fig3.update_layout(
        height=30 * len(emg22),
        font=dict(size=20),
        font_family="Helvetica",
        title_font_family="Helvetica",
    )
    fig3.update_layout(
        margin=dict(
            l=200,  # left margin
            r=50,  # right margin
            t=50,  # top margin
            b=50,  # bottom margin to give more space to x-axis labels
        )
    )
    return fig3


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="/assets/UCLAAndersonSOM_Wht_PMScoated.png",
                                height="30px",
                            )
                        )
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://www.anderson.ucla.edu/",
                target="_blank",
                style={"textDecoration": "none"},
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Data Simulation", className="ms-2")),
                    dbc.Col(width=1),
                ],
                align="center",
                className="g-0",
            ),
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="/assets/2022IMPACT New Center Logo2.png",
                                height="40px",
                            )
                        )
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://www.anderson.ucla.edu/about/centers/impactanderson",
                target="_blank",
                style={"textDecoration": "none"},
            ),
        ],
        fluid=True,
    ),
    color="#313339",
    dark=True,
)

tab2card0 = dbc.Card(
    [
        dbc.CardHeader(
            "Climate Strategy Index",
            style={
                "background-color": "#C3D7EE",
                "text-align": "center",
                "font-weight": "bold",
                "font-style": "italic",
            },
            id="top2",
        ),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        html.B(
                            "Climate Strategy Index is a sector-wise scoring methodology constructed to rank firms based on their environmental performance, governace and goals and relative weights assigned to each of these categories."
                        ),
                        html.B(
                            "Better overall strategy is associated with a higher index."
                        ),
                    ],
                    style={"text-align": "center"},
                ),
                html.A(
                    dbc.Button(
                        "Scroll to top",
                        style={"background-color": "#313339", "color": "#FFFFFF"},
                    ),
                    href="#top2",
                    style={
                        "position": "fixed",
                        "bottom": "20px",
                        "right": "20px",
                        "z-index": "100",
                    },
                ),
                html.Br(),
                #             dbc.Row([
                #                 dbc.Col([],width=5),
                #                 dbc.Col([
                #                     dbc.Button(
                #                         "Download Logic Documentation",
                #                         #href="/assets/Index Calculation.pdf",
                #                         #download="Index Calculation.pdf",
                #                         outline=True,
                #                         style={"background-color": "#FDB71A"},
                #                         #html.Button("Download Image", id="btn_image"),
                #                         id="dnld_file"
                #                         #color="Light"
                #                         #size="sm",
                #                         #className="mx-auto"
                #                     ),
                #                     dcc.Download(id="download_file")
                #                 ],width=2),
                #                 dbc.Col([],width=5),
                #             ], className="d-flex justify-content-center"),
                #             dbc.Button(
                #                 "Download Logic Documentation",
                #                 href="/assets/Index Calculation.pdf",
                #                 download="Index Calculation.pdf",
                #                 #external_link=True,
                #                 style={"color":"C3D7EE","text-align":"center"},
                #             ),
                dbc.Row(
                    [
                        html.P(
                            "The Weights panel can be used to select the sector and appropriate weightage of each category"
                        ),
                        html.P(
                            "The Ranking panel provides the firm rankings for the selected sector based on the climate strategy index calculated as the weighted mean of environmental performance, governace and goal metrics of the respective firms"
                        ),
                        html.P(
                            "The Score Breakdown panel lists the features used to calculate each category's index based on an example firm. The example firm can also be added to the sector-level ranking list for comparison"
                        ),
                    ],
                    style={"text-align": "center"},
                ),
            ]
        ),
    ],
    className="m-1",
)

tab2card1 = dbc.Card(
    [
        dbc.CardHeader(
            "Weights",
            style={
                "background-color": "#C3D7EE",
                "text-align": "center",
                "font-weight": "bold",
                "font-style": "italic",
            },
        ),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "Select Sector ⇗",
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                    },
                                    id="ss12",
                                )
                            ],
                            width=12,
                        ),
                        dbc.Tooltip(
                            "Use the arrow to select your sector of interest or start typing to see matching options. Only one sector can be selected at a time.",
                            style={"textDecoration": "underline", "cursor": "pointer"},
                            target="ss12",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(set(df["GICS.Sector"].tolist()))
                                    if x is not None and not pd.isnull(x)
                                ],
                                value="Consumer Staples",
                                id="sector_select12",
                            ),
                            width=12,
                        )
                    ]
                ),
                html.Br(),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "Performance ⇗",
                                    style={"text-align": "center"},
                                    id="perf_tool",
                                ),
                                dbc.Tooltip(
                                    "Performance metrics focuses on quantified attributes like amount of GHG emitted, water consumed and land used near key biodiversity areas",
                                    style={
                                        "textDecoration": "underline",
                                        "cursor": "pointer",
                                    },
                                    target="perf_tool",
                                ),
                                dcc.Slider(
                                    min=0,
                                    max=100,
                                    step=10,
                                    value=40,
                                    id="performance_slider",
                                ),
                            ]
                        )
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "Governance ⇗",
                                    style={"text-align": "center"},
                                    id="gov_tool",
                                ),
                                dbc.Tooltip(
                                    "Governance metrics focuses on disclosure of administrative compliance like ESG incentives and competencies of board members, audit of reports and TCFD framework adherance of disclosures",
                                    style={
                                        "textDecoration": "underline",
                                        "cursor": "pointer",
                                    },
                                    target="gov_tool",
                                ),
                                dcc.Slider(
                                    min=0,
                                    max=100,
                                    step=10,
                                    value=30,
                                    id="governance_slider",
                                ),
                            ]
                        )
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "Goals ⇗",
                                    style={"text-align": "center"},
                                    id="goal_tool",
                                ),
                                dbc.Tooltip(
                                    "Goals metrics focuses on the state of Net Zero goals - if there is a complete or an interim one, the inclusions therein and status of working with SBTI",
                                    style={
                                        "textDecoration": "underline",
                                        "cursor": "pointer",
                                    },
                                    target="goal_tool",
                                ),
                                dcc.Slider(
                                    min=0, max=100, step=10, value=30, id="goal_slider"
                                ),
                            ]
                        )
                    ]
                ),
            ]
        ),
    ],
    className="m-1",
)

tab2card2 = dbc.Card(
    [
        dbc.CardHeader(
            "Ranking based on Climate Strategy Index",
            style={
                "background-color": "#C3D7EE",
                "text-align": "center",
                "font-weight": "bold",
                "font-style": "italic",
            },
        ),
        dbc.CardBody(
            [
                dbc.Row([dbc.Col(dcc.Graph(id="overall_index"))]),
                dbc.Row(
                    [
                        dbc.Checklist(
                            options=[
                                {
                                    "label": "Add additional firm to ranked list",
                                    "value": 0,
                                }
                            ],
                            id="newfirm_toggle",
                            switch=True,
                            # className="form-check-input"
                        )
                    ]
                ),
            ]
        ),
    ],
    className="m-1",
)

tab2card3 = dbc.Card(
    [
        dbc.CardHeader(
            "Score Breakdown",
            style={
                "background-color": "#C3D7EE",
                "text-align": "center",
                "font-weight": "bold",
                "font-style": "italic",
            },
        ),
        dbc.CardBody(
            [
                dbc.Form(
                    [
                        dbc.Row(
                            [
                                dbc.Label("For a firm", width="auto"),
                                dbc.Col(
                                    dbc.Input(
                                        type="text",
                                        placeholder="Enter firm name",
                                        value="ABC Foods Inc",
                                        id="firmname_input",
                                    ),
                                    className="me-3",
                                ),
                                dbc.Label("in", width="auto"),
                                dbc.Label(id="firmsector_input", width="auto"),
                                dbc.Label("sector having annual Revenue", width="auto"),
                                dbc.Col(
                                    dbc.InputGroup(
                                        [
                                            # dbc.InputGroupText("Annual revenue:"),
                                            dbc.InputGroupText("$"),
                                            dbc.Input(
                                                value=7986.252,
                                                type="number",
                                                id="firmrev_input",
                                            ),
                                            dbc.InputGroupText("M"),
                                        ],
                                        # className="mb-3",
                                    ),
                                    className="me-3",
                                ),
                                # dbc.Col(dbc.Button("Submit", color="primary"), width="auto"),
                            ],
                            className="g-2",
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H5(
                                            [
                                                "Environmental Performance Index is the average sector-based percentile ranking of the following Metrics normalized by revenue"
                                            ]
                                        )
                                    ],
                                    width=9,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "What is Percentile Ranking?",
                                            id="per_rank_exp",
                                            n_clicks=0,
                                            outline=True,
                                            color="secondary",
                                            className="me-1",
                                        )
                                    ],
                                    width=3,
                                ),
                                # html.H5([""]),
                                # html.Span("percentile ranking", id="percentile_tooltip"),
                                #                      dbc.Tooltip(
                                #                          "Percentile ranking indicates the relative position of a score within a distribution, showing the percentage of scores that fall below it.",
                                #                          style={"textDecoration": "underline", "cursor": "pointer"},
                                #                          target="percentile_tooltip",
                                #                      ),
                                #                     dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0),
                                dbc.Offcanvas(
                                    html.P(
                                        "Percentile ranking indicates the relative position of a score within a distribution, showing the percentage of scores that fall below it."
                                    ),
                                    id="per_rank_exp_off",
                                    title="Percentile Rank",
                                    is_open=False,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Scope 1 Emission",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        html.I(className="bi bi-info-circle-fill me-2"),
                                        dbc.Input(
                                            type="number",
                                            value=179.211,
                                            id="ghg1_input",
                                        ),
                                        dbc.InputGroupText("thousand metric tons"),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Scope 2 Emission (market-based)",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dbc.Input(
                                            type="number", value=68.639, id="ghg2_input"
                                        ),
                                        dbc.InputGroupText("thousand metric tons"),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Scope 3 Emission",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dbc.Input(
                                            type="number",
                                            value=5941.676,
                                            id="ghg3_input",
                                        ),
                                        dbc.InputGroupText("thousand metric tons"),
                                    ],
                                    className="me-3",
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                #                         dbc.Col([
                                #                             dbc.Label("Water consumption", width="auto",style={'font-style': 'italic'}),
                                #                             dbc.Input(type="number", value=872.90, id="wc_input"),
                                #                             dbc.InputGroupText("mega litres")],
                                #                             className="me-3",
                                #                         ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Water withdrawal",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dbc.Input(
                                            type="number", value=5416.50, id="ww_input"
                                        ),
                                        dbc.InputGroupText("mega litres"),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Biodiversity ⇗",
                                            width="auto",
                                            id="biod_tooltip",
                                            style={"font-style": "italic"},
                                        ),
                                        dbc.Tooltip(
                                            "Biodiversity indicates the total area of sites owned, leased, or managed in or adjacent to protected areas or key biodiversity areas ",
                                            style={
                                                "textDecoration": "underline",
                                                "cursor": "pointer",
                                            },
                                            target="biod_tooltip",
                                        ),
                                        dbc.Input(
                                            type="number", value=119537, id="biod_input"
                                        ),
                                        dbc.InputGroupText("hectares"),
                                    ],
                                    className="me-3",
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Performance Index based on above values and in comparison to firms listed alongside:",
                                    width="auto",
                                ),
                                dbc.Label(
                                    id="perf_index_disp",
                                    width="auto",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Br(),
                        dbc.Row(
                            [
                                html.H5(
                                    "Environmental Governace Index is the encoded average of the following Metrics"
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "GHG Assurance",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "Partial", "value": 0.5},
                                            ],
                                            value=0,
                                            id="ghga_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "TCFD Disclosure",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "Partial", "value": 0.5},
                                            ],
                                            value=0.5,
                                            id="tcfd_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Environmental skill as a key board competency",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "Partial", "value": 0.5},
                                            ],
                                            value=1,
                                            id="envskill_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Executive compensation tied to ESG milestone",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "Partial", "value": 0.5},
                                            ],
                                            value=1,
                                            id="envcomp_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                            ],
                            # style={'background-color': 'aquamarine'}
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Encoding: Yes=1 ; Partial=0.5 ; No=0", width="auto"
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Governace Index based on above values:",
                                    width="auto",
                                ),
                                dbc.Label(
                                    id="gov_index_disp",
                                    width="auto",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        ),
                        html.Br(),
                        html.Br(),
                        dbc.Row(
                            [
                                html.H5(
                                    "Environmental Goals Index is the encoded average of the following Metrics"
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Has a Net Zero Goal",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                            ],
                                            value=0,
                                            id="nzg_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Net Zero goal covers scope 1 emissions",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="nzs1_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Net Zero goal covers scope 2 emissions",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="nzs2_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Net Zero goal covers all of scope 3 emissions",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="nzs3_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Has an interim Goal on the way to Net Zero",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="ntig_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Working with SBTI",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="sbti_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Status of goal with SBTI",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Comitted", "value": 1},
                                                {"label": "Validated", "value": 0.5},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="sbti_stat_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "'Net Zero'/'Carbon neutral' mentioned in Proxy Statement",
                                            width="auto",
                                            style={"font-style": "italic"},
                                        ),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Yes", "value": 1},
                                                {"label": "No", "value": 0},
                                                {"label": "NA", "value": 0},
                                            ],
                                            value=0,
                                            id="ntcnps_input",
                                        ),
                                    ],
                                    className="me-3",
                                ),
                            ],
                            className="g-2",
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Encoding: Yes=1 ; Committed=1 ; Validated=0.5 ; No=0 ; NA=0 ",
                                    width="auto",
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Goals Index based on above values:", width="auto"
                                ),
                                dbc.Label(
                                    id="goal_index_disp",
                                    width="auto",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Label(
                                    "Climate Strategy Index is the weighted average of the above 3 indices:",
                                    width="auto",
                                ),
                                dbc.Label(
                                    id="overall_index_disp",
                                    width="auto",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ],
    className="m-1",
)


tab2card4 = [
    dbc.Button(
        "For more information regarding index calculation, click here",
        outline=True,
        style={"background-color": "#FDB71A", "color": "#000000"},
        id="dnld_file",
    ),
    dcc.Download(id="download_file"),
]

tab2 = html.Div(
    [
        dbc.Row([tab2card0], className="m-1"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(tab2card1, className="m-1"),
                        dbc.Row(tab2card3, className="m-1"),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Row(tab2card2, className="m-1"),
                        dbc.Row(tab2card4, className="m-1"),
                    ],
                    width=6,
                ),
            ]
        ),
        # dbc.Row([dbc.Col([tab2card2],width=12)],className="mb-4 ml-3"),
        # dbc.Row([dbc.Col([tab2card3],width=6)],className="mb-4 ml-3")
    ]
)

layout = html.Div([dbc.Row([dbc.Col(navbar)], className="mb-4"), tab2])


def register_tab1_callbacks(app):
    @app.callback(
        [Output("overall_index", "figure"), Output("firmsector_input", "children")],
        [
            Input("sector_select12", "value"),
            Input("governance_slider", "value"),
            Input("goal_slider", "value"),
            Input("performance_slider", "value"),
            Input("newfirm_toggle", "value"),
        ],
        [
            State("firmname_input", "value"),
            State("firmrev_input", "value"),
            State("ghg1_input", "value"),
            State("ghg2_input", "value"),
            State("ghg3_input", "value"),
            # State('wc_input', 'value'),
            State("ww_input", "value"),
            State("biod_input", "value"),
            State("ghga_input", "value"),
            State("tcfd_input", "value"),
            State("envskill_input", "value"),
            State("envcomp_input", "value"),
            State("nzg_input", "value"),
            State("nzs1_input", "value"),
            State("nzs2_input", "value"),
            State("nzs3_input", "value"),
            State("ntig_input", "value"),
            State("sbti_input", "value"),
            State("sbti_stat_input", "value"),
            State("ntcnps_input", "value"),
        ],
    )
    def update_overallindex(
        sector,
        governance_weight,
        goals_weight,
        performance_weight,
        toggle,
        name,
        rev,
        ghg1,
        ghg2,
        ghg3,
        ww,
        biod,
        ghga,
        tcfd,
        envskill,
        envcomp,
        nzg,
        nzs1,
        nzs2,
        nzs3,
        ntig,
        sbti,
        sbti_stat,
        ntcnps,
    ):
        companies = company_list_from_sector(sector)
        name_bold = "<b>" + name + "</b>"
        if toggle:
            firm_ind = 1
        else:
            firm_ind = 0
        new_firm_perf = [
            name_bold,
            ghg1 * 1000,
            ghg2 * 1000,
            ghg3 * 1000,
            sector,
            rev,
            ww,
            biod,
        ]
        new_firm_gov = [name_bold, ghga, tcfd, envskill, envcomp]
        new_firm_goal = [
            name_bold,
            nzg,
            nzs1,
            nzs2,
            nzs3,
            ntig,
            sbti,
            sbti_stat,
            ntcnps,
        ]

        figindex = overallindex(
            sector,
            companies,
            governance_weight,
            goals_weight,
            performance_weight,
            firm_ind,
            new_firm_perf,
            new_firm_gov,
            new_firm_goal,
        )
        return figindex, sector

    @app.callback(
        [
            Output("gov_index_disp", "children"),
            Output("goal_index_disp", "children"),
            Output("perf_index_disp", "children"),
            Output("overall_index_disp", "children"),
        ],
        [
            Input("sector_select12", "value"),
            Input("governance_slider", "value"),
            Input("goal_slider", "value"),
            Input("performance_slider", "value"),
            Input("firmname_input", "value"),
            Input("firmrev_input", "value"),
            Input("ghg1_input", "value"),
            Input("ghg2_input", "value"),
            Input("ghg3_input", "value"),
            # Input('wc_input', 'value'),
            Input("ww_input", "value"),
            Input("biod_input", "value"),
            Input("ghga_input", "value"),
            Input("tcfd_input", "value"),
            Input("envskill_input", "value"),
            Input("envcomp_input", "value"),
            Input("nzg_input", "value"),
            Input("nzs1_input", "value"),
            Input("nzs2_input", "value"),
            Input("nzs3_input", "value"),
            Input("ntig_input", "value"),
            Input("sbti_input", "value"),
            Input("sbti_stat_input", "value"),
            Input("ntcnps_input", "value"),
        ],
    )
    def update_indexplaceholders(
        sector,
        governance_weight,
        goals_weight,
        performance_weight,
        name,
        rev,
        ghg1,
        ghg2,
        ghg3,
        ww,
        biod,
        ghga,
        tcfd,
        envskill,
        envcomp,
        nzg,
        nzs1,
        nzs2,
        nzs3,
        ntig,
        sbti,
        sbti_stat,
        ntcnps,
    ):
        companies = company_list_from_sector(sector)
        name_bold = "<b>" + name + "</b>"
        #     if toggle:
        #         firm_ind = 1
        #     else:
        #         firm_ind = 0
        new_firm_perf = [
            name_bold,
            ghg1 * 1000,
            ghg2 * 1000,
            ghg3 * 1000,
            sector,
            rev,
            ww,
            biod,
        ]
        new_firm_gov = [name_bold, ghga, tcfd, envskill, envcomp]
        new_firm_goal = [
            name_bold,
            nzg,
            nzs1,
            nzs2,
            nzs3,
            ntig,
            sbti,
            sbti_stat,
            ntcnps,
        ]

        gov, goal, perf, overall = index_calculator(
            sector,
            companies,
            governance_weight,
            goals_weight,
            performance_weight,
            1,
            new_firm_perf,
            new_firm_gov,
            new_firm_goal,
        )

        return gov, goal, perf, overall

    ##File download
    @app.callback(
        Output("download_file", "data"),
        Input("dnld_file", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_func(n_clicks):
        PATH = pathlib.Path(__file__).parent
        FILE_PATH = PATH.parent.joinpath("assets").resolve()
        return dcc.send_file(FILE_PATH.joinpath("Index Calculation.pdf"))

    ##off canvas
    @app.callback(
        Output("per_rank_exp_off", "is_open"),
        Input("per_rank_exp", "n_clicks"),
        [State("per_rank_exp_off", "is_open")],
    )
    def toggle_offcanvas(n1, is_open):
        if n1:
            return not is_open
        return is_open
