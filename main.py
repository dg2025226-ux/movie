import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 **216편**의 데이터를 살펴봅니다.
"""
)


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # genre 열에 세로막대(|)로 여러 장르가 적혀 있으면 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # openDt(개봉일, 8자리 숫자)를 날짜형으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    return df


df = load_data()

with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="%{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(showlegend=True)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 2. 장르 안 영화별 총 관객 - 트리맵
# ------------------------------------------------------------
st.header("2. 장르별 영화의 총 관객 (트리맵)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=30, l=10, r=10, b=10))

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()
