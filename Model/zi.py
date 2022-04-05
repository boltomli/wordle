from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class Zi(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(...)
    stroke_count: int = Field(...)
    strokes: str = Field(...)
    heng_count: int = Field(...)
    shu_count: int = Field(...)
    pie_count: int = Field(...)
    dian_count: int = Field(...)
    zhe_count: int = Field(...)


engine = create_engine('sqlite:///Data/strokes.db', connect_args={'check_same_thread': False})
SQLModel.metadata.create_all(engine)
session = Session(engine)
