import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.station import Station
from app.models.enums import SourceEnum,StationTypeEnum

ARQUIVO_JSON = Path("scripts/all_stations.json")

def populate_db():
    if not ARQUIVO_JSON.exists():
        print(f"❌ Arquivo {ARQUIVO_JSON} não encontrado!")
        return

    with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
        dados_json = json.load(f)

    estacoes_formatadas = []
    
    for e in dados_json:
        dt_inicio = e.get("DT_INICIO_OPERACAO")
        dt_ultima = e.get("DT_ULTIMA_REMESSA")
        
        start_date = datetime.strptime(dt_inicio, "%Y-%m-%d").date() if dt_inicio else None
        last_date = datetime.strptime(dt_ultima, "%Y-%m-%d").date() if dt_ultima else None

        source_val = SourceEnum[e.get("SOURCE")] if e.get("SOURCE") else None
        try:
            station_type_val = StationTypeEnum(e.get("TIPO_ESTACAO")) if e.get("TIPO_ESTACAO") else None
        except ValueError:
            station_type_val = None

        estacoes_formatadas.append({
            "code": e.get("CD_ESTACAO"),
            "source": source_val,
            "name": e.get("DC_NOME"),
            "city": e.get("DC_CIDADE"),
            "state": e.get("SG_ESTADO"),
            "latitude": e.get("VL_LATITUDE"),
            "longitude": e.get("VL_LONGITUDE"),
            "status": e.get("CD_SITUACAO"),
            "operation_start_date": start_date,
            "last_data_date": last_date,
            "station_type": station_type_val
        })

    with SessionLocal() as db:
        try:
            print(f"Inserindo {len(estacoes_formatadas)} estações...")
            
            db.bulk_insert_mappings(Station, estacoes_formatadas)
            db.commit()
            
            print("✅ Sucesso! Todas as estações foram cadastradas.")
        except Exception as erro:
            db.rollback()
            print(f"❌ Erro ao salvar no banco: {erro}")

if __name__ == "__main__":
    populate_db()