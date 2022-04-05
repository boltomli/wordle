import asyncio
import csv
import os.path

import aiofiles
import streamlit as st
from fastapi import HTTPException
from httpx import AsyncClient
from sqlmodel import select

from Model.zi import Zi, session

client = AsyncClient(timeout=10, follow_redirects=True)


STROKES = {
    1: '横',
    2: '竖',
    3: '撇',
    4: '捺/点',
    5: '折',
    0: 'unknown',
}


async def download(url: str, path: str) -> None:
    resp = await client.get(url)
    if resp.is_success:
        async with aiofiles.open(path, 'wb') as f:
            await f.write(resp.content)
    else:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)


@st.cache
def normalize_strokes(strokes: str):
    result = [0] * 6
    for stroke in strokes:
        if int(stroke) not in STROKES:
            result[0] += 1
        else:
            result[int(stroke)] += 1
    return result


def build_stroke_options():
    return [
        [s[0] for s in session.query(Zi.heng_count).distinct().order_by(Zi.heng_count).all()],
        [s[0] for s in session.query(Zi.shu_count).distinct().order_by(Zi.shu_count).all()],
        [s[0] for s in session.query(Zi.pie_count).distinct().order_by(Zi.pie_count).all()],
        [s[0] for s in session.query(Zi.dian_count).distinct().order_by(Zi.dian_count).all()],
        [s[0] for s in session.query(Zi.zhe_count).distinct().order_by(Zi.zhe_count).all()],
    ]


def exec_stroke_query(query):
    statement = select(Zi)
    if query[0] > 0:
        statement = statement.where(Zi.heng_count == query[0])
    if query[1] > 0:
        statement = statement.where(Zi.shu_count == query[1])
    if query[2] > 0:
        statement = statement.where(Zi.pie_count == query[2])
    if query[3] > 0:
        statement = statement.where(Zi.dian_count == query[3])
    if query[4] > 0:
        statement = statement.where(Zi.zhe_count == query[4])
    return [s.dict() for s in session.exec(statement).all()]


strokes_url = 'https://github.com/yindian/hzbishun/raw/master/res/13000.csv'
strokes_file = 'Data/strokes.data'

stroke_options = build_stroke_options()

if len(stroke_options[0]) == 0:
    try:
        if not os.path.exists(strokes_file):
            asyncio.run(download(strokes_url, strokes_file))
        with open(strokes_file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if '字' in row and '画数' in row and '笔画码' in row:
                    if row['字'] and row['画数'] and row['笔画码']:
                        zi = session.exec(select(Zi).where(Zi.name == row['字'])).first()
                        if not zi:
                            strokes = normalize_strokes(row['笔画码'])
                            session.add(Zi(
                                name=str(row['字']),
                                stroke_count=int(row['画数']),
                                strokes=str(row['笔画码']),
                                heng_count=strokes[1],
                                shu_count=strokes[2],
                                pie_count=strokes[3],
                                dian_count=strokes[4],
                                zhe_count=strokes[5],
                            ))
        session.commit()
    except Exception as e:
        st.warning(repr(e))


st.title('strokes')
st.subheader('info')
st.text(f'Strokes data from {strokes_url}')

stroke_cols = st.columns(len(STROKES))
stroke_query = [0, 0, 0, 0, 0]
for i in range(len(stroke_cols)):
    with stroke_cols[i]:
        if i > 0:
            stroke_query[i-1] = st.selectbox(STROKES[i], stroke_options[i-1])
result = exec_stroke_query(stroke_query)
st.table(result)
