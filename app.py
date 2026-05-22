import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings, json, uuid, os

warnings.filterwarnings("ignore")

st.set_page_config(page_title="AI 주식 예측 분석기", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────
# 인기 한국 주식 사전
# ─────────────────────────────────────────────────────────────────
_POPULAR_KRX = {
    "삼성전자":("005930","KOSPI"),"삼성전자우":("005935","KOSPI"),
    "SK하이닉스":("000660","KOSPI"),"삼성바이오로직스":("207940","KOSPI"),
    "LG에너지솔루션":("373220","KOSPI"),"현대차":("005380","KOSPI"),
    "셀트리온":("068270","KOSPI"),"삼성SDI":("006400","KOSPI"),
    "POSCO홀딩스":("005490","KOSPI"),"KB금융":("105560","KOSPI"),
    "신한지주":("055550","KOSPI"),"NAVER":("035420","KOSPI"),
    "네이버":("035420","KOSPI"),"기아":("000270","KOSPI"),
    "LG화학":("051910","KOSPI"),"현대모비스":("012330","KOSPI"),
    "LG전자":("066570","KOSPI"),"하나금융지주":("086790","KOSPI"),
    "SK텔레콤":("017670","KOSPI"),"카카오뱅크":("323410","KOSPI"),
    "한국전력":("015760","KOSPI"),"포스코퓨처엠":("003670","KOSPI"),
    "삼성물산":("028260","KOSPI"),"SK이노베이션":("096770","KOSPI"),
    "한화에어로스페이스":("012450","KOSPI"),"한화솔루션":("009830","KOSPI"),
    "두산에너빌리티":("034020","KOSPI"),"크래프톤":("259960","KOSPI"),
    "하이브":("352820","KOSPI"),"엔씨소프트":("036570","KOSPI"),
    "카카오":("035720","KOSDAQ"),"카카오페이":("377300","KOSPI"),
    "에코프로비엠":("247540","KOSDAQ"),"에코프로":("086520","KOSDAQ"),
    "셀트리온헬스케어":("091990","KOSDAQ"),"알테오젠":("196170","KOSDAQ"),
    "리노공업":("058470","KOSDAQ"),"HLB":("028300","KOSDAQ"),
    "현대건설":("000720","KOSPI"),"고려아연":("010130","KOSPI"),
    "SK":("034730","KOSPI"),"LG":("003550","KOSPI"),
    "롯데케미칼":("011170","KOSPI"),"KT":("030200","KOSPI"),
    "현대중공업":("329180","KOSPI"),"삼성중공업":("010140","KOSPI"),
    "대한항공":("003490","KOSPI"),"아모레퍼시픽":("090430","KOSPI"),
    # 추가
    "현대로템":("064350","KOSPI"),"한화오션":("042660","KOSPI"),
    "HD현대":("267250","KOSPI"),"삼성전기":("009150","KOSPI"),
    "LG디스플레이":("034220","KOSPI"),"기업은행":("024110","KOSPI"),
    "우리금융지주":("316140","KOSPI"),"한국항공우주":("047810","KOSPI"),
    "현대글로비스":("086280","KOSPI"),"두산밥캣":("241560","KOSPI"),
    "HD현대일렉트릭":("267260","KOSPI"),"LS일렉트릭":("010120","KOSPI"),
    "메리츠금융지주":("138040","KOSPI"),"삼성생명":("032830","KOSPI"),
    "SK바이오팜":("326030","KOSPI"),"카카오게임즈":("293490","KOSDAQ"),
    "펄어비스":("263750","KOSDAQ"),"컴투스":("078340","KOSDAQ"),
    "위메이드":("112040","KOSDAQ"),"더블유게임즈":("192080","KOSDAQ"),
    "롯데웰푸드":("280360","KOSPI"),"오리온":("271560","KOSPI"),
    "CJ제일제당":("097950","KOSPI"),"농심":("004370","KOSPI"),
    "현대해상":("001450","KOSPI"),"삼성화재":("000810","KOSPI"),
}

# 한글 미국 주식명 → 티커 매핑
_KO_US_MAP = {
    "애플":("AAPL","Apple"),"테슬라":("TSLA","Tesla"),
    "구글":("GOOGL","Alphabet"),"알파벳":("GOOGL","Alphabet"),
    "마이크로소프트":("MSFT","Microsoft"),"MS":("MSFT","Microsoft"),
    "아마존":("AMZN","Amazon"),"메타":("META","Meta"),
    "페이스북":("META","Meta"),"엔비디아":("NVDA","NVIDIA"),
    "넷플릭스":("NFLX","Netflix"),"인텔":("INTC","Intel"),
    "퀄컴":("QCOM","Qualcomm"),"버크셔":("BRK-B","Berkshire Hathaway"),
    "JP모건":("JPM","JPMorgan"),"골드만삭스":("GS","Goldman Sachs"),
    "존슨앤존슨":("JNJ","Johnson & Johnson"),"화이자":("PFE","Pfizer"),
    "코카콜라":("KO","Coca-Cola"),"맥도날드":("MCD","McDonald's"),
    "나이키":("NKE","Nike"),"스타벅스":("SBUX","Starbucks"),
    "보잉":("BA","Boeing"),"팔란티어":("PLTR","Palantir"),
    "우버":("UBER","Uber"),"에어비앤비":("ABNB","Airbnb"),
    "스포티파이":("SPOT","Spotify"),"줌":("ZM","Zoom"),
    "페이팔":("PYPL","PayPal"),"코인베이스":("COIN","Coinbase"),
    "리비안":("RIVN","Rivian"),"루시드":("LCID","Lucid"),
    "AMD":("AMD","AMD"),"ARM":("ARM","ARM Holdings"),
    "브로드컴":("AVGO","Broadcom"),"TSMC":("TSM","TSMC"),
    "일라이릴리":("LLY","Eli Lilly"),"버텍스":("VRTX","Vertex"),
    "모더나":("MRNA","Moderna"),"바이오엔텍":("BNTX","BioNTech"),
    "스페이스엑스":("SPCE","Virgin Galactic"),"로켓랩":("RKLB","Rocket Lab"),
    "엑슨모빌":("XOM","ExxonMobil"),"셰브론":("CVX","Chevron"),
    "비자":("V","Visa"),"마스터카드":("MA","Mastercard"),
}

# ─────────────────────────────────────────────────────────────────
# 예측 저장/로드 (Supabase 우선, 로컬 JSON 폴백)
# ─────────────────────────────────────────────────────────────────
PRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions.json")

def _get_sb():
    """Supabase 클라이언트 반환. secrets 없으면 None."""
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL","")
        key = st.secrets.get("SUPABASE_KEY","")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def load_predictions() -> list:
    sb = _get_sb()
    if sb:
        try:
            res = sb.table("predictions").select("*").order("saved_at", desc=True).execute()
            rows = res.data or []
            # forecasts 컬럼은 jsonb → 이미 list로 반환됨
            return rows
        except Exception:
            pass
    # 로컬 폴백
    if not os.path.exists(PRED_FILE):
        return []
    try:
        with open(PRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("predictions", [])
    except Exception:
        return []

def save_prediction(ticker, company, base_price, future_fc, model_name) -> str:
    pid = str(uuid.uuid4())[:8]
    record = {
        "id": pid, "ticker": ticker, "company": company,
        "saved_at": datetime.today().strftime("%Y-%m-%d %H:%M"),
        "base_price": round(float(base_price), 2),
        "model": model_name,
        "forecasts": [
            {"date": str(row["ds"])[:10],
             "predicted": round(float(row["yhat"]), 2),
             "lower":     round(float(row["yhat_lower"]), 2),
             "upper":     round(float(row["yhat_upper"]), 2)}
            for _, row in future_fc.iterrows()
        ],
    }
    sb = _get_sb()
    if sb:
        try:
            sb.table("predictions").insert(record).execute()
            return pid
        except Exception:
            pass
    # 로컬 폴백
    preds = load_predictions()
    preds.append(record)
    with open(PRED_FILE, "w", encoding="utf-8") as f:
        json.dump({"predictions": preds}, f, ensure_ascii=False, indent=2)
    return pid

def delete_prediction(pid: str):
    sb = _get_sb()
    if sb:
        try:
            sb.table("predictions").delete().eq("id", pid).execute()
            return
        except Exception:
            pass
    # 로컬 폴백
    preds = [p for p in load_predictions() if p["id"] != pid]
    with open(PRED_FILE, "w", encoding="utf-8") as f:
        json.dump({"predictions": preds}, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────────────
# Sidebar – 메뉴 + 설정
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 메뉴")
    page = st.radio("", ["📈 주가 분석", "🎯 예측 검증"], label_visibility="collapsed")
    st.divider()

    if page == "📈 주가 분석":
        st.subheader("⚙️ 분석 설정")
        market_choice = st.radio("대상 시장",
            ["자동 감지","한국 (KRX)","미국 (NYSE/NASDAQ)"], index=0)
        history_period = st.selectbox("과거 데이터 기간",
            [90,180,365,730], index=2,
            format_func=lambda x: f"{x}일 ({x//30}개월)")
        st.divider()
        st.subheader("🌐 글로벌 지수 표시")
        show_sp500  = st.checkbox("S&P 500", value=True)
        show_nasdaq = st.checkbox("NASDAQ Composite", value=True)
        show_kospi  = st.checkbox("KOSPI", value=True)
        show_dji    = st.checkbox("다우존스 (DJI)", value=False)
        st.divider()
        st.markdown("**입력 예시**\n- 한국: `삼성전자`, `005930`\n- 미국: `Apple`, `TSLA`")

    elif page == "🎯 예측 검증":
        _sb_preds = load_predictions()
        if _sb_preds:
            st.subheader("📋 저장된 예측")
            _sb_sorted = sorted(_sb_preds, key=lambda x: x["saved_at"], reverse=True)
            _sb_sel = st.radio(
                "예측 목록",
                range(len(_sb_sorted)),
                format_func=lambda i: (
                    f"📅 {_sb_sorted[i]['saved_at'][:10]}\n"
                    f"  {_sb_sorted[i]['company']}"
                ),
                label_visibility="collapsed",
                key="_sb_pred_radio",
            )
            st.session_state["_pred_sel_idx"] = _sb_sel
        else:
            st.info("저장된 예측 없음")

    st.caption("⚠️ AI 통계 예측 참고용 · 투자 조언 아님")

# ─────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────
def _has_korean(t): return any("가"<=c<="힣" for c in t)

def _to_naive(idx):
    idx = pd.to_datetime(idx)
    return idx.tz_convert("UTC").tz_localize(None) if idx.tz else idx

def _clean_yf(raw):
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)
    raw.index = _to_naive(raw.index)
    return raw

# ─────────────────────────────────────────────────────────────────
# KRX 검색
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=7200, show_spinner=False)
def _load_krx_via_pykrx():
    try:
        from pykrx import stock as pyk
        today = datetime.today().strftime("%Y%m%d")
        frames=[]
        for mkt in ["KOSPI","KOSDAQ"]:
            df = pyk.get_market_sector_belonging(today, mkt)
            if df is not None and not df.empty:
                df["_market"]=mkt; frames.append(df)
        if not frames: return pd.DataFrame()
        combined=pd.concat(frames)
        nc=next((c for c in combined.columns if "한글" in c or ("종목명" in c and "영문" not in c)),None)
        if not nc: return pd.DataFrame()
        out=combined[[nc,"_market"]].rename(columns={nc:"name"})
        out.index=out.index.astype(str).str.zfill(6)
        return out
    except Exception: return pd.DataFrame()

def search_krx(q):
    results=[]
    for sname,(code,mkt) in _POPULAR_KRX.items():
        if q in sname or sname.startswith(q):
            suffix=".KS" if mkt=="KOSPI" else ".KQ"
            results.append({"display":f"{sname} ({code}) · 🇰🇷 {mkt}",
                             "name":sname,"ticker":f"{code}{suffix}","market":"KRX"})
    if not results and q.isdigit() and len(q)==6:
        for s,l in [(".KS","KOSPI"),(".KQ","KOSDAQ")]:
            results.append({"display":f"{q} ({l}) · 🇰🇷 한국","name":q,
                             "ticker":f"{q}{s}","market":"KRX"})
    if not results:
        krx=_load_krx_via_pykrx()
        if not krx.empty:
            for code,row in krx[krx["name"].str.contains(q,case=False,na=False)].head(8).iterrows():
                mkt=row.get("_market","KOSPI"); s=".KS" if mkt=="KOSPI" else ".KQ"
                results.append({"display":f"{row['name']} ({code}) · 🇰🇷 {mkt}",
                                 "name":row["name"],"ticker":f"{code}{s}","market":"KRX"})
    return results[:8]

def search_stocks(query, market_choice):
    import yfinance as yf
    q=query.strip(); korean=_has_korean(q); results=[]

    # 한글 → 미국 주식 매핑 확인
    us_from_ko = None
    if korean:
        for ko,(ticker,en_name) in _KO_US_MAP.items():
            if q in ko or ko in q or q==ko:
                us_from_ko = (ticker, en_name); break

    # KRX 검색: 한글이고 미국 매핑이 없는 경우, 또는 숫자 6자리
    if market_choice in ["자동 감지","한국 (KRX)"]:
        if (korean and not us_from_ko) or (q.isdigit() and len(q)==6):
            results += search_krx(q)

    # 미국 주식 검색: 영문 입력 또는 한글 미국주식명 또는 미국 선택
    search_q = us_from_ko[0] if us_from_ko else q
    if not korean or us_from_ko or market_choice == "미국 (NYSE/NASDAQ)":
        # 한글 미국주식 매핑인 경우 바로 결과 추가
        if us_from_ko and market_choice != "한국 (KRX)":
            ticker, en_name = us_from_ko
            results.append({"display":f"{en_name} ({ticker}) · 🇺🇸 미국",
                            "name":en_name,"ticker":ticker,"market":"US"})
        try:
            for item in yf.Search(search_q,max_results=12,news_count=0).quotes:
                if item.get("quoteType")!="EQUITY": continue
                sym=item.get("symbol",""); name=item.get("longname") or item.get("shortname") or sym
                is_kr=sym.endswith(".KS") or sym.endswith(".KQ")
                if market_choice=="한국 (KRX)" and not is_kr: continue
                if market_choice=="미국 (NYSE/NASDAQ)" and is_kr: continue
                if any(r["ticker"]==sym for r in results): continue
                mkt="KRX" if is_kr else "US"; lbl="🇰🇷 한국" if is_kr else "🇺🇸 미국"
                results.append({"display":f"{name} ({sym}) · {lbl}","name":name,"ticker":sym,"market":mkt})
        except Exception: pass
    return results

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock(ticker, days):
    import yfinance as yf
    end=datetime.today(); start=end-timedelta(days=days+60)
    raw=yf.download(ticker,start=start,end=end,progress=False)
    if raw is None or raw.empty: return None
    df=_clean_yf(raw); return df[df.index>=pd.Timestamp(end-timedelta(days=days))]

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_indices(days, names):
    import yfinance as yf
    tmap={"SP500":"^GSPC","NASDAQ":"^IXIC","KOSPI":"^KS11","DJI":"^DJI"}
    end=datetime.today(); start=end-timedelta(days=days+60); out={}
    for name in names:
        yt=tmap.get(name)
        if not yt: continue
        try:
            raw=yf.download(yt,start=start,end=end,progress=False)
            if raw is not None and not raw.empty:
                df=_clean_yf(raw); out[name]=df["Close"]
        except Exception: pass
    return out

# ─────────────────────────────────────────────────────────────────
# 예측 모델 (순수 numpy)
# ─────────────────────────────────────────────────────────────────
def _biz_days(last_ts, n):
    dates=[]; offset=1
    while len(dates)<n:
        c=last_ts+pd.Timedelta(days=offset)
        if c.weekday()<5: dates.append(c)
        offset+=1
    return dates

def run_forecast(df, forecast_days=7):
    arr=df["Close"].dropna().astype(float).values; n=len(arr)
    last_ts=pd.Timestamp(_to_naive(df.index)[-1])
    if n<10: raise ValueError("데이터 부족")
    x=np.arange(n,dtype=float)
    slope,intercept=np.polyfit(x,arr,1)
    trend=slope*x+intercept; detrended=arr-trend
    period=5
    season=np.array([detrended[np.arange(p,n,period)].mean() for p in range(period)])
    season-=season.mean()
    season_c=np.array([season[i%period] for i in range(n)])
    resid=detrended-season_c; alpha=0.3
    ewma=np.empty(n); ewma[0]=resid[0]
    for i in range(1,n): ewma[i]=alpha*resid[i]+(1-alpha)*ewma[i-1]
    last_e=ewma[-1]
    fdates=_biz_days(last_ts,forecast_days)
    fc=np.array([slope*(n+i)+intercept+season[int(n+i)%period]+last_e*(1-alpha)**(i+1)
                 for i in range(forecast_days)])
    dv=(np.diff(arr[-60:])/arr[-60:-1]).std() if n>=61 else (np.diff(arr)/arr[:-1]).std()
    ci=fc*dv*np.sqrt(np.arange(1,forecast_days+1))*1.96
    future_fc=pd.DataFrame({"ds":fdates,"yhat":fc,"yhat_lower":fc-ci,"yhat_upper":fc+ci})
    hfit=trend+season_c+ewma; hstd=float(np.std(arr-hfit))
    hist_fc=pd.DataFrame({"ds":list(_to_naive(df.index)),"yhat":hfit.tolist(),
                           "yhat_lower":(hfit-1.96*hstd).tolist(),"yhat_upper":(hfit+1.96*hstd).tolist()})
    forecast=pd.concat([hist_fc,future_fc],ignore_index=True)
    return forecast,future_fc,"EWMA 추세·계절성 모델"

def calc_correlations(df,idx_data):
    ret=df["Close"].pct_change().dropna(); out={}
    for name,series in idx_data.items():
        ir=series.pct_change().dropna(); common=ret.index.intersection(ir.index)
        if len(common)>20: out[name]=round(ret[common].corr(ir[common]),3)
    return out

# ─────────────────────────────────────────────────────────────────
# 뉴스 감성 분석
# ─────────────────────────────────────────────────────────────────
_POS_KW = [
    "beat","record","growth","profit","upgrade","buy","strong","exceed",
    "gain","rise","jump","rally","bullish","outperform","raise","increase",
    "surge","high","positive","revenue","expansion","acquisition","launch",
    "partnership","dividend","buyback","recovery","breakout","milestone",
]
_NEG_KW = [
    "miss","decline","loss","downgrade","sell","weak","below","cut",
    "fall","drop","plunge","bearish","underperform","reduce","decrease",
    "slump","negative","concern","risk","lawsuit","investigation","debt",
    "default","bankruptcy","recall","fraud","fine","penalty","layoff",
]

def _kw_score(text):
    t = text.lower()
    p = sum(1 for w in _POS_KW if w in t)
    n = sum(1 for w in _NEG_KW if w in t)
    return (p - n) / (p + n) if (p + n) > 0 else 0.0

@st.cache_data(ttl=900, show_spinner=False)
def fetch_news(ticker):
    import yfinance as yf
    try:
        raw_news = yf.Ticker(ticker).news or []
        results = []
        for item in raw_news[:15]:
            # yfinance 버전별로 구조가 다름 — 안전하게 추출
            content = item.get("content") or item
            title = content.get("title","") if isinstance(content,dict) else item.get("title","")
            if not title:
                continue
            summary  = (content.get("summary","") or "") if isinstance(content,dict) else ""
            provider = ""
            if isinstance(content,dict):
                pub = content.get("provider") or content.get("publisher") or {}
                provider = pub.get("displayName","") if isinstance(pub,dict) else str(pub)
            ts = 0
            if isinstance(content,dict):
                ts = content.get("pubDate") or content.get("providerPublishTime") or 0
            if isinstance(ts, str):
                try: ts = int(pd.Timestamp(ts).timestamp())
                except: ts = 0
            link = (content.get("canonicalUrl",{}) or {}).get("url","") if isinstance(content,dict) else item.get("link","")
            score = _kw_score(title + " " + summary)
            results.append({
                "title": title, "provider": provider,
                "time": datetime.fromtimestamp(int(ts)).strftime("%m-%d %H:%M") if ts else "",
                "score": score, "link": link,
            })
        return results
    except Exception:
        return []

IDX_LABELS={"SP500":"S&P 500","NASDAQ":"NASDAQ","KOSPI":"KOSPI","DJI":"Dow Jones"}
IDX_COLORS={"SP500":"#E74C3C","NASDAQ":"#27AE60","KOSPI":"#F39C12","DJI":"#8E44AD"}
WEEKDAY_KO={0:"월",1:"화",2:"수",3:"목",4:"금"}

# ═════════════════════════════════════════════════════════════════
# PAGE 1: 주가 분석
# ═════════════════════════════════════════════════════════════════
if page == "📈 주가 분석":
    st.title("📈 AI 주식 예측 분석기")
    st.markdown("기업명 또는 티커를 입력하면 과거 주가 현황과 **향후 1주일 일단위 예측 그래프**를 제공합니다.")

    company_input=st.text_input("기업명 또는 티커 입력",
        placeholder="예: 삼성전자, 005930, Apple, TSLA …",label_visibility="collapsed")

    if company_input:
        idx_list=(["SP500"] if show_sp500 else [])+(["NASDAQ"] if show_nasdaq else [])+\
                 (["KOSPI"] if show_kospi else [])+(["DJI"] if show_dji else [])
        with st.spinner("🔍 기업 검색 중…"):
            results=search_stocks(company_input,market_choice)

        if not results:
            st.warning("검색 결과 없음\n\n"
                "- 🇰🇷 한국: `삼성전자` 또는 `005930`\n- 🇺🇸 미국: `Apple` 또는 `AAPL`")
            st.stop()

        labels=[r["display"] for r in results]
        sel_lbl=st.selectbox("📋 종목 선택",labels)
        selected=results[labels.index(sel_lbl)]

        # 종목이 바뀌면 이전 분석 결과 초기화
        if st.session_state.get("_last_ticker") != selected["ticker"]:
            st.session_state.pop("_analysis", None)
            st.session_state.pop("last_saved_id", None)

        if st.button("📊 분석 시작",type="primary",use_container_width=True):
            ticker=selected["ticker"]; market=selected["market"]; name=selected["name"]
            prog=st.progress(0,"주가 데이터 수집 중…")
            df=fetch_stock(ticker,history_period); prog.progress(35,"주가 완료…")
            if df is None or df.empty:
                st.error(f"❌ 데이터 없음 (티커: {ticker})"); prog.empty(); st.stop()
            idx_data=fetch_indices(history_period,idx_list); prog.progress(65,"지수 완료…")
            prog.progress(75,"뉴스 수집 중…")
            news_list = fetch_news(ticker)
            prog.progress(85,"AI 예측 모델 실행 중…")
            try:
                forecast,future_fc,model_name=run_forecast(df,forecast_days=7)
                prog.progress(100,"완료!"); prog.empty()
                # 뉴스 감성 점수 계산
                sent_score = float(np.mean([n["score"] for n in news_list])) if news_list else 0.0
                # 분석 결과 전체를 세션에 저장 → 저장 버튼 클릭 후 재실행 시에도 유지됨
                st.session_state["_analysis"]={
                    "ticker":ticker,"name":name,"market":market,
                    "df":df,"idx_data":idx_data,
                    "forecast":forecast,"future_fc":future_fc,"model_name":model_name,
                    "latest":float(df["Close"].iloc[-1]),
                    "news":news_list,"sent_score":sent_score,
                }
                st.session_state["_last_ticker"]=ticker
                st.session_state.pop("last_saved_id",None)
            except Exception as e:
                import traceback; prog.empty()
                st.error(f"❌ 예측 오류: {e}")
                with st.expander("🔍 상세 오류"): st.code(traceback.format_exc())

        # ── 분석 결과 표시 (버튼 조건 밖 — 저장 버튼 클릭 후 재실행 시에도 유지)
        if "_analysis" in st.session_state:
            an=st.session_state["_analysis"]
            ticker=an["ticker"]; name=an["name"]; market=an["market"]
            df=an["df"]; idx_data=an["idx_data"]
            forecast=an["forecast"]; model_name=an["model_name"]; latest=an["latest"]
            news_list=an.get("news",[]); sent_score=an.get("sent_score",0.0)
            # 감성 점수로 예측값 보정 (최대 ±3%)
            sent_adj = 1.0 + sent_score * 0.03
            future_fc = an["future_fc"].copy()
            future_fc["yhat"]       *= sent_adj
            future_fc["yhat_lower"] *= sent_adj
            future_fc["yhat_upper"] *= sent_adj

            # ── Metrics
            prev=float(df["Close"].iloc[-2]) if len(df)>1 else latest
            chg=latest-prev; chg_pct=chg/prev*100 if prev else 0
            st.divider(); st.subheader(f"📌 {name}  ({ticker})")
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("현재가",f"{latest:,.2f}",f"{chg:+,.2f} ({chg_pct:+.2f}%)")
            c2.metric("최고가",f"{df['Close'].max():,.2f}")
            c3.metric("최저가",f"{df['Close'].min():,.2f}")
            c4.metric("평균 거래량",f"{df['Volume'].mean():,.0f}" if "Volume" in df.columns and df["Volume"].sum()>0 else "N/A")
            if len(df)>=20:
                ma20=float(df["Close"].rolling(20).mean().iloc[-1])
                c5.metric("MA20 대비","상승 추세" if latest>ma20 else "하락 추세",f"{(latest/ma20-1)*100:+.1f}%")

            # ── Historical Chart
            st.subheader("📉 과거 주가 차트")
            has_ohlc=all(c in df.columns for c in ["Open","High","Low","Close"])
            has_vol="Volume" in df.columns and df["Volume"].sum()>0
            fig1=make_subplots(rows=2 if has_vol else 1,cols=1,shared_xaxes=True,
                               vertical_spacing=0.04,row_heights=[0.65,0.35] if has_vol else [1.0])
            if has_ohlc:
                fig1.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],
                    low=df["Low"],close=df["Close"],name="OHLC",
                    increasing_line_color="#FF4444",decreasing_line_color="#0066CC"),row=1,col=1)
                for w,color,dash in [(5,"orange","solid"),(20,"purple","dash"),(60,"gray","dot")]:
                    if len(df)>=w:
                        fig1.add_trace(go.Scatter(x=df.index,y=df["Close"].rolling(w).mean(),
                            name=f"MA{w}",line=dict(color=color,width=1,dash=dash)),row=1,col=1)
            else:
                fig1.add_trace(go.Scatter(x=df.index,y=df["Close"],name="종가",
                    line=dict(color="royalblue",width=2)),row=1,col=1)
            if has_vol:
                vc=["#FF4444" if has_ohlc and df["Close"].iloc[i]>=df["Open"].iloc[i] else "#0066CC"
                    for i in range(len(df))]
                fig1.add_trace(go.Bar(x=df.index,y=df["Volume"],name="거래량",
                    marker_color=vc,opacity=0.7),row=2,col=1)
            fig1.update_layout(height=480 if has_vol else 350,xaxis_rangeslider_visible=False,
                               hovermode="x unified",
                               legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
            st.plotly_chart(fig1,use_container_width=True)

            # ── Global Comparison
            if idx_data:
                st.subheader("🌏 글로벌 시장 지수 비교 (정규화)")
                fig2=go.Figure()
                sn=df["Close"]/df["Close"].iloc[0]*100
                fig2.add_trace(go.Scatter(x=sn.index,y=sn,name=f"📊 {name}",
                    line=dict(color="royalblue",width=2.5)))
                for iname,series in idx_data.items():
                    al=series[series.index>=df.index[0]]
                    if not al.empty:
                        nm=al/al.iloc[0]*100
                        fig2.add_trace(go.Scatter(x=nm.index,y=nm,name=IDX_LABELS.get(iname,iname),
                            line=dict(color=IDX_COLORS.get(iname,"gray"),width=1.5,dash="dash"),opacity=0.85))
                fig2.add_hline(y=100,line_dash="dot",line_color="gray",opacity=0.4)
                fig2.update_layout(title="글로벌 지수 대비 성과 (시작점=100)",
                                   yaxis_title="상대 수익률(%)",height=380,hovermode="x unified",
                                   legend=dict(orientation="h",yanchor="bottom",y=1.02))
                st.plotly_chart(fig2,use_container_width=True)

                corr=calc_correlations(df,idx_data)
                if corr:
                    st.subheader("📐 글로벌 지수 상관계수")
                    ccols=st.columns(len(corr))
                    for i,(iname,val) in enumerate(corr.items()):
                        desc=("강한 양의 상관" if val>0.7 else "보통 양의 상관" if val>0.4
                              else "약한 상관" if val>0.1 else "음의 상관/무상관")
                        ccols[i].metric(IDX_LABELS.get(iname,iname),f"{val:.3f}",desc)

            # ── Prediction Chart
            st.subheader("🔮 향후 1주일 주가 예측 (AI)")
            hist_end=pd.Timestamp(_to_naive(df.index)[-1])
            show_from=hist_end-timedelta(days=60)
            df_recent=df[df.index>=show_from]
            fc_hist=forecast[(forecast["ds"]>=show_from)&(forecast["ds"]<=hist_end)]

            fig3=go.Figure()
            fig3.add_trace(go.Scatter(x=df_recent.index,y=df_recent["Close"],
                name="실제 주가",line=dict(color="royalblue",width=2)))
            fig3.add_trace(go.Scatter(x=fc_hist["ds"],y=fc_hist["yhat"],
                name="모델 적합값",line=dict(color="orange",width=1.5,dash="dot"),opacity=0.7))
            fig3.add_trace(go.Scatter(
                x=pd.concat([future_fc["ds"],future_fc["ds"][::-1]]),
                y=pd.concat([future_fc["yhat_upper"],future_fc["yhat_lower"][::-1]]),
                fill="toself",fillcolor="rgba(231,76,60,0.15)",
                line=dict(color="rgba(255,255,255,0)"),name="95% 예측 구간"))
            fig3.add_trace(go.Scatter(x=future_fc["ds"],y=future_fc["yhat"],
                name="예측 주가",mode="lines+markers",
                line=dict(color="#E74C3C",width=2.5),marker=dict(size=9)))
            fig3.add_vline(x=hist_end.strftime("%Y-%m-%d"),line_dash="dash",
                           line_color="gray",opacity=0.6)
            fig3.update_layout(title=f"{name} — 향후 7영업일 예측 ({model_name})",
                yaxis_title="주가",height=460,hovermode="x unified",
                legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig3,use_container_width=True)

            # ── Table
            st.subheader("📅 일별 예측 결과")
            rows=[]; prev_val=latest
            for _,row in future_fc.iterrows():
                day=row["ds"]; yhat=row["yhat"]
                d_chg=(yhat-prev_val)/prev_val*100 if prev_val else 0
                rows.append({"날짜":f"{day.strftime('%Y-%m-%d')} ({WEEKDAY_KO.get(day.weekday(),'')})",
                             "예측 주가":f"{yhat:,.2f}","하한(95%)":f"{row['yhat_lower']:,.2f}",
                             "상한(95%)":f"{row['yhat_upper']:,.2f}","전일 대비":f"{d_chg:+.2f}%"})
                prev_val=yhat
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

            total_chg=(float(future_fc["yhat"].iloc[-1])-latest)/latest*100
            direction="상승" if total_chg>0 else "하락"
            # 감성 조정 표시 텍스트
            if abs(sent_score) > 0.05 and news_list:
                adj_pct = (sent_adj - 1) * 100
                adj_tag = f"  \n📰 뉴스 감성 반영: {'긍정' if sent_score>0 else '부정'} ({adj_pct:+.1f}%)"
            else:
                adj_tag = ""
            st.info(f"**예측 요약**: 향후 7영업일 **{abs(total_chg):.1f}%** {direction} 예상  \n"
                    f"최고 **{future_fc['yhat'].max():,.2f}** · 최저 **{future_fc['yhat'].min():,.2f}**"
                    + adj_tag)

            # ── 뉴스 & 감성 분석
            st.subheader("📰 최신 뉴스 & 시장 심리")
            if news_list:
                # 감성 게이지
                if sent_score > 0.2:
                    mood_label, mood_color = "긍정적 😊", "#27AE60"
                elif sent_score < -0.2:
                    mood_label, mood_color = "부정적 😟", "#E74C3C"
                else:
                    mood_label, mood_color = "중립 😐", "#F39C12"
                pct = int((sent_score + 1) / 2 * 100)
                st.markdown(
                    f"**전체 시장 심리**: "
                    f"<span style='color:{mood_color};font-weight:bold'>{mood_label}</span> "
                    f"(점수: {sent_score:+.2f}) &nbsp;→&nbsp; 예측값 **{(sent_adj-1)*100:+.1f}%** 조정 적용",
                    unsafe_allow_html=True
                )
                st.progress(pct, text=f"부정 ←{'─'*int(pct/5)}● {'─'*(20-int(pct/5))}→ 긍정")

                st.divider()
                for n in news_list:
                    icon = "📈" if n["score"] > 0.1 else ("📉" if n["score"] < -0.1 else "➖")
                    time_str = f"`{n['time']}`  " if n["time"] else ""
                    pub_str  = f"*{n['provider']}*" if n["provider"] else ""
                    if n.get("link"):
                        title_md = f"[{n['title']}]({n['link']})"
                    else:
                        title_md = n["title"]
                    st.markdown(f"{icon} {time_str}{pub_str}  \n&nbsp;&nbsp;&nbsp;&nbsp;{title_md}")
            else:
                st.info("이 종목의 뉴스를 찾을 수 없습니다. (한국 주식은 뉴스가 제한될 수 있습니다)")

            # ── 예측 저장 버튼 (버튼 조건 밖에 위치 → 클릭 시 정상 실행됨)
            st.divider()
            col_save, col_msg = st.columns([1, 3])
            with col_save:
                if st.button("📌 이 예측 저장하기", use_container_width=True):
                    pid = save_prediction(ticker, name, latest, future_fc, model_name)
                    st.session_state["last_saved_id"] = pid
            with col_msg:
                if st.session_state.get("last_saved_id"):
                    st.success(f"✅ 예측이 저장됐습니다! (ID: {st.session_state['last_saved_id']})  \n"
                               "왼쪽 메뉴 **🎯 예측 검증** 에서 나중에 결과를 확인하세요.")

        st.divider()
        st.caption("⚠️ 본 예측은 통계 모델 기반 참고 정보입니다. 투자 결정 시 전문가 조언을 병행하시기 바랍니다.")

    else:
        st.info("위 검색창에 기업명 또는 티커를 입력하세요.")
        c1,c2,c3=st.columns(3)
        c1.markdown("**🇰🇷 한국 주식**\n- `삼성전자`\n- `SK하이닉스`\n- `카카오`")
        c2.markdown("**🇺🇸 미국 주식**\n- `Apple`\n- `TSLA`\n- `NVDA`")
        c3.markdown("**📊 기능**\n- 캔들 차트 + MA\n- 글로벌 지수 비교\n- 7일 AI 예측 + 저장")

# ═════════════════════════════════════════════════════════════════
# PAGE 2: 예측 검증
# ═════════════════════════════════════════════════════════════════
elif page == "🎯 예측 검증":
    st.title("🎯 예측 검증")

    preds = load_predictions()
    if not preds:
        st.info("저장된 예측이 없습니다.\n\n"
                "**📈 주가 분석** 페이지에서 예측 실행 후 **📌 이 예측 저장하기** 버튼을 누르세요.")
        st.stop()

    preds_sorted = sorted(preds, key=lambda x: x["saved_at"], reverse=True)
    sel_idx = min(st.session_state.get("_pred_sel_idx", 0), len(preds_sorted) - 1)
    pred = preds_sorted[sel_idx]

    # ── 헤더: 선택된 예측 정보 + 삭제
    st.subheader(f"📌 {pred['company']} ({pred['ticker']})")
    col_info, col_del = st.columns([4, 1])
    with col_info:
        dates = [f["date"] for f in pred["forecasts"]]
        st.markdown(f"저장일시: **{pred['saved_at']}** | 모델: `{pred['model']}` | "
                    f"기준가: **{pred['base_price']:,.2f}** | "
                    f"예측 기간: {min(dates)} ~ {max(dates)}")
    with col_del:
        if st.button("🗑️ 삭제", use_container_width=True, type="secondary"):
            delete_prediction(pred["id"])
            st.session_state["_pred_sel_idx"] = 0
            st.rerun()

    # ── 실제 주가 조회
    forecasts = pred["forecasts"]
    today_str = datetime.today().strftime("%Y-%m-%d")
    past_fc   = [f for f in forecasts if f["date"] <= today_str]
    future_fc_list = [f for f in forecasts if f["date"] > today_str]

    if not past_fc:
        st.info(f"예측 시작일({forecasts[0]['date']})이 아직 도래하지 않았습니다.")
        st.subheader("📅 예측 내역 (검증 대기)")
        rows = []
        for f in forecasts:
            rows.append({"날짜": f["date"], "예측 주가": f"{f['predicted']:,.2f}",
                         "하한(95%)": f"{f['lower']:,.2f}", "상한(95%)": f"{f['upper']:,.2f}",
                         "상태": "⏳ 대기"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.stop()

    # ── 실제 가격 조회
    import yfinance as yf
    with st.spinner("실제 주가 데이터 조회 중…"):
        try:
            start_dt = pd.Timestamp(forecasts[0]["date"]) - pd.Timedelta(days=5)
            end_dt   = pd.Timestamp(today_str) + pd.Timedelta(days=2)
            raw = yf.download(pred["ticker"], start=start_dt, end=end_dt, progress=False)
            actual_df = _clean_yf(raw) if (raw is not None and not raw.empty) else pd.DataFrame()
        except Exception:
            actual_df = pd.DataFrame()

    def get_actual(date_str):
        if actual_df.empty: return None
        ts = pd.Timestamp(date_str)
        if ts in actual_df.index:
            return float(actual_df.loc[ts, "Close"])
        nearby = actual_df.index[actual_df.index <= ts]
        if len(nearby) == 0: return None
        return float(actual_df.loc[nearby[-1], "Close"])

    # ── 검증 테이블
    st.subheader("📊 예측 vs 실제 비교")
    rows = []
    correct_dir = 0; total_dir = 0
    mape_vals = []; mae_vals = []
    base = pred["base_price"]

    for f in forecasts:
        actual = get_actual(f["date"])
        status = "⏳ 대기" if f["date"] > today_str else ("✅ 완료" if actual else "📭 데이터 없음")
        row = {
            "날짜": f["date"],
            "예측 주가": f"{f['predicted']:,.2f}",
            "하한(95%)": f"{f['lower']:,.2f}",
            "상한(95%)": f"{f['upper']:,.2f}",
            "실제 주가": f"{actual:,.2f}" if actual else "-",
            "오차": f"{actual - f['predicted']:+,.2f}" if actual else "-",
            "오차율": f"{(actual - f['predicted']) / f['predicted'] * 100:+.2f}%" if actual else "-",
            "범위 내": ("✅" if actual and f["lower"] <= actual <= f["upper"] else "❌") if actual else "-",
            "상태": status,
        }
        rows.append(row)

        if actual:
            err_pct = abs((actual - f["predicted"]) / f["predicted"]) * 100
            mape_vals.append(err_pct)
            mae_vals.append(abs(actual - f["predicted"]))
            pred_dir = f["predicted"] > base
            act_dir  = actual > base
            if pred_dir == act_dir: correct_dir += 1
            total_dir += 1

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── 정확도 지표
    if mape_vals:
        st.subheader("🏆 예측 정확도 지표")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("평균 오차율 (MAPE)", f"{np.mean(mape_vals):.2f}%",
                  "낮을수록 정확")
        m2.metric("평균 절대 오차 (MAE)", f"{np.mean(mae_vals):,.2f}",
                  "낮을수록 정확")
        dir_acc = correct_dir / total_dir * 100 if total_dir > 0 else 0
        m3.metric("방향 정확도", f"{dir_acc:.0f}%",
                  f"{correct_dir}/{total_dir}일 맞춤")
        in_range = sum(1 for r in rows if r["범위 내"] == "✅")
        m4.metric("95% 구간 내 실제값", f"{in_range}/{len(mape_vals)}일",
                  "신뢰구간 포함률")

    # ── 비교 차트
    if not actual_df.empty:
        st.subheader("📈 예측 vs 실제 주가 차트")
        fig_v = go.Figure()

        # 실제 주가 (예측 기간 전후 포함)
        chart_start = pd.Timestamp(forecasts[0]["date"]) - pd.Timedelta(days=10)
        actual_range = actual_df[actual_df.index >= chart_start]
        if not actual_range.empty:
            fig_v.add_trace(go.Scatter(x=actual_range.index, y=actual_range["Close"],
                name="실제 주가", line=dict(color="royalblue", width=2)))

        # 기준가 수평선
        fig_v.add_hline(y=pred["base_price"], line_dash="dot",
                        line_color="gray", opacity=0.5,
                        annotation_text=f"기준가 {pred['base_price']:,.0f}")

        # 예측값 (점)
        pred_dates = [f["date"] for f in forecasts]
        pred_vals  = [f["predicted"] for f in forecasts]
        lower_vals = [f["lower"] for f in forecasts]
        upper_vals = [f["upper"] for f in forecasts]

        # 신뢰구간
        fig_v.add_trace(go.Scatter(
            x=pred_dates + pred_dates[::-1],
            y=upper_vals + lower_vals[::-1],
            fill="toself", fillcolor="rgba(231,76,60,0.1)",
            line=dict(color="rgba(255,255,255,0)"), name="95% 예측 구간"))

        fig_v.add_trace(go.Scatter(x=pred_dates, y=pred_vals,
            name="예측 주가", mode="lines+markers",
            line=dict(color="#E74C3C", width=2, dash="dash"),
            marker=dict(size=8, symbol="circle")))

        # 실제 주가 (예측일 포인트)
        actual_points_x, actual_points_y = [], []
        for f in forecasts:
            a = get_actual(f["date"])
            if a:
                actual_points_x.append(f["date"])
                actual_points_y.append(a)
        if actual_points_x:
            fig_v.add_trace(go.Scatter(x=actual_points_x, y=actual_points_y,
                name="실제값 (예측일)", mode="markers",
                marker=dict(size=10, color="#27AE60", symbol="diamond")))

        fig_v.update_layout(
            title=f"{pred['company']} — 예측 검증 차트",
            yaxis_title="주가", height=430, hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_v, use_container_width=True)

    if future_fc_list:
        remaining = len(future_fc_list)
        st.info(f"⏳ 아직 {remaining}일치 예측이 남아있습니다 "
                f"(마지막: {future_fc_list[-1]['date']}). 해당 날짜 이후에 다시 확인하세요.")

    st.divider()
    st.caption("⚠️ 실제 주가는 yfinance에서 조회됩니다. 조회 시점에 따라 데이터가 없을 수 있습니다.")
