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
app.index_string = """<!DOCTYPE html>
<html>
<head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}
<style>
@keyframes tkrMove{from{transform:translateX(0);}to{transform:translateX(-50%);}}
.tkr-wrap{overflow:hidden;background:#070d1a;border-bottom:1px solid #1a3a5a;height:52px;width:100%;display:flex;align-items:center;}
.tkr-inner{display:flex;flex-direction:row;flex-wrap:nowrap;white-space:nowrap;animation:none;width:max-content;align-items:center;}
.tkr-inner:hover{animation-play-state:paused;}
.tkr-card{display:inline-flex;flex-direction:row;align-items:center;gap:8px;padding:0 14px;margin:0 5px;height:36px;background:linear-gradient(135deg,#0d1e30,#0a1628);border:1px solid #1a5276;border-radius:8px;cursor:pointer;flex-shrink:0;white-space:nowrap;box-shadow:0 0 6px rgba(0,180,255,0.2);}
.tkr-card:hover{background:#1a3a5a;border-color:#00b4ff;box-shadow:0 0 12px rgba(0,180,255,0.5);}
</style>
<script>
function reloadPage(){window.location.reload();}
    // Theme toggle function
    var isDark = true;
    function toggleTheme(){
        isDark = !isDark;
        var btn = document.getElementById("theme-toggle-btn");
        var layout = document.getElementById("main-layout");
        if(!isDark){
            document.body.style.backgroundColor = "#f0f4f8";
            if(layout) layout.style.backgroundColor = "#f0f4f8";
            btn.textContent = "☀️ Light";
            btn.style.background = "#ffd700";
            btn.style.color = "#1a1a1a";
            btn.style.borderColor = "#e6c200";
        } else {
            document.body.style.backgroundColor = "#050a0f";
            if(layout) layout.style.backgroundColor = "#050a0f";
            btn.textContent = "🌙 Dark";
            btn.style.background = "#1a3a5a";
            btn.style.color = "white";
            btn.style.borderColor = "#1a5276";
        }
    }
    // Dark/Light toggle
    var isDark = true;
    document.addEventListener("click", function(e){
        var btn = e.target.closest("#theme-btn");
        if(btn){
            isDark = !isDark;
            var body = document.querySelector("._dash-loading, ._dash-loading-callback, body, #react-entry-point > div");
            var main = document.querySelector("#react-entry-point > div > div");
            if(isDark){
                if(main) main.style.backgroundColor = "#050a0f";
                btn.textContent = "🌙 Dark";
                btn.style.backgroundColor = "#1a3a5a";
            } else {
                if(main) main.style.backgroundColor = "#f0f4f8";
                btn.textContent = "☀️ Light";
                btn.style.backgroundColor = "#e8c84a";
                btn.style.color = "#1a1a1a";
            }
        }
    });
    // Refresh button reloads page
    document.addEventListener("click", function(e){
        if(e.target && (e.target.id==="refresh-btn" || e.target.closest("#refresh-btn"))){
            window.location.reload();
        }
    });
</script>
<style>
#fixed-btns{position:fixed;top:12px;right:15px;z-index:99999;display:flex;flex-direction:column;gap:6px;}
#fixed-btns button{padding:6px 14px;border-radius:8px;border:1px solid #1a5276;background:#1a3a5a;color:white;font-size:12px;cursor:pointer;font-family:Space Grotesk,Arial;}
#fixed-btns button:hover{background:#1a5276;}
</style>
</head>
<body>{%app_entry%}<div id="fixed-btns"><button onclick="window.location.reload()">🔄 Refresh</button><button onclick="toggleTheme()" id="theme-toggle-btn">🌙 Dark</button></div><footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""
app.layout = html.Div(id="main-layout", style={"backgroundColor": "#050a0f", "fontFamily": "Space Grotesk, Arial", "minHeight": "100vh"}, children=[
    html.Div([
        html.Button(id="smclose", n_clicks=0, style={"display":"none"}),
        html.Button(id="smback",  n_clicks=0, style={"display":"none"}),
    ]),
    html.Div(id="smodal",children=[],style={"display":"none","position":"fixed","top":"0","left":"0","right":"0","bottom":"0","background":"rgba(0,0,0,0.85)","zIndex":"9999","alignItems":"center","justifyContent":"center"}),
    html.Div(
        html.Div([
            html.Div([html.Span("AAPL",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $249.06",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +0.50%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],id="tick-AAPL",n_clicks=0,className="tkr-card"),
            html.Div([html.Span("TSLA",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $342.50",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +2.45%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],id="tick-TSLA",n_clicks=0,className="tkr-card"),
            html.Div([html.Span("MSFT",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $418.20",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" -0.74%",style={"fontSize":"11px","fontWeight":"700","color":"#ff4444"})],id="tick-MSFT",n_clicks=0,className="tkr-card"),
            html.Div([html.Span("AMZN",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $196.80",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +1.20%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],id="tick-AMZN",n_clicks=0,className="tkr-card"),
            html.Div([html.Span("GOOGL",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $168.40",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +0.53%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],id="tick-GOOGL",n_clicks=0,className="tkr-card"),
            html.Div([html.Span("AAPL",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $249.06",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +0.50%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],className="tkr-card"),
            html.Div([html.Span("TSLA",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $342.50",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +2.45%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],className="tkr-card"),
            html.Div([html.Span("MSFT",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $418.20",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" -0.74%",style={"fontSize":"11px","fontWeight":"700","color":"#ff4444"})],className="tkr-card"),
            html.Div([html.Span("AMZN",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $196.80",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +1.20%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],className="tkr-card"),
            html.Div([html.Span("GOOGL",style={"fontSize":"13px","fontWeight":"700","color":"#e0eaf8"}),html.Span(" $168.40",style={"fontSize":"12px","color":"#7ec8ff"}),html.Span(" +0.53%",style={"fontSize":"11px","fontWeight":"700","color":"#00ff99"})],className="tkr-card"),
        ],className="tkr-inner"),
        className="tkr-wrap"
    ),
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
        html.Button("🔄 Refresh", id="refresh-btn", n_clicks=0, style={"backgroundColor": "#1a3a5a", "color": "white", "border": "1px solid #1a5276", "fontSize": "13px", "cursor": "pointer", "padding": "6px 14px", "borderRadius": "8px", "position": "fixed", "top": "15px", "right": "20px", "zIndex": "9999"}),
        html.Span(id="refresh-msg"),
        html.Button("🌙 Dark", id="theme-btn", n_clicks=0, style={"backgroundColor": "#1a3a5a", "color": "white", "border": "1px solid #1a5276", "fontSize": "13px", "cursor": "pointer", "padding": "6px 14px", "borderRadius": "8px", "position": "fixed", "top": "50px", "right": "20px", "zIndex": "9999"}),
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

@app.callback(Output("heat-fig", "figure"), Input("stock-selector", "value"))
def update_heatmap(selected):
    fig = go.Figure()
    for ticker in TICKERS:
        opacity = 1.0 if ticker == selected else 0.2
        mask = [1 if t == selected or t == ticker else 0 for t in TICKERS]
        fig.add_trace(go.Heatmap(
            z=[[corr.loc[ticker, t] * (1 if t == selected else 0.2) for t in TICKERS]],
            x=TICKERS, y=[ticker],
            colorscale="RdBu", zmin=-1, zmax=1,
            showscale=False, opacity=opacity))
    fig2 = go.Figure(go.Heatmap(
        z=corr.values, x=TICKERS, y=TICKERS,
        colorscale="RdBu", zmin=-1, zmax=1,
        text=corr.values, texttemplate="%{text}"))
    idx = TICKERS.index(selected)
    for i in range(len(TICKERS)):
        for j in range(len(TICKERS)):
            if i != idx and j != idx:
                fig2.add_shape(type="rect",
                    x0=j-0.5, x1=j+0.5, y0=i-0.5, y1=i+0.5,
                    fillcolor="rgba(0,0,0,0.6)", line_width=0)
    fig2.update_layout(title=f"Correlation Heatmap — {selected} highlighted", template="plotly_dark")
    return fig2

@app.callback(
    Output("refresh-btn", "children"),
    Output("refresh-msg", "children"),
    Output("stop-spin", "disabled"),
    Output("stop-spin", "n_intervals"),
    Input("refresh-btn", "n_clicks"),
    Input("stop-spin", "n_intervals"))
def refresh_data(n, intervals):
    if n and n > 0 and (intervals is None or intervals == 0):
        return "⏳", dash.no_update, False, 0
    return "🔄 Refresh", dash.no_update, True, 0




@app.callback(Output("price-chart", "figure"), Input("timeframe", "value"), Input("stock-selector", "value"), Input("anim-interval", "n_intervals"), Input("play-btn", "n_clicks"))
def update_chart(days, ticker, n_intervals, play_clicks):
    df = data[ticker].tail(days).reset_index(drop=True)
    sma20 = df["Close"].rolling(window=20).mean()
    sma50 = df["Close"].rolling(window=50).mean()
    price_bins = pd.cut(df["Close"], bins=15)
    vol_profile = df.groupby(price_bins, observed=True)["Volume"].sum()
    max_vol = vol_profile.max()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=ticker,
        increasing_line_color="#00FF99", decreasing_line_color="#FF4444"))
    fig.add_trace(go.Scatter(x=df["Date"], y=sma20, mode="lines", name="SMA 20", line=dict(color="#FFD700", dash="dash", width=1)))
    fig.add_trace(go.Scatter(x=df["Date"], y=sma50, mode="lines", name="SMA 50", line=dict(color="#00CCFF", dash="dot", width=1)))
    if n_intervals and n_intervals > 0:
        idx = min(n_intervals % len(df), len(df)-1)
        heartbeat_x = df["Date"].iloc[:idx+1]
        heartbeat_y = df["Close"].iloc[:idx+1]
        fig.add_trace(go.Scatter(x=heartbeat_x, y=heartbeat_y, mode="lines",
            name="Live Price", line=dict(color="#FF00FF", width=2)))
        fig.add_trace(go.Scatter(x=[df["Date"].iloc[idx]], y=[df["Close"].iloc[idx]],
            mode="markers", name="Current",
            marker=dict(color="#FF00FF", size=10, symbol="circle")))
    for bin_range, vol in vol_profile.items():
        mid = (bin_range.left + bin_range.right) / 2
        bar_width = (vol / max_vol) * 15
        color = "rgba(0,255,153,0.4)" if vol > vol_profile.median() else "rgba(255,68,68,0.4)"
        fig.add_shape(type="rect",
            x0=df["Date"].iloc[-1], x1=df["Date"].iloc[-1],
            y0=bin_range.left, y1=bin_range.right,
            fillcolor=color, line_width=0)
    fig.update_layout(
        title=f"{ticker} — Candlestick + Volume Profile + Heartbeat",
        template="plotly_dark", xaxis_title="Date", yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False, height=600)
    return fig

@app.callback(Output("volume-profile", "figure"), Input("timeframe", "value"), Input("stock-selector", "value"))
def update_volume_profile(days, selected):
    fig = go.Figure()
    for ticker, df in data.items():
        filtered = df.tail(days)
        price_bins = pd.cut(filtered["Close"], bins=20)
        vol_profile = filtered.groupby(price_bins, observed=True)["Volume"].sum()
        opacity = 1.0 if ticker == selected else 0.15
        fig.add_trace(go.Bar(x=vol_profile.values, y=[str(b) for b in vol_profile.index], orientation="h", name=ticker, opacity=opacity))
    fig.update_layout(title=f"Volume Profile — {selected} highlighted", template="plotly_dark", xaxis_title="Total Volume", yaxis_title="Price Range", barmode="group")
    return fig

@app.callback(Output("volume-fig", "figure"), Input("timeframe", "value"), Input("stock-selector", "value"))
def update_volume_chart(days, selected):
    fig = go.Figure()
    for ticker, df in data.items():
        opacity = 1.0 if ticker == selected else 0.15
        fig.add_trace(go.Bar(x=df["Date"].tail(days), y=df["Volume"].tail(days), name=ticker, opacity=opacity))
    fig.update_layout(title=f"Volume Chart — {selected} highlighted", template="plotly_dark", xaxis_title="Date", yaxis_title="Volume", barmode="group")
    return fig

@app.callback(Output("vol-ind", "figure"), Input("timeframe", "value"), Input("stock-selector", "value"))
def update_volatility(days, selected):
    fig = go.Figure()
    for ticker, df in data.items():
        filtered = df.tail(days)
        opacity = 1.0 if ticker == selected else 0.15
        fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["Volatility"], mode="lines", name=ticker, opacity=opacity))
    fig.update_layout(title=f"Volatility — {selected} highlighted", template="plotly_dark", xaxis_title="Date", yaxis_title="Price Range (USD)")
    return fig

@app.callback(Output("order-book", "figure"), Input("timeframe", "value"), Input("stock-selector", "value"))
def update_order_book(days, selected):
    fig = go.Figure()
    price = float(data[selected]["Close"].iloc[-1])
    bid_prices = [round(price - j * 0.10, 2) for j in range(1, 6)]
    ask_prices = [round(price + j * 0.10, 2) for j in range(1, 6)]
    bid_sizes = [1000 - j * 150 for j in range(5)]
    ask_sizes = [1000 - j * 150 for j in range(5)]
    fig.add_trace(go.Bar(x=bid_sizes, y=[str(p) for p in bid_prices], orientation="h", name=f"{selected} Bid", marker_color="#00FF99"))
    fig.add_trace(go.Bar(x=ask_sizes, y=[str(p) for p in ask_prices], orientation="h", name=f"{selected} Ask", marker_color="#FF4444"))
    fig.update_layout(title=f"Order Book - {selected} Bid vs Ask", template="plotly_dark", xaxis_title="Order Size", yaxis_title="Price (USD)", barmode="group")
    return fig

@app.callback(Output("live-alerts-box", "children"), Input("stock-selector", "value"))
def update_alerts(selected):
    filtered = []
    df = data[selected]
    avg_vol = df["Volume"].mean()
    for _, row in df.iterrows():
        if row["DailyChange"] > 4:
            filtered.append(f"📈 UP {selected} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]} +{row[chr(68)+chr(97)+chr(105)+chr(108)+chr(121)+chr(67)+chr(104)+chr(97)+chr(110)+chr(103)+chr(101)]:.2f}%")
        elif row["DailyChange"] < -4:
            filtered.append(f"📉 DOWN {selected} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]} {row[chr(68)+chr(97)+chr(105)+chr(108)+chr(121)+chr(67)+chr(104)+chr(97)+chr(110)+chr(103)+chr(101)]:.2f}%")
        if row["Volume"] > avg_vol * 2:
            filtered.append(f"🔔 SPIKE {selected} {str(row[chr(68)+chr(97)+chr(116)+chr(101)])[:10]}")
    return [html.P(a, style={"color": "white", "padding": "8px", "borderBottom": "1px solid #333", "margin": "0"}) for a in filtered[:20]]



@app.callback(Output("rsi-chart", "figure"), Input("stock-selector", "value"), Input("timeframe", "value"))
def update_rsi(ticker, days):
    df = data[ticker].tail(days).copy()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=rsi, mode="lines", name="RSI", line=dict(color="#00CCFF", width=2)))
    fig.add_hline(y=70, line_dash="dash", line_color="#FF4444", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="#00FF99", annotation_text="Oversold (30)")
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,255,153,0.1)", line_width=0)
    fig.update_layout(
        title=f"{ticker} RSI Indicator (14 days)",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="RSI Value",
        yaxis=dict(range=[0, 100]),
        height=300)
    return fig


@app.callback(
    Output('alert-msg', 'children'),
    Input('set-alert-btn', 'n_clicks'),
    Input('alert-ticker', 'value'),
    Input('alert-price', 'value'))
def check_alert(n, ticker, alert_price):
    if not n or n == 0 or alert_price is None:
        return ''
    current = float(data[ticker]['Close'].iloc[-1])
    high = float(data[ticker]['High'].max())
    low = float(data[ticker]['Low'].min())
    ap = float(alert_price)
    if abs(current - ap) / current < 0.02:
        return f'ALERT! {ticker} current ${current:.2f} is very close to ${ap}!'
    elif ap > high:
        return f'WARNING: ${ap} is above period high ${high:.2f} for {ticker}'
    elif ap < low:
        return f'WARNING: ${ap} is below period low ${low:.2f} for {ticker}'
    elif ap > current:
        return f'Alert set! {ticker} at ${current:.2f} needs +${ap-current:.2f} to reach ${ap}'
    else:
        return f'Alert set! {ticker} at ${current:.2f} needs -${current-ap:.2f} to reach ${ap}'

@app.callback(
    Output("anim-interval", "disabled"),
    Output("play-btn", "style"),
    Output("stop-btn", "style"),
    Output("play-status", "children"),
    Input("play-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"))
def control_animation(play, stop):
    play_style = {"backgroundColor": "#00FF99", "color": "black", "border": "none",
                  "padding": "10px 25px", "borderRadius": "8px", "fontSize": "14px",
                  "cursor": "pointer", "fontWeight": "bold", "marginRight": "10px"}
    stop_style = {"backgroundColor": "#FF3B5C", "color": "white", "border": "none",
                  "padding": "10px 25px", "borderRadius": "8px", "fontSize": "14px",
                  "cursor": "pointer", "fontWeight": "bold"}
    stop_inactive = {**stop_style, "backgroundColor": "#333", "color": "#666"}
    if ctx.triggered_id == "play-btn" and play and play % 2 == 1:
        return False, {**play_style, "backgroundColor": "#333", "color": "#666"}, stop_style, "⏳ Animating..."
    return True, play_style, stop_inactive, "⏹ Stopped"


@app.callback(
    Output("smodal","children"),
    Output("smodal","style"),
    Input("tick-AAPL","n_clicks"),
    Input("tick-TSLA","n_clicks"),
    Input("tick-MSFT","n_clicks"),
    Input("tick-AMZN","n_clicks"),
    Input("tick-GOOGL","n_clicks"),
    prevent_initial_call=True)
def show_stock(a,b,c,d,e):
    from dash import ctx
    info = {
        "AAPL":{"name":"Apple Inc.","sector":"Technology","price":249.06,"chg":"+0.50%","high":258.69,"low":194.50,"avg":228.02,"vol":"62.4M","mktcap":"$3.78T","rsi":65,"up":True,"desc":"World largest company. Makes iPhone, Mac, iPad, Apple Watch, App Store and iCloud."},
        "TSLA":{"name":"Tesla Inc.","sector":"Electric Vehicles","price":342.50,"chg":"+2.45%","high":488.54,"low":182.00,"avg":274.90,"vol":"121.8M","mktcap":"$1.09T","rsi":58,"up":True,"desc":"Electric vehicle and clean energy company. Makes Model S/3/X/Y, Cybertruck and energy storage."},
        "MSFT":{"name":"Microsoft Corp.","sector":"Software","price":418.20,"chg":"-0.74%","high":462.10,"low":380.44,"avg":421.76,"vol":"28.1M","mktcap":"$3.10T","rsi":42,"up":False,"desc":"Leading cloud and software company. Owns Azure, Office 365, Teams, Windows, Xbox and GitHub."},
        "AMZN":{"name":"Amazon.com Inc.","sector":"E-Commerce","price":196.80,"chg":"+1.20%","high":233.00,"low":151.61,"avg":193.52,"vol":"45.7M","mktcap":"$2.08T","rsi":56,"up":True,"desc":"Global e-commerce and AWS cloud giant. Also runs Prime Video, Alexa and advertising."},
        "GOOGL":{"name":"Alphabet Inc.","sector":"Search/Ads","price":168.40,"chg":"+0.53%","high":200.49,"low":146.37,"avg":170.31,"vol":"31.2M","mktcap":"$2.07T","rsi":52,"up":True,"desc":"Parent of Google. Dominates search and ads. Also runs YouTube, Google Cloud and Waymo."},
    }
    sym = ctx.triggered_id.replace("tick-","") if ctx.triggered_id else None
    if not sym or sym not in info: return [],{"display":"none"}
    s = info[sym]
    pc = "#00ff99" if s["up"] else "#ff4444"
    rc = "#ff4444" if s["rsi"]>70 else "#00ff99" if s["rsi"]<30 else "#7ec8ff"
    rt = "Overbought" if s["rsi"]>70 else "Oversold" if s["rsi"]<30 else "Neutral"
    df_s = data[sym].tail(60)
    fig_c = go.Figure()
    fig_c.add_trace(go.Candlestick(x=df_s.index,open=df_s["Open"],high=df_s["High"],low=df_s["Low"],close=df_s["Close"],increasing_line_color="#00ff99",decreasing_line_color="#ff4444",name=sym))
    fig_c.add_trace(go.Scatter(x=df_s.index,y=df_s["Close"].rolling(20).mean(),line=dict(color="#ffd700",width=1.5,dash="dash"),name="SMA 20"))
    fig_c.update_layout(paper_bgcolor="#070d1a",plot_bgcolor="#070d1a",font=dict(color="#7ec8ff"),height=260,margin=dict(l=40,r=20,t=30,b=40),xaxis=dict(gridcolor="#0f2a40",rangeslider_visible=False),yaxis=dict(gridcolor="#0f2a40"),title=dict(text=f"{sym} — Last 60 Days",font=dict(color="#7ec8ff",size=12)))
    cv = ["#00ff99" if c>=o else "#ff4444" for c,o in zip(df_s["Close"],df_s["Open"])]
    fig_v = go.Figure(go.Bar(x=df_s.index,y=df_s["Volume"],marker_color=cv))
    fig_v.update_layout(paper_bgcolor="#070d1a",plot_bgcolor="#070d1a",font=dict(color="#7ec8ff"),height=130,margin=dict(l=40,r=20,t=10,b=40),xaxis=dict(gridcolor="#0f2a40"),yaxis=dict(gridcolor="#0f2a40"),showlegend=False)
    def stat(lbl,val,col="#99b8cc"):
        return html.Div([
            html.P(lbl,style={"fontSize":"9px","color":"#4a6a88","letterSpacing":"1px","margin":"0","textTransform":"uppercase"}),
            html.P(val,style={"fontSize":"18px","fontWeight":"700","color":col,"margin":"4px 0 0"}),
        ],style={"background":"#0a1825","border":"1px solid #0f2a40","borderRadius":"10px","padding":"14px","flex":"1","minWidth":"110px"})
    modal = html.Div([html.Div([
        html.Button("✕",id="smclose",n_clicks=0,style={"position":"absolute","top":"16px","right":"16px","background":"#1a3a5a","color":"#7ec8ff","border":"none","width":"36px","height":"36px","borderRadius":"50%","fontSize":"16px","cursor":"pointer","fontWeight":"700"}),
        html.H2(sym,style={"fontSize":"36px","fontWeight":"700","color":"#e0eaf8","margin":"0"}),
        html.P(f"{s['name']} · {s['sector']}",style={"color":"#4a6a88","fontSize":"13px","margin":"4px 0 12px"}),
        html.Div([
            html.Span(f"${s['price']:.2f}",style={"fontSize":"32px","fontWeight":"700","color":pc,"marginRight":"12px"}),
            html.Span(s["chg"],style={"fontSize":"18px","fontWeight":"700","color":pc}),
        ],style={"display":"flex","alignItems":"baseline","marginBottom":"14px"}),
        html.P(s["desc"],style={"color":"#7a9ab8","fontSize":"13px","lineHeight":"1.6","background":"#0a1825","padding":"12px","borderRadius":"8px","border":"1px solid #0f2a40","marginBottom":"16px"}),
        html.Div([stat("52W High",f"${s['high']}","#00ff99"),stat("52W Low",f"${s['low']}","#ff4444"),stat("Avg Price",f"${s['avg']}","#ffd700"),stat("Volume",s["vol"]),stat("Mkt Cap",s["mktcap"]),stat(f"RSI ({s['rsi']})",rt,rc)],style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"16px"}),
        html.P("PRICE CHART",style={"color":"#4a6a88","fontSize":"10px","letterSpacing":"2px","margin":"0 0 4px"}),
        dcc.Graph(figure=fig_c,config={"displayModeBar":False},style={"marginBottom":"8px"}),
        html.P("VOLUME",style={"color":"#4a6a88","fontSize":"10px","letterSpacing":"2px","margin":"0 0 4px"}),
        dcc.Graph(figure=fig_v,config={"displayModeBar":False},style={"marginBottom":"16px"}),
        html.Button("← BACK",id="smback",n_clicks=0,style={"width":"100%","padding":"12px","borderRadius":"10px","border":"1px solid #1a3a5a","background":"#0a1825","color":"#7ec8ff","fontSize":"13px","fontWeight":"700","cursor":"pointer"}),
    ],style={"position":"relative","background":"#070d1a","border":"1px solid #1a3a5a","borderRadius":"20px","padding":"32px","width":"92%","maxWidth":"900px","maxHeight":"92vh","overflowY":"auto"})],
    style={"display":"flex","alignItems":"center","justifyContent":"center","width":"100%","height":"100%"})
    show = {"display":"flex","position":"fixed","top":"0","left":"0","right":"0","bottom":"0","background":"rgba(0,0,0,0.85)","zIndex":"9999","alignItems":"center","justifyContent":"center"}
    return modal, show

@app.callback(
    Output("smodal","style",allow_duplicate=True),
    Input("smclose","n_clicks"),
    Input("smback","n_clicks"),
    prevent_initial_call=True)
def close_stock(a,b):
    return {"display":"none"}


@app.callback(
    Output("main-layout", "style"),
    Output("theme-btn", "children"),
    Output("theme-btn", "style"),
    Input("theme-btn", "n_clicks"),
    prevent_initial_call=True)
def toggle_theme(n):
    dark_style = {"backgroundColor":"#050a0f","fontFamily":"Space Grotesk, Arial","minHeight":"100vh","color":"#e0eaf8"}
    light_style = {"backgroundColor":"#f0f4f8","fontFamily":"Space Grotesk, Arial","minHeight":"100vh","color":"#1a1a1a"}
    btn_dark = {"backgroundColor":"#1a3a5a","color":"white","border":"1px solid #1a5276","fontSize":"13px","cursor":"pointer","padding":"6px 14px","borderRadius":"8px","position":"fixed","top":"50px","right":"20px","zIndex":"9999"}
    btn_light = {"backgroundColor":"#ffd700","color":"#1a1a1a","border":"1px solid #e6c200","fontSize":"13px","cursor":"pointer","padding":"6px 14px","borderRadius":"8px","position":"fixed","top":"50px","right":"20px","zIndex":"9999"}
    if n % 2 == 1:
        return light_style, "🌙 Dark", btn_light
    return dark_style, "☀️ Light", btn_dark

if __name__ == "__main__":
    app.run(debug=True)