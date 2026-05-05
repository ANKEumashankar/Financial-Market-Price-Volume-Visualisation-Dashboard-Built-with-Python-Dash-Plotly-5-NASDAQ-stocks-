import dash
from dash import dcc, html, Input, Output, ctx
import plotly.graph_objects as go
import pandas as pd
import requests

API_KEY = "20A7ZLIVMF8U59VR"
TICKERS = ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL"]
data = {}
for ticker in TICKERS:
    df = pd.read_csv(f"cleaned_data/{ticker}_clean.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Volatility"] = df["High"] - df["Low"]
    df["DailyChange"] = ((df["Close"] - df["Open"]) / df["Open"]) * 100
    data[ticker] = df

changes = {}
total_volumes = {}
investors_in = {}
investors_out = {}
for ticker, df in data.items():
    first = df["Close"].iloc[0]
    last = df["Close"].iloc[-1]
    changes[ticker] = round(((last - first) / first) * 100, 2)
    total_volumes[ticker] = df["Volume"].sum()
    investors_in[ticker] = int(df[df["DailyChange"] > 0]["Volume"].sum() / 1000)
    investors_out[ticker] = int(df[df["DailyChange"] < 0]["Volume"].sum() / 1000)

top_gainer = max(changes, key=changes.get)
top_loser = min(changes, key=changes.get)
total_volume = sum(total_volumes.values())
highest_invested = max(total_volumes, key=total_volumes.get)
lowest_invested = min(total_volumes, key=total_volumes.get)

volume_fig = go.Figure()
for ticker, df in data.items():
    volume_fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name=ticker))
volume_fig.update_layout(title="Volume Chart", template="plotly_dark", xaxis_title="Date", yaxis_title="Volume", barmode="group")

close_df = pd.DataFrame({ticker: data[ticker]["Close"].values for ticker in TICKERS})
corr = close_df.corr().round(2)
heat_fig = go.Figure(go.Heatmap(z=corr.values, x=TICKERS, y=TICKERS, colorscale="RdBu", zmin=-1, zmax=1, text=corr.values, texttemplate="%{text}"))
heat_fig.update_layout(title="Correlation Heatmap", template="plotly_dark")

vol_fig = go.Figure()
for ticker, df in data.items():
    vol_fig.add_trace(go.Scatter(x=df["Date"], y=df["Volatility"], mode="lines", name=ticker))
vol_fig.update_layout(title="Volatility Indicator", template="plotly_dark", xaxis_title="Date", yaxis_title="Price Range (USD)")

alerts = []
for ticker, df in data.items():
    avg_vol = df["Volume"].mean()
    for _, row in df.iterrows():
        if row["DailyChange"] > 4:
            alerts.append(f"UP {ticker} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]} +{row[chr(68)+chr(97)+chr(105)+chr(108)+chr(121)+chr(67)+chr(104)+chr(97)+chr(110)+chr(103)+chr(101)]:.2f}%")
        elif row["DailyChange"] < -4:
            alerts.append(f"DOWN {ticker} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]} {row[chr(68)+chr(97)+chr(105)+chr(108)+chr(121)+chr(67)+chr(104)+chr(97)+chr(110)+chr(103)+chr(101)]:.2f}%")
        if row["Volume"] > avg_vol * 2:
            alerts.append(f"SPIKE {ticker} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]}")


