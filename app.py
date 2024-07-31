#%%
import plotly.graph_objs as go

import streamlit as st
from dbharbor.bigquery import SQL
import numpy as np
import dgsheet
from streamlit_authentication.google_oauth import authenticate
import os
import pathlib
from dotenv import load_dotenv
load_dotenv()

# Access the environment variables
sql_file_dir_path = f"{pathlib.Path(__file__).resolve().parents[0]}/Queries/"


def box_text(my_string, font_size=24):
  st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: {font_size}px;'>{my_string}</div>", unsafe_allow_html=True)



@st.cache_data(ttl=60 * 60 * 12) # seconds
def get_data(query_file_name):
    con = SQL(  credentials_filepath = os.getenv('BIGQUERY_CRED'))
    with open(f"{sql_file_dir_path}{query_file_name}.sql") as sql_file:
        sql = sql_file.read()
        df = con.read(sql)


    return df



def display_subscription_info(subscriptions, subscription_trials_df, total, is_trial, section_title):
    # Display the section title
    cols = st.columns(total)
    with cols[0]:
        st.markdown(f"<div style='text-align: left; white-space: nowrap; font-weight: bold; font-size: 36px;'>{section_title}</div>", unsafe_allow_html=True)

    # Recreate columns for displaying subscription data
    cols = st.columns(total)
    for i in range(total):
        sub = subscriptions[i]
        
        if i < total - 1:
            subscription_trials_df_temp = subscription_trials_df[
                (subscription_trials_df['product_eom'] == sub) & 
                (subscription_trials_df['is_trial'] == is_trial)
            ]
            units = subscription_trials_df_temp['units'].iat[0] if not subscription_trials_df_temp.empty else 0
        else:
            subscription_trials_df_temp = subscription_trials_df[subscription_trials_df['is_trial'] == is_trial]
            units = subscription_trials_df_temp['units'].sum()
        
        with cols[i]:
            box_text(sub)
            box_text("{:,}".format(units))


def get_data_gsheets():

    url = 'https://docs.google.com/spreadsheets/d/1LzYYliKurBl9TZsA436z-NTKPV3bOEEA_DaA13ctcfQ/edit?gid=83865450#gid=83865450'
    filepath_cred = os.getenv('BIGQUERY_CRED')

    df = dgsheet.read_gsheet(url, filepath_cred=filepath_cred, skiprows=11, usecols="A:F", nrows=7)

    def data_clean(x):
        if x == '' or x == None:
            x = np.nan
        else:
            x = x.replace('%', '')
            x = float(x) / 100
        return x
    for col in df.columns:
        if col != 'Invoice Number':
            df[col] = df[col].map(data_clean)


    return df


def plot_line_charts(data, x_axis, y_axis, measure_axis, secondary_y_axis=None, secondary_y_label=None):
    """
    Plots line charts with optional secondary y-axis using Plotly.
    
    Args:
    - data (DataFrame): Data for plotting.
    - x_axis (str): Column name for x-axis.
    - y_axis (str): Column name for primary y-axis.
    - measure_axis (list of str): List of column names for primary y-axis data series.
    - secondary_y_axis (str, optional): Column name for secondary y-axis data series.
    - secondary_y_label (str, optional): Label for the secondary y-axis.
    """
    
    # Create the figure
    fig = go.Figure()

    # Plot primary y-axis data series
    for measure in measure_axis:
        dash='dot' if '6 pay' in measure.lower() else 'solid'
        fig.add_trace(go.Scatter(
            x=data[x_axis], 
            y=data[measure], 
            mode='lines', 
            name=measure,
            yaxis='y1',
            line=dict(dash=dash, shape='spline', width=2)

        ))


    titlefont = {'size': 18, 'color': 'black', 'family': 'Arial Black, sans-serif'}
    tickfont = {'size': 12, 'color': 'black', 'family': 'Arial Ash, sans-serif'}
    tickangle = 90 if x_axis == 'Month' else 0
    title_standoff = 45
    tickformat='.0%' if x_axis == 'Invoice Number' else None

    # Update layout for primary y-axis
    fig.update_layout(
        xaxis=dict(title=x_axis, tickangle=tickangle, titlefont=titlefont, tickfont =tickfont,title_standoff=title_standoff),
        yaxis=dict(title=y_axis, titlefont=titlefont, tickfont =tickfont, title_standoff=title_standoff,tickformat = tickformat)
    )





    if secondary_y_axis:
        colors = ['green', 'orange', 'purple']  # Add more colors if needed
        for i, measure in enumerate(secondary_y_axis):
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=data[x_axis], 
                y=data[measure], 
                mode='lines', 
                name=measure,
                yaxis='y2',
                line=dict(color=color, dash='dot')
            ))

        # Update layout for secondary y-axis
        fig.update_layout(
            yaxis2=dict(
                title=secondary_y_label,
                overlaying='y',
                side='right',
                tickfont=dict(color='green'),
                titlefont=dict(color='green'),
                range=[0, 1] 
            )
        )
    

        # Update layout for legend position
    fig.update_layout(
        legend=dict(
            x=0.5,  # X position of the legend (0 is left, 1 is right)
            y=1.1,  # Y position of the legend (0 is bottom, 1 is top)
            xanchor='center',  # Anchor the legend at the center of the x position
            yanchor='top',  # Anchor the legend at the top of the y position
            orientation='h'  # Horizontal orientation
        )
    )
    # Display the plot in Streamlit
    st.plotly_chart(fig)



