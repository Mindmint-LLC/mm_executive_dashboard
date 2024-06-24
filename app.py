import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
# from streamlit_authentication.google_oauth import authenticate
from streamlit_autorefresh import st_autorefresh


# @authenticate
def main():
    st_autorefresh(interval=3610 * 1000, key="fizzbuzzcounter")
    # Authenticate with Google Cloud
    client = bigquery.Client.from_service_account_json(os.getenv('BIGQUERY_CRED'))

    # Query your BigQuery view
    query = """
    SELECT *
    FROM `bbg-platform.challenges.ghc_trial_conversions_vw`
    """

    @st.cache_data(ttl=3600)  # Cache the data for 1 hour (3600 seconds)
    def load_data():
        df = client.query(query).to_dataframe()
        df['due_date'] = pd.to_datetime(df['due_date'])  # Convert 'due_date' to datetime
        return df

    # Load the data
    df = load_data()

    # Filter data for the date range 6/20/24 to 7/15/24 and aggregate units by due_date
    start_date = pd.to_datetime('2024-06-20')
    end_date = pd.to_datetime('2024-07-15')
    filtered_df = df[(df['due_date'] >= start_date) & (df['due_date'] <= end_date)]

    # Convert 'due_date' to just date
    filtered_df['due_date'] = filtered_df['due_date'].dt.date

    # Create a bar chart using Plotly
    # st.subheader('Total Trials Due')
    # fig = px.bar(aggregated_data, x='due_date', y='units', labels={'due_date': 'Date', 'units': 'Total Units'}, title='Total Trials Due')
    # st.plotly_chart(fig, use_container_width=True)

    # Calculate the required metrics
    total_active = df['units'].sum()
    total_paid = df[df['invoice_status'] == 'paid']['units'].sum()
    total_unpaid = df[df['invoice_status'] == 'unpaid']['units'].sum()
    total_failed_first = df['failed_first_attempt'].sum()
    total_recovered = df['failed_recovered'].sum()

    # Calculate additional metrics
    total_cancelled = df[df['invoice_status'] == 'cancelled']['units'].sum()
    cancelled_percentage = (total_cancelled / total_active) * 100 if total_active > 0 else 0
    refund_total = df[df['invoice_status'] == 'refund']['units'].sum()
    upgrade_total = df[df['invoice_status'] == 'upgrade']['units'].sum()  
    paid_upgrade_percentage = (total_paid + upgrade_total) / total_active * 100 if total_active > 0 else 0
    refund_percentage = (refund_total / total_active) * 100 if total_active > 0 else 0
    failed_first_percentage = (total_failed_first / total_active) * 100 if total_active > 0 else 0
    recovered_percentage = (total_recovered / total_failed_first) * 100 if total_failed_first > 0 else 0

    # Create Streamlit dashboard
    st.title('Subscription Dashboard')

    # Display metrics in specified rows
    st.subheader('Overview Metrics')

    # Define function to create a row with specified columns and spacing
    def create_metric_row(metrics):
        cols = st.columns([1, 0.1, 1, 0.1, 1, 0.1, 1, 0.1, 1])
        for i, (label, value) in enumerate(metrics):
            cols[i * 2].metric(label, value)

    # Create rows with metrics and adjusted spacing for left alignment
    create_metric_row([("Total", f"{total_active:,}"), ("Cancelled", f"{total_cancelled:,}"), ("Cancelled %", f"{cancelled_percentage:.1f}%")])
    create_metric_row([("Unpaid", f"{total_unpaid:,}"), ("Paid", f"{total_paid:,}"), ("Refund", f"{refund_total:,}"), ("Upgrade", f"{upgrade_total:,}")])
    create_metric_row([("Paid/Upgrade %", f"{paid_upgrade_percentage:.1f}%"), ("Refund %", f"{refund_percentage:.1f}%")])
    create_metric_row([("Failed First Attempt", f"{total_failed_first:,}"), ("Failed First %", f"{failed_first_percentage:.1f}%"), ("Recovered", f"{total_recovered:,}"), ("Recovered %", f"{recovered_percentage:.1f}%")])

    # Aggregate units by due_date
    aggregated_data = filtered_df.groupby('due_date').agg({'units': 'sum'}).reset_index()

    # Display the aggregated data for inspection
    st.subheader('Filtered and Aggregated Data')
    st.dataframe(aggregated_data)


main()