app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Stock detail data
STOCK_DETAILS = {
    "AAPL":  {"name":"Apple Inc.",     "sector":"Consumer Technology", "price":"$249.06", "chg":"+0.50%", "chgcolor":"#00ff99", "high":"$258.69", "low":"$194.50", "avg":"$228.02", "vol":"62.4M", "mktcap":"$3.78T", "rsi":"65", "rsicolor":"#7ec8ff", "rsitxt":"Neutral",   "desc":"World largest company. Makes iPhone, Mac, iPad, Apple Watch and services like App Store and iCloud."},
    "TSLA":  {"name":"Tesla Inc.",      "sector":"Electric Vehicles",   "price":"$342.50", "chg":"+2.45%", "chgcolor":"#00ff99", "high":"$488.54", "low":"$182.00", "avg":"$274.90", "vol":"121.8M","mktcap":"$1.09T", "rsi":"58", "rsicolor":"#7ec8ff", "rsitxt":"Neutral",   "desc":"Electric vehicle and clean energy company. Makes Model S/3/X/Y, Cybertruck, and energy storage systems."},
    "MSFT":  {"name":"Microsoft Corp.", "sector":"Enterprise Software",  "price":"$418.20", "chg":"-0.74%", "chgcolor":"#ff4444", "high":"$462.10", "low":"$380.44", "avg":"$421.76", "vol":"28.1M", "mktcap":"$3.10T", "rsi":"42", "rsicolor":"#7ec8ff", "rsitxt":"Neutral",   "desc":"Leading cloud and software company. Owns Azure, Office 365, Teams, Windows, Xbox, and GitHub."},
    "AMZN":  {"name":"Amazon.com Inc.", "sector":"E-Commerce / Cloud",   "price":"$196.80", "chg":"+1.20%", "chgcolor":"#00ff99", "high":"$233.00", "low":"$151.61", "avg":"$193.52", "vol":"45.7M", "mktcap":"$2.08T", "rsi":"56", "rsicolor":"#7ec8ff", "rsitxt":"Neutral",   "desc":"Global e-commerce leader and AWS cloud computing giant. Also runs Prime Video, Alexa, and advertising."},
    "GOOGL": {"name":"Alphabet Inc.",   "sector":"Search / Advertising", "price":"$168.40", "chg":"+0.53%", "chgcolor":"#00ff99", "high":"$200.49", "low":"$146.37", "avg":"$170.31", "vol":"31.2M", "mktcap":"$2.07T", "rsi":"52", "rsicolor":"#7ec8ff", "rsitxt":"Neutral",   "desc":"Parent of Google. Dominates search and online advertising. Also runs YouTube, Google Cloud, and Waymo."},
}

