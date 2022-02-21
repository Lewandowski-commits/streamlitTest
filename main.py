from datetime import date, timedelta
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

if __name__ == '__main__':
    st.title('NBP currency converter')

    minDate = '2002-01-02'
    maxDate = requests.get(f'https://api.nbp.pl/api/exchangerates/tables/A/').json()[0]['effectiveDate']

    rateDate = st.date_input('Select date on which the rate was valid',
                             min_value=date.fromisoformat(minDate),
                             max_value=date.fromisoformat(maxDate),
                             value=date.fromisoformat(maxDate))


    try:
        request_string = f'https://api.nbp.pl/api/exchangerates/tables/A/{rateDate}?format=json'
        r = requests.get(request_string).json()

        df = pd.json_normalize(r[0]['rates'])

        chosenRate = st.selectbox('Choose your currency', options=df['currency'].sort_values().unique())
        rate = round(df[df["currency"] == chosenRate].iloc[0]["mid"], 2)
        rateCode = df[df["currency"] == chosenRate].iloc[0]["code"]

        st.write(f'1 PLN = {rate} {rateCode}')
        plnAmount = int(st.number_input('How much PLN to convert?', 0))

        st.header(f'{plnAmount} PLN = {round(rate*plnAmount, 2)} {rateCode}')
    except ValueError:
        st.error('The date you picked has no records')

    rateHistoryTimeDelta = timedelta(days=367)
    maxDateDatetime = date.fromisoformat(maxDate)
    rateHistoryMinDate = maxDateDatetime-rateHistoryTimeDelta

    request_string = f'http://api.nbp.pl/api/exchangerates/rates/A/{rateCode}/{rateHistoryMinDate}/{maxDate}?format=json'
    r = requests.get(request_string).json()
    rateHistoryDf = pd.json_normalize(r['rates'])
    rateHistoryDf = rateHistoryDf.drop(['no'], axis = 1)
    rateHistoryDf['effectiveDate'] = pd.to_datetime(rateHistoryDf['effectiveDate'],
                                                    format="%Y/%m/%d")

    rateHistoryFig = px.line(rateHistoryDf,
                            x='effectiveDate',
                            y = 'mid',
                            title = f'Rate of PLN to {rateCode} in last 367 days')

    st.plotly_chart(rateHistoryFig)

else:
    pass

