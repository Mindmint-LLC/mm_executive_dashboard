#%%

import streamlit as st
from dbharbor.bigquery import SQL
from streamlit_authentication.google_oauth import authenticate


#%%

def box_text(my_string, font_size=24):
  st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: {font_size}px;'>{my_string}</div>", unsafe_allow_html=True)


@st.cache_data(ttl=60 * 60 * 12) # seconds
def get_data():
    con = SQL()

    sql = """
    with max_eom as (
    select max(eom) as eom
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly`
    )

    select m.product_eom
    , m.is_trial
    , count(*) as units
    from `bbg-platform.analytics.fct_mastermind__subscriptions_monthly` m
    join max_eom me
        on m.eom = me.eom
    where m.is_cancelled = 0
    group by all
    """
    df = con.read(sql)

    return df


#%%

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

    df = get_data()
    subscriptions = ['47 membership', '423 membership', '97 membership', '997 membership', 'Total']
    total = len(subscriptions)


    #%%

    cols = st.columns(total)
    with cols[0]:
        st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'>Active</div>", unsafe_allow_html=True)

    cols = st.columns(total)
    for i in range(total):
        sub = subscriptions[i]

        if i < total - 1:
            df_temp = df[(df['product_eom'] == sub) & (df['is_trial'] == 0)]
            units = df_temp['units'].iat[0]
            with cols[i]:
                box_text(sub)
                box_text("{:,}".format(units))

        if i == total - 1:
            df_temp = df[df['is_trial'] == 0]
            units = df_temp['units'].sum()
            with cols[i]:
                box_text(sub)
                box_text("{:,}".format(units))
            

    #%%

    st.markdown('<br><br>', unsafe_allow_html=True)

    cols = st.columns(total)
    with cols[0]:
        st.markdown(f"<div style='text-align: left; font-weight: bold; font-size: 36px;'>Trial</div>", unsafe_allow_html=True)

    cols = st.columns(total)
    for i in range(total):
        sub = subscriptions[i]

        if i < total - 1:
            df_temp = df[(df['product_eom'] == sub) & (df['is_trial'] == 1)]
            units = df_temp['units'].iat[0]
            with cols[i]:
                box_text(sub)
                box_text("{:,}".format(units))

        if i == total - 1:
            df_temp = df[df['is_trial'] == 1]
            units = df_temp['units'].sum()
            with cols[i]:
                box_text(sub)
                box_text("{:,}".format(units))


if __name__ == '__main__':
    main()