app.layout = html.Div(style={"backgroundColor": "#050a0f", "fontFamily": "Space Grotesk, Arial", "minHeight": "100vh"}, children=[

    html.Div([
        html.Div([
            # AAPL
            html.Div([
                html.Span("AAPL", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$249.06", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+0.50%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","cursor":"pointer","flexShrink":"0"}),
            # TSLA
            html.Div([
                html.Span("TSLA", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$342.50", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+2.45%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","cursor":"pointer","flexShrink":"0"}),
            # MSFT
            html.Div([
                html.Span("MSFT", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$418.20", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("-0.74%", style={"fontSize":"11px","fontWeight":"700","color":"#ff4444","background":"rgba(255,68,68,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","cursor":"pointer","flexShrink":"0"}),
            # AMZN
            html.Div([
                html.Span("AMZN", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$196.80", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+1.20%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","cursor":"pointer","flexShrink":"0"}),
            # GOOGL
            html.Div([
                html.Span("GOOGL", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$168.40", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+0.53%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","cursor":"pointer","flexShrink":"0"}),
            # Repeat for seamless loop
            html.Div([
                html.Span("AAPL", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$249.06", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+0.50%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","flexShrink":"0"}),
            html.Div([
                html.Span("TSLA", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$342.50", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+2.45%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","flexShrink":"0"}),
            html.Div([
                html.Span("MSFT", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$418.20", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("-0.74%", style={"fontSize":"11px","fontWeight":"700","color":"#ff4444","background":"rgba(255,68,68,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","flexShrink":"0"}),
            html.Div([
                html.Span("AMZN", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$196.80", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+1.20%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","borderRight":"1px solid #1a3a5a","flexShrink":"0"}),
            html.Div([
                html.Span("GOOGL", style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8","marginRight":"8px"}),
                html.Span("$168.40", style={"fontSize":"12px","color":"#99b8cc","marginRight":"6px"}),
                html.Span("+0.53%", style={"fontSize":"11px","fontWeight":"700","color":"#00ff99","background":"rgba(0,255,153,0.1)","padding":"2px 7px","borderRadius":"4px"}),
            ], style={"display":"inline-flex","alignItems":"center","padding":"0 24px","height":"38px","flexShrink":"0"}),
        ], className="ticker-moving"),
    ], className="ticker-outer"),

    # Stock detail modal




    # ── STOCK MODAL (pure JS) ──
    html.Div([
        html.Div(id="stock-popup-content", style={
            "background":"#070d1a","border":"1px solid #1a3a5a",
            "borderRadius":"20px","padding":"32px","width":"90%",
            "maxWidth":"700px","maxHeight":"88vh","overflowY":"auto","position":"relative"
        })
    ], id="stock-popup", style={
        "display":"none","position":"fixed","top":"0","left":"0","right":"0","bottom":"0",
        "background":"rgba(0,0,0,0.85)","zIndex":"9999",
        "alignItems":"center","justifyContent":"center"
    }),

    html.Div([
        html.Div([
            html.Div([
                html.Span(className="live-dot"),
                html.Span("LIVE", style={"color": "#00f5a0", "fontSize": "10px", "letterSpacing": "3px", "fontWeight": "600"})
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
            html.H1("FINANCIAL MARKET DASHBOARD",
                style={"fontSize": "28px", "fontWeight": "700", "letterSpacing": "4px",
                       "background": "linear-gradient(90deg, #00b4ff, #00f5a0)",
                       "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
                       "margin": "0"}),
            html.P("Real-Time Price & Volume Analytics — Jul 2024 to Jan 2025",
                style={"color": "#7a9ab8", "fontSize": "12px", "letterSpacing": "2px", "margin": "4px 0 0 0"})
        ], style={"textAlign": "center"}),
    ], style={"background": "linear-gradient(90deg, #050a0f 0%, #0a1628 50%, #050a0f 100%)",
              "borderBottom": "1px solid rgba(0,180,255,0.15)",
              "padding": "20px 32px", "marginBottom": "8px"}),
    html.Div([
        html.Button("🔄", id="refresh-btn", n_clicks=0, style={"backgroundColor": "transparent", "color": "white", "border": "none", "fontSize": "28px", "cursor": "pointer", "position": "fixed", "top": "15px", "right": "20px", "zIndex": "9999"}),
        html.Span(id="refresh-msg"),
        dcc.Interval(id="stop-spin", interval=2000, n_intervals=0, max_intervals=1, disabled=True),
    ], style={"textAlign": "center", "padding": "20px"}),
    html.Div([
        html.Div([
            html.P("📈 TOP GAINER", style={"color": "#aaa", "fontSize": "12px", "letterSpacing": "2px", "margin": "0"}),
            html.H2(top_gainer, style={"color": "white", "margin": "5px 0", "fontSize": "32px"}),
            html.H3(f"+{changes[top_gainer]}%", style={"color": "#00FF99", "margin": "0", "fontSize": "24px"}),
        ], style={"background": "linear-gradient(135deg, #0D2137, #1F4E79)",
                  "padding": "25px", "borderRadius": "15px", "width": "28%",
                  "textAlign": "center", "border": "1px solid #00FF99",
                  "boxShadow": "0 0 15px rgba(0,255,153,0.2)"}),

        html.Div([
            html.P("📉 TOP LOSER", style={"color": "#aaa", "fontSize": "12px", "letterSpacing": "2px", "margin": "0"}),
            html.H2(top_loser, style={"color": "white", "margin": "5px 0", "fontSize": "32px"}),
            html.H3(f"{changes[top_loser]}%", style={"color": "#FF4444", "margin": "0", "fontSize": "24px"}),
        ], style={"background": "linear-gradient(135deg, #2D0D0D, #7B1F1F)",
                  "padding": "25px", "borderRadius": "15px", "width": "28%",
                  "textAlign": "center", "border": "1px solid #FF4444",
                  "boxShadow": "0 0 15px rgba(255,68,68,0.2)"}),

        html.Div([
            html.P("💰 TOTAL VOLUME", style={"color": "#aaa", "fontSize": "12px", "letterSpacing": "2px", "margin": "0"}),
            html.H2("All Stocks", style={"color": "white", "margin": "5px 0", "fontSize": "24px"}),
            html.H3(f"{total_volume:,.0f}", style={"color": "#FFD700", "margin": "0", "fontSize": "18px"}),
        ], style={"background": "linear-gradient(135deg, #1A1500, #4A3800)",
                  "padding": "25px", "borderRadius": "15px", "width": "28%",
                  "textAlign": "center", "border": "1px solid #FFD700",
                  "boxShadow": "0 0 15px rgba(255,215,0,0.2)"}),

    ], style={"display": "flex", "justifyContent": "space-around", "margin": "20px"}),
    html.Div([
        html.P("52 WEEK STATISTICS", style={"color": "#aaa", "textAlign": "center", "letterSpacing": "3px", "fontSize": "13px", "margin": "0 0 10px 0"}),
        html.Div([
            html.Div([
                html.Div([
                    html.P(t, style={"color": "#aaa", "fontSize": "11px", "margin": "0"}),
                    html.P(f"High: {data[t][chr(72)+chr(105)+chr(103)+chr(104)].max():.2f}", style={"color": "#00FF99", "fontSize": "13px", "margin": "2px 0"}),
                    html.P(f"Low: {data[t][chr(76)+chr(111)+chr(119)].min():.2f}", style={"color": "#FF4444", "fontSize": "13px", "margin": "2px 0"}),
                    html.P(f"Avg: {data[t][chr(67)+chr(108)+chr(111)+chr(115)+chr(101)].mean():.2f}", style={"color": "#FFD700", "fontSize": "13px", "margin": "2px 0"}),
                ], style={"background": "#1A1A2E", "padding": "12px", "borderRadius": "10px", "textAlign": "center", "border": "1px solid #333"})
                for t in TICKERS
            ], style={"display": "flex", "justifyContent": "space-around", "gap": "10px"})
        ])
    ], style={"margin": "20px"}),
    html.P("INVESTOR ACTIVITY", style={"color": "#FFD700", "textAlign": "center", "letterSpacing": "3px", "fontSize": "13px", "marginTop": "10px"}),
    html.Div([
        html.Div([
            html.P("🏆 HIGHEST INVESTED", style={"color": "#aaa", "fontSize": "11px", "letterSpacing": "1px", "margin": "0"}),
            html.H2(highest_invested, style={"color": "#00FF99", "margin": "5px 0"}),
            html.P(f"{total_volumes[highest_invested]:,.0f} shares", style={"color": "#aaa", "fontSize": "12px"})
        ], style={"background": "linear-gradient(135deg, #0D2137, #1A3A1A)", "padding": "20px", "borderRadius": "12px", "width": "22%", "textAlign": "center", "border": "1px solid #00FF99"}),

        html.Div([
            html.P("📊 LOWEST INVESTED", style={"color": "#aaa", "fontSize": "11px", "letterSpacing": "1px", "margin": "0"}),
            html.H2(lowest_invested, style={"color": "#FF4444", "margin": "5px 0"}),
            html.P(f"{total_volumes[lowest_invested]:,.0f} shares", style={"color": "#aaa", "fontSize": "12px"})
        ], style={"background": "linear-gradient(135deg, #2D0D0D, #3A1A1A)", "padding": "20px", "borderRadius": "12px", "width": "22%", "textAlign": "center", "border": "1px solid #FF4444"}),

        html.Div(
            [html.P("📈 INVESTORS IN", style={"color": "#aaa", "fontSize": "11px", "letterSpacing": "1px", "margin": "0 0 8px 0"})] +
            [html.P(f"{t}  {investors_in[t]:,}", style={"color": "#00FF99", "margin": "3px", "fontSize": "13px"}) for t in TICKERS],
            style={"background": "linear-gradient(135deg, #0D1A2D, #1A1A3A)", "padding": "20px", "borderRadius": "12px", "width": "22%", "textAlign": "center", "border": "1px solid #0088FF"}),

        html.Div(
            [html.P("📉 INVESTORS OUT", style={"color": "#aaa", "fontSize": "11px", "letterSpacing": "1px", "margin": "0 0 8px 0"})] +
            [html.P(f"{t}  {investors_out[t]:,}", style={"color": "#FF4444", "margin": "3px", "fontSize": "13px"}) for t in TICKERS],
            style={"background": "linear-gradient(135deg, #1A0D0D, #2A1A1A)", "padding": "20px", "borderRadius": "12px", "width": "22%", "textAlign": "center", "border": "1px solid #FF4444"}),

    ], style={"display": "flex", "justifyContent": "space-around", "margin": "20px"}),
    html.Div([
        html.P("🔔 PRICE ALERT", style={"color": "#aaa", "fontSize": "12px", "letterSpacing": "2px", "margin": "0 10px 0 0"}),
        dcc.Dropdown(id="alert-ticker", options=[{"label": t, "value": t} for t in TICKERS], value="AAPL", clearable=False, style={"width": "120px", "color": "black", "marginRight": "10px"}),
        dcc.Input(id="alert-price", type="number", placeholder="250", debounce=True, style={"width": "150px", "height": "40px", "padding": "0 10px", "borderRadius": "8px", "border": "2px solid #FFD700", "backgroundColor": "#0d1f35", "color": "white", "fontSize": "16px", "marginRight": "10px", "textAlign": "center"}),
        html.Button("Set Alert", id="set-alert-btn", n_clicks=0, style={"backgroundColor": "#FFD700", "color": "black", "border": "none", "padding": "10px 20px", "borderRadius": "8px", "cursor": "pointer", "fontWeight": "bold", "marginRight": "10px"}),
        html.Span(id="alert-msg", style={"color": "#00FF99", "marginLeft": "10px", "fontSize": "14px"})
    ], style={"display": "flex", "alignItems": "center", "margin": "20px", "flexWrap": "wrap"}),
    html.Div([
        html.Button("▶ Play", id="play-btn", n_clicks=0,
            style={"backgroundColor": "#00FF99", "color": "black", "border": "none",
                   "padding": "10px 25px", "borderRadius": "8px", "fontSize": "14px",
                   "cursor": "pointer", "fontWeight": "bold", "marginRight": "10px"}),
        html.Button("⏹ Stop", id="stop-btn", n_clicks=0,
            style={"backgroundColor": "#333", "color": "#666", "border": "none",
                   "padding": "10px 25px", "borderRadius": "8px", "fontSize": "14px",
                   "cursor": "pointer", "fontWeight": "bold", "marginRight": "20px"}),
        html.Span(id="play-status", style={"color": "#7a9ab8", "marginLeft": "5px", "fontSize": "13px", "marginRight": "20px"}),
        dcc.Interval(id="anim-interval", interval=300, n_intervals=0, disabled=True),
        html.Label("Time Frame:", style={"color": "white", "marginRight": "10px"}),
        dcc.Dropdown(id="timeframe",
            options=[{"label": "1 Month", "value": 30},
                     {"label": "3 Months", "value": 90},
                     {"label": "6 Months", "value": 180}],
            value=180, clearable=False,
            style={"width": "150px", "color": "black", "marginRight": "20px"}),
        html.Label("Stock:", style={"color": "white", "marginRight": "10px"}),
        dcc.Dropdown(id="stock-selector",
            options=[{"label": t, "value": t} for t in TICKERS],
            value="AAPL", clearable=False,
            style={"width": "150px", "color": "black"}),
    ], style={"display": "flex", "alignItems": "center", "margin": "20px", "flexWrap": "wrap"}),
    dcc.Graph(id="price-chart", style={"margin": "20px"}),
    dcc.Graph(id="volume-fig", style={"margin": "20px"}),
    dcc.Graph(id="heat-fig", style={"margin": "20px"}),
    html.Div([
        html.H3("Market Momentum", style={"color": "#FFD700", "textAlign": "center"}),
        html.Div([html.Div([html.H4(ticker, style={"color": "white", "textAlign": "center"}), html.H3(f"+{changes[ticker]}% UP" if changes[ticker] > 0 else f"{changes[ticker]}% DOWN", style={"color": "#00FF99" if changes[ticker] > 0 else "#FF4444", "textAlign": "center"})], style={"background": "#1A1A2E", "padding": "15px", "borderRadius": "10px", "width": "18%"}) for ticker in TICKERS], style={"display": "flex", "justifyContent": "space-around", "margin": "20px"})
    ], style={"margin": "20px"}),
    dcc.Graph(id="vol-ind", style={"margin": "20px"}),
    dcc.Graph(id="order-book", style={"margin": "20px"}),
    dcc.Graph(id="rsi-chart", style={"margin": "20px"}),
    dcc.Graph(id="volume-profile", style={"margin": "20px"}),
    html.Div([
        html.H3("Live Alerts", style={"color": "#FFD700", "padding": "10px"}),
        html.Div(id="live-alerts-box", style={"backgroundColor": "#1A1A2E", "borderRadius": "10px", "margin": "20px", "padding": "10px", "maxHeight": "400px", "overflowY": "scroll"})
    ], style={"margin": "20px"}),
])




@app.callback(
    Output("stock-modal-div", "style", allow_duplicate=True),
    Input("close-modal-btn", "n_clicks"),
    prevent_initial_call=True)
def close_stock_modal(n):
    return {"display":"none","position":"fixed","top":"0","left":"0",
            "right":"0","bottom":"0","background":"rgba(0,0,0,0.85)",
            "zIndex":"9999","alignItems":"center","justifyContent":"center"}

if __name__ == "__main__":
    app.run(debug=True)