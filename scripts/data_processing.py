import os
import pandas as pd
import plotly.graph_objs as go


def return_figures():
    """
    Retrieve data and generate figures for web page
    :return:
    """

    # Declare directory
    directory = "./data"

    # Retrieve names dataframe
    names = retrieve_names(directory)

    # Declare features list
    figures = []

    # Add charts
    figures.append(generate_time_series(names, "M", 5))
    figures.append(generate_time_series(names, "F", 5))
    figures.append(generate_streaks_plot(names))

    return figures


def generate_streaks_plot(dataframe):
    """
    Calculate streaks at rank 1 and generate bar plot
    :param dataframe:
    :return:
    """

    # Calculate streaks for each gender
    males = get_streaks(dataframe, "M")
    females = get_streaks(dataframe, "F")

    # Combine dataframes
    streaks = pd.concat([males, females])

    # Add color by gender
    streaks["color"] = streaks["gender"].apply(lambda x: "#347DC1" if x == "M" else "#E6A6C7")

    # Sort by count
    streaks.sort_values(by='count', inplace=True)

    # Generate graph
    graph = list()
    graph.append(
        go.Bar(
            y=streaks.index.tolist(),
            x=streaks["count"].tolist(),
            marker={
                "color": streaks["color"].tolist(),
                "line": {
                    "color": streaks["color"].tolist(),
                    "width": 1.5
                }
            },
            orientation="h",
            opacity=0.7
        )
    )

    layout = {
        "title": "Longest Top Rank Streaks",
        "xaxis": {
            "title": "Years",
            "autotick": True
        },
        "yaxis": {
            "title": "Name"
        },
        "autosize": False,
        "width": 350,
        "height": 900,
    }

    return {"data": graph, "layout": layout}


def generate_time_series(dataframe, gender, n):
    """
    Generate time series of top 5 baby names by gender
    :param dataframe:
    :param gender:
    :param n:
    :return:
    """

    # Isolate to gender and sort by year/count
    df = dataframe[dataframe["gender"] == gender]

    # Group by yearly count
    top_n = get_yearly_top_n(df, n)

    # Isolate unique names
    name_list = top_n["name"].unique().tolist()

    # Generate graph points by name
    graph = list()
    for name in name_list:
        x_val = top_n[top_n["name"] == name]["year"].tolist()
        y_val = top_n[top_n["name"] == name]["rank"].tolist()

        graph.append(
            go.Scatter(
                x=x_val,
                y=y_val,
                mode='lines',
                name=name
            )
        )

    # Generate layout
    gender_string = "Males" if gender == "M" else "Females"

    layout = {
        "title": f"Yearly Top {n} Names for {gender_string}",
        "xaxis": {
            "title": "Year",
            "autotick": True
        },
        "yaxis": {
            "title": "Rank"
        }
    }

    return {"data": graph, "layout": layout}


def get_streaks(dataframe, gender):
    """
    Generate a dataframe of longest streaks at rank 1 for a gender
    :param dataframe:
    :param gender:
    :return:
    """

    # Isolate to gender
    df = dataframe[dataframe["gender"] == gender]

    # Get top 1 entries
    top = get_yearly_top_n(df, 1)

    # Calculate streaks
    streaks = calculate_streaks(top)

    # Add gender column
    streaks["gender"] = gender

    return streaks


def calculate_streaks(dataframe):
    """
    Calculate streaks at rank 1 for a dataframe
    :param dataframe:
    :return:
    """

    # Isolate unique names
    name_list = dataframe["name"].unique().tolist()

    # Initiate empty dictionary
    longest_streaks = {}

    # Iterate over name list
    for name in name_list:

        streaks = []
        year = 0
        current_streak = 0

        # Find streaks by year
        for i, v in dataframe[dataframe["name"] == name].iterrows():
            if int(v["year"]) == year + 1:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

            year = int(v["year"])

        streaks.append(current_streak)

        longest_streaks[name] = max(streaks)

    return pd.DataFrame.from_dict(longest_streaks, orient='index', columns=['count'])


def get_yearly_top_n(dataframe, n):
    """
    Get top n records for each year within a dataframe
    :param dataframe:a
    :param n:
    :return:
    """
    # Sort by count
    dataframe = dataframe.sort_values(by=["year", "count"], ascending=[True, False])

    # Get top n by year
    top_n = dataframe.groupby('year').head(n)

    # Add rank column
    top_n["rank"] = top_n.groupby('year')["count"].rank("dense", ascending=False).astype(int)

    return top_n


def retrieve_names(directory):
    """
    Retrieve list of all files in the directory and combine their contents into a
    single dataframe.
    :param directory:
    :return:
    """

    # Retrieve list of files
    files = os.listdir(directory)

    # Remove invalid files
    files = [f for f in files if f.endswith(".txt")]

    # Create list of data frames from files
    years = []

    for file in files:

        # Create dataframe
        df = pd.read_csv(
            "./data/" + file, header=None, names=["name", "gender", "count"]
        )

        # Add year column
        df["year"] = file[3:7]

        # Append to years
        years.append(df)

    # Return concatenated dataframe
    return pd.concat(years)
