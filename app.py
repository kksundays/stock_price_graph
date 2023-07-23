import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('株価可視化アプリ')

st.sidebar.write("""
# 株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 1000, 20)

st.write(f"""
### 過去 **{days}日間** の株価
""")

@st.cache_data
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: 
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '(ドル)範囲を指定してください。',
        0.0, 3500.0, (0.0, 5000.0)
    )
    ymin_jp, ymax_jp = st.sidebar.slider(
        '(円)範囲を指定してください。',
        0.0, 35000.0, (0.0, 35000.0)
    )

    tickers = {
        'apple': 'AAPL',
        'mata': 'META',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN',
        'SP500' : '^GSPC',
        'ダウ' : '^DJI'
    }
    
    tickers_jp = {
        'TOYOTA' : '7203.T',
        'SONY' : '6758.T',
        'SoftBank': '9434.T',
        '東京海上' : '8766.T' ,
        '伊藤忠' : '8001.T',
        '日経225' : '^N225',
    }

    df = get_data(days, tickers)
    df_jp = get_data(days, tickers_jp)

    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['apple','mata','google','microsoft']
    )
    companies_jp = st.multiselect(
        '会社名を選択してください。',
        list(df_jp.index),
        ['SONY','東京海上','日経225']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    elif not companies_jp:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        data_jp = df_jp.loc[companies_jp]

        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)

        st.write("### 株価 (JP円)", data_jp.sort_index())
        data_jp = data_jp.T.reset_index()
        data_jp = pd.melt(data_jp, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(JP円)'}
        )
        chart_jp = (
            alt.Chart(data_jp)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(JP円):Q", stack=None, scale=alt.Scale(domain=[ymin_jp, ymax_jp])),
                color='Name:N'
            )
        )
        st.altair_chart(chart_jp, use_container_width=True)

except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )