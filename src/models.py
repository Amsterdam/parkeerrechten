
from sqlalchemy import Column, Numeric, String, Unicode, SmallInteger, Integer
from sqlalchemy.orm import declarative_base

import settings

Base = declarative_base()


class NPRTable(Base):
    __tablename__ = settings.NPR_DB_TABLE_NAME

    VERW_RECHT_ID = Column(Numeric(10, 0), nullable=False, primary_key=True)
    LAND_C_V_RECHT = Column(String(3))
    VERK_P_V_RECHT = Column(Numeric(10, 0))
    VERK_PUNT_OMS = Column(Unicode(80))
    B_TYD_V_RECHT = Column(String(14))
    E_TYD_V_RECHT = Column(String(14))
    E_TYD_R_AANP = Column(String(14))
    BEDRAG_V_RECHT = Column(Numeric(10, 2))
    BTW_V_RECHT = Column(Numeric(10, 2))
    BEDR_V_RECHT_B = Column(Numeric(10, 2))
    BTW_V_RECHT_BER = Column(Numeric(10, 2))
    BEDR_V_RECHT_H = Column(Numeric(10, 2))
    BTW_V_RECHT_HER = Column(Numeric(10, 2))
    TYD_HERBEREK = Column(String(14))
    RECHTV_V_RECHT = Column(String(10))
    RECHTV_INT_OMS = Column(Unicode(80))
    GEB_BEH_V_RECHT = Column(SmallInteger())
    GEBIEDS_BEH_OMS = Column(Unicode(80))
    GEB_C_V_RECHT = Column(String(10))
    GEBIED_OMS = Column(Unicode(80))
    REG_TYD_V_RECHT = Column(String(14))
    COORD_V_RECHT = Column(Unicode(30))
    GEBR_DOEL_RECHT = Column(String(10))
    GEBR_DOEL_OMS = Column(Unicode(80))
    R_TYD_E_TYD_VR = Column(String(14))
    VER_BATCH_ID = Column(Integer())
    VER_BATCH_NAAM = Column(String(12), index=True)
    KENM_RECHTV_INT = Column(Unicode(40))