if 'page_set' not in st.session_state:
    st.set_page_config(layout="wide")
    st.session_state['page_set'] = True


st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)


@authenticate
def main():

    # logo_url = "https://path_to_your_logo/logo.png"
    # st.image(logo_url, width=100)d

    st.title('Mastermind Portfolio')
    st.markdown('<br><br>', unsafe_allow_html=True)

    subscription_trials_df = get_data('current_subscription_n_trials')

    
    subscriptions = ['47 membership', '423 membership', '97 membership', '997 membership', 'Total']
    total = len(subscriptions)


    #%%

    cols = st.columns(total)


    display_subscription_info(subscriptions, subscription_trials_df, total, is_trial=0, section_title="Active Subscribers")

    st.markdown('<br><br>', unsafe_allow_html=True)

    # Display Trial subscriptions
    display_subscription_info(subscriptions, subscription_trials_df, total, is_trial=1, section_title="Trial")

    st.markdown('<br><br>', unsafe_allow_html=True)

    display_subscription_info(subscriptions, subscription_trials_df, total, is_trial=2, section_title="Total")


    #%%

    st.markdown('<br><br>', unsafe_allow_html=True)

    st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'> </div>", unsafe_allow_html=True)
 
    # subscription_trials_table_df = get_data('current_subscription_n_trials_table')
    # subscription_trials_table_df.rename(columns={'product_eom': ''}, inplace=True)
    # subscription_trials_table_df.set_index('', inplace=True)
    # st.dataframe(subscription_trials_table_df, use_container_width=True)


    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'>Monthly Active Subscriptions </div>", unsafe_allow_html=True)


    mas_linechart_df = get_data('monthly_active_subscription')

# Plot with only primary y-axis
    plot_line_charts(
        data=mas_linechart_df,
        x_axis='Month',
        y_axis='Count',
        measure_axis=["47 membership", "423 membership", "997 membership", "97 membership"]
    )


    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'>MBA Metrics</div>", unsafe_allow_html=True)


    mba_linechart_df = get_data('mba')

    # Plot with both primary and secondary y-axes
    plot_line_charts(
        data=mba_linechart_df,
        x_axis='Month',
        y_axis='Count',
        measure_axis=["Sales", "Cancels", "Total Active"],
        secondary_y_axis=['pif_sales_ratio',"Drop Rate"],
        secondary_y_label='Ratio (Dotted Lines)'
    )



    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'>Payment Plan Performance </div>", unsafe_allow_html=True)

    payment_plan = get_data_gsheets()

    # Plot with both primary and secondary y-axes
    plot_line_charts(
        data=payment_plan,
        x_axis='Invoice Number',
        y_axis='Percentage',
        measure_axis=["Project Next 3 Pay", "Project Next 6 Pay", "Launchpad 3 Pay", "Launchpad 6 Pay", "MBS 3 Pay"]
    )







if __name__ == '__main__':
    main()







