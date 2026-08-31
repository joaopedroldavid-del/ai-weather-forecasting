import logging
from datetime import date, datetime, timezone

from supabase import Client

from app.config.supabase_client import get_supabase_client
from app.models.weather_reading import WeatherReading

logger = logging.getLogger(__name__)

TABLE_NAME = "bdmep_forecast"

COL_UF = "UF"
COL_CIDADE = "CIDADE"
COL_DATA = "Data"
COL_HORA_UTC = "Hora UTC"
COL_PRECIPITACAO = "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)"
COL_PRESSAO = "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
COL_PRESSAO_MAX = "PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)"
COL_PRESSAO_MIN = "PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)"
COL_RADIACAO = "RADIACAO GLOBAL (Kj/m²)"
COL_TEMPERATURA = "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)"
COL_ORVALHO = "TEMPERATURA DO PONTO DE ORVALHO (°C)"
COL_TEMPERATURA_MAX = "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)"
COL_TEMPERATURA_MIN = "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)"
COL_ORVALHO_MAX = "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)"
COL_ORVALHO_MIN = "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)"
COL_UMIDADE_MAX = "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)"
COL_UMIDADE_MIN = "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)"
COL_UMIDADE = "UMIDADE RELATIVA DO AR, HORARIA (%)"
COL_VENTO_DIRECAO = "VENTO, DIREÇÃO HORARIA (gr) (° (gr))"
COL_VENTO_RAJADA = "VENTO, RAJADA MAXIMA (m/s)"
COL_VENTO_VELOCIDADE = "VENTO, VELOCIDADE HORARIA (m/s)"


def _parse_float(raw: str | None) -> float | None:
    """Parse a raw bdmep_forecast text cell (Brazilian comma-decimal, e.g.
    "922,3" or ",8" meaning 0.8) into a float, or None when the cell is
    blank/missing/malformed."""
    if raw is None:
        return None

    stripped = raw.strip()
    if not stripped:
        return None

    try:
        return float(stripped.replace(",", "."))
    except ValueError:
        # Malformed source value (bad sensor read, corrupted export, etc.) -
        # treated as missing data rather than failing the whole row.
        logger.warning("Could not parse float value from bdmep_forecast: %r", raw)
        return None


def _parse_observed_at(data_raw: str, hora_raw: str) -> datetime:
    parsed_date = datetime.strptime(data_raw, "%Y/%m/%d")
    hour = int(hora_raw.split(" ")[0][:2])
    return parsed_date.replace(hour=hour, tzinfo=timezone.utc)


def _row_to_domain(row: dict) -> WeatherReading:
    return WeatherReading(
        uf=row[COL_UF],
        city=row[COL_CIDADE],
        observed_at=_parse_observed_at(row[COL_DATA], row[COL_HORA_UTC]),
        precipitation_mm=_parse_float(row.get(COL_PRECIPITACAO)),
        pressure_mb=_parse_float(row.get(COL_PRESSAO)),
        pressure_max_mb=_parse_float(row.get(COL_PRESSAO_MAX)),
        pressure_min_mb=_parse_float(row.get(COL_PRESSAO_MIN)),
        radiation_kj_m2=_parse_float(row.get(COL_RADIACAO)),
        temperature_c=_parse_float(row.get(COL_TEMPERATURA)),
        dew_point_c=_parse_float(row.get(COL_ORVALHO)),
        temperature_max_c=_parse_float(row.get(COL_TEMPERATURA_MAX)),
        temperature_min_c=_parse_float(row.get(COL_TEMPERATURA_MIN)),
        dew_point_max_c=_parse_float(row.get(COL_ORVALHO_MAX)),
        dew_point_min_c=_parse_float(row.get(COL_ORVALHO_MIN)),
        humidity_max_pct=_parse_float(row.get(COL_UMIDADE_MAX)),
        humidity_min_pct=_parse_float(row.get(COL_UMIDADE_MIN)),
        humidity_pct=_parse_float(row.get(COL_UMIDADE)),
        wind_direction_deg=_parse_float(row.get(COL_VENTO_DIRECAO)),
        wind_gust_ms=_parse_float(row.get(COL_VENTO_RAJADA)),
        wind_speed_ms=_parse_float(row.get(COL_VENTO_VELOCIDADE)),
    )


class WeatherReadingRepository:
    def __init__(self, client: Client | None = None):
        self._client = client or get_supabase_client()

    def find_by_city(self, city: str, start_date: date, end_date: date) -> list[WeatherReading]:
        response = (
            self._client.table(TABLE_NAME)
            .select("*")
            .eq(COL_CIDADE, city)
            .gte(COL_DATA, start_date.strftime("%Y/%m/%d"))
            .lte(COL_DATA, end_date.strftime("%Y/%m/%d"))
            .order(COL_DATA)
            .order(COL_HORA_UTC)
            .execute()
        )
        return [_row_to_domain(row) for row in response.data]

    def list_cities(self) -> list[str]:
        response = self._client.table(TABLE_NAME).select(COL_CIDADE).execute()
        cities = {row[COL_CIDADE] for row in response.data if row.get(COL_CIDADE)}
        return sorted(cities)

    def ping(self) -> None:
        """Cheapest possible round-trip to confirm the Supabase connection is
        alive. Raises whatever the client raises on failure - callers decide
        what an unreachable database means for them."""
        self._client.table(TABLE_NAME).select(COL_UF).limit(1).execute()
