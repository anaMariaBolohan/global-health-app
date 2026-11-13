from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Index, Numeric,
    SmallInteger, String, Text, UniqueConstraint, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Source(Base):
    __tablename__ = "source"

    source_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    url: Mapped[str | None] = mapped_column(Text)

    indicators: Mapped[list["Indicator"]] = relationship(back_populates="source")


class Country(Base):
    __tablename__ = "country"

    iso3: Mapped[str] = mapped_column(String(3), primary_key=True)
    iso2: Mapped[str | None] = mapped_column(String(2))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100))
    subregion: Mapped[str | None] = mapped_column(String(50))  # Task 1.8 Extension
    income_group: Mapped[str | None] = mapped_column(String(50))

    observations: Mapped[list["Observation"]] = relationship(back_populates="country")


class Indicator(Base):
    __tablename__ = "indicator"

    indicator_id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    category: Mapped[str | None] = mapped_column(String(50))     # Task 1.8 Extension
    description: Mapped[str | None] = mapped_column(Text)          # Task 1.8 Extension
    source_id: Mapped[int] = mapped_column(ForeignKey("source.source_id"), nullable=False)

    source: Mapped[Source] = relationship(back_populates="indicators")
    observations: Mapped[list["Observation"]] = relationship(back_populates="indicator")


class Observation(Base):
    __tablename__ = "observation"
    __table_args__ = (
        UniqueConstraint("country_iso3", "indicator_id", "year", "sex", name="uq_observation"),
        Index("ix_observation_indicator_year", "indicator_id", "year"),
    )

    observation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    country_iso3: Mapped[str] = mapped_column(ForeignKey("country.iso3"), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicator.indicator_id"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sex: Mapped[str] = mapped_column(String(10), server_default="BTSX", nullable=False)
    
    value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    value_low: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))   # Task 1.8 Extension (WHO bounds)
    value_high: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))  # Task 1.8 Extension (WHO bounds)
    
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    country: Mapped[Country] = relationship(back_populates="observations")
    indicator: Mapped[Indicator] = relationship(back_populates="observations")


class ImportLog(Base):
    __tablename__ = "import_log"

    import_id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    rows_loaded: Mapped[int] = mapped_column(nullable=False)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )