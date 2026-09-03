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

# ------------------------------------------------------------
# 3. 총 관객 히스토그램
# ------------------------------------------------------------
st.header("3. 총 관객 분포 (히스토그램)")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
)
fig_hist.update_traces(
    hovertemplate="관객 구간: %{x}<br>편수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 관객이 몰린 구간과, 관객이 가장 많은 영화 계산
hist_counts, hist_edges = pd.cut(df["total_audi"], bins=30, retbins=True)
mode_bin = hist_counts.value_counts().idxmax()
top_movie_row = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"**🔍 이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객 "
    f"**{int(mode_bin.left):,}명 ~ {int(mode_bin.right):,}명** 구간에 몰려 있고, "
    f"총 관객이 가장 많은 영화는 **'{top_movie_row['movieNm']}'** "
    f"(총 관객 {int(top_movie_row['total_audi']):,}명)입니다."
)

st.divider()

# ------------------------------------------------------------
# 4. 개봉일 스크린수 vs 총 관객 - 산점도
# ------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계 (산점도)")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 5. 장르별 총 관객 - 박스플롯 (10편 이상 장르만)
# ------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (박스플롯)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major_genre = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major_genre,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_data={"movieNm": True},
)
fig_box.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르 (영화 10편 이상)",
    yaxis_title="총 관객 수",
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 6. 개봉일 스크린수 vs 총 관객 - 버블 그래프 (크기: 첫 주 관객)
# ------------------------------------------------------------
st.header("6. 개봉일 스크린수와 총 관객의 관계 (버블 그래프)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 7. 제작 국가 → 장르 - 선버스트 그래프
# ------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성 (선버스트)")

nation_genre_counts = (
    df.groupby(["nation", "genre"]).size().reset_index(name="count")
)

fig_sunburst = px.sunburst(
    nation_genre_counts,
    path=["nation", "genre"],
    values="count",
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>",
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 8. 장르 top3 - 막대 그래프 (영화명, 총 관객 포함)
# ------------------------------------------------------------
st.header("8. 영화 편수 상위 3개 장르의 영화별 총 관객 (막대 그래프)")

top3_genres = df["genre"].value_counts().head(3).index.tolist()
df_top3_genre = df[df["genre"].isin(top3_genres)].sort_values(
    ["genre", "total_audi"], ascending=[True, False]
)

fig_bar_top3 = px.bar(
    df_top3_genre,
    x="movieNm",
    y="total_audi",
    color="genre",
)
fig_bar_top3.update_traces(
    hovertemplate="영화명: %{x}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_bar_top3.update_layout(
    xaxis_title="영화명",
    yaxis_title="총 관객 수",
    xaxis={"categoryorder": "total descending"},
)

st.plotly_chart(fig_bar_top3, use_container_width=True)

st.markdown("**🔍 이 그래프로 알 수 있는 것:** ")

st.divider()
