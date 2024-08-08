import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('startup_cleaned.csv')

# Convert the 'date' column to datetime format and extract month and year
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# Set up the Streamlit page configuration
st.set_page_config(layout='wide', page_title="Startup Analysis")


def load_overall_analysis():
    """Function to perform and display overall analysis of startup data."""
    st.title("Overall Analysis")

    # Calculate total investment, maximum funding, average funding, and number of funded startups
    total = round(df['amount'].sum())
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    num_startup = df['startup'].nunique()

    # Display the calculated metrics in a 4-column layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total Investment', f'{total} cr')
    with col2:
        st.metric('Maximum Funding', f'{max_funding} cr')
    with col3:
        st.metric('Average Funding', f'{round(avg_funding)} cr')
    with col4:
        st.metric('Funded Startups', num_startup)

    # Display a Month-on-Month (MOM) analysis graph
    st.header('Month-on-Month (MOM) Analysis')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])

    # Group data by year and month, either summing or counting the 'amount' column
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    # Create an x-axis combining month and year for plotting
    temp_df['x-axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)

    # Plot the MOM analysis graph
    fig3, ax3 = plt.subplots()
    ax3.plot(temp_df['x-axis'], temp_df['amount'])
    st.pyplot(fig3)


def load_investor_details(investor):
    """Function to load and display investment details for a specific investor."""
    st.title(investor)

    # Display the most recent five investments by the investor
    last5_df = df[df['investors'].str.contains(investor, na=False)].head()[
        ['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader("Most Recent Investments")
    if not last5_df.empty:
        st.dataframe(last5_df)
    else:
        st.write("No recent investments found.")

    col1, col2 = st.columns(2)

    # Display the biggest investments made by the investor
    with col1:
        big_series = df[df['investors'].str.contains(investor, na=False)].groupby('startup')[
            'amount'].sum().sort_values(ascending=False).head()
        st.subheader("Biggest Investments")
        if not big_series.empty:
            fig, ax = plt.subplots()
            ax.bar(big_series.index, big_series.values)
            st.pyplot(fig)
        else:
            st.write("No investment data available.")

    # Display the sectors the investor has invested in
    with col2:
        vertical_series = df[df['investors'].str.contains(investor, na=False)].groupby('vertical')['amount'].sum()
        st.subheader("Sectors Invested In")
        if not vertical_series.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(vertical_series, labels=vertical_series.index, autopct='%0.01f%%')
            st.pyplot(fig1)
        else:
            st.write("No sector data available.")

    # Display year-on-year investment trend for the investor
    year_series = df[df['investors'].str.contains(investor, na=False)].groupby('year')['amount'].sum()
    st.subheader("Year-on-Year Investment")
    if not year_series.empty:
        fig2, ax2 = plt.subplots()
        ax2.plot(year_series.index, year_series.values)
        st.pyplot(fig2)
    else:
        st.write("No year-on-year investment data available.")


# Sidebar configuration for navigation
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'Startup', 'Investor'])

# Load content based on sidebar selection
if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'Startup':
    selected_startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find Startup Details')
    st.title('Startup Analysis')
    # Placeholder: Add logic to show startup details when btn1 is clicked

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
