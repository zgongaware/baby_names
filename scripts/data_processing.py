import os
import pandas as pd
import plotly.graph_objs as go


def return_figures():

    # Declare directory
    directory = "./data"

    # Retrieve names dataframe
    names = retrieve_names(directory)

    # Declare features list
    figures = []

    # Add charts
    figures.append(generate_time_series(names, "M", 5))
    figures.append(generate_time_series(names, "F", 5))

    return figures


def generate_time_series(dataframe, gender, n):

    # Isolate to gender and sort by year/count
    df = dataframe[dataframe["gender"] == gender]

    # Group by yearly count
    top_n = get_yearly_top_n(df, n)

    # Isolate unique names
    name_list = top_n["name"].unique().tolist()

    # Generate graph points by name
    graph = []
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


def get_yearly_top_n(dataframe, n):
    """
    Get top n records for each year within a dataframe
    :param dataframe:
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
