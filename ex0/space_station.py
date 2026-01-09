#!/usr/bin/env python3
import sys
try:
    from pydantic import BaseModel, Field, ValidationError
except ImportError as e:
    print(f"ImportError: {e}")
    print("pydanticをインストールする必要があります。")
    print("ルートディレクトリにて以下のコマンドを実行してください。")
    print("    python3 -m venv m9_ven")
    print("    source m9_ven/bin/activate")
    print("    pip install pydantic")
    sys.exit(1)

from typing import Optional
from pathlib import Path
from datetime import datetime
import json


class SpaceStation(BaseModel):
    """
    宇宙ステーションの属性モデル
    pydantic.BaseBodelを継承し、型の検証を担う
    """

    station_id: str = Field(min_length=3,
                            max_length=10,
                            description="宇宙ステーション識別ID")
    name: str = Field(min_length=1,
                      max_length=50,
                      description="宇宙ステーション名")
    crew_size: int = Field(ge=1,
                           le=20,
                           description="ステーションクルー人数")
    power_level: float = Field(ge=0.0,
                               le=100.0,
                               description="電力")
    oxygen_level: float = Field(ge=0.0,
                                le=100.0,
                                description="酸素レベル")
    last_maintenance: datetime
    is_operational: bool = True
    notes: Optional[str] = Field(default=None,
                                 max_length=200,
                                 description="コメント")


def loading_json(file_name: str) -> list:
    """
    jsonファイルから情報を取得する
    """

    current_dir = Path(__file__).parent
    target_dir = current_dir.parent / "tools" / "generated_data"
    file_path = target_dir / file_name

    if not file_path.exists():
        print("jsonファイルが見つかりません。")
        print("ルートディレクトリにて以下のコマンドを実行してください。")
        print("    wget {data_generator.tar}")
        print("    mkdir tools")
        print("    mv data_exporter.py tools")
        print("    python data_exporter.py")
        sys.exit(1)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def valid_station_data(station_data: list) -> None:
    """
    渡されたステーションデータを検証する
    """

    for data in station_data:
        try:
            station = SpaceStation(**data)
            status = 'Operational' if station.is_operational else 'Maintenance'
            print("Valid station created:\n"
                  f"ID: {station.station_id}\n"
                  f"Name: {station.name}\n"
                  f"Crew: {station.crew_size} people\n"
                  f"Power: {station.power_level}%\n"
                  f"Oxygen: {station.oxygen_level}%\n"
                  f"Status: {status}"
                  f"Maintenance: {station.last_maintenance}"
                  f"note: {station.notes}")
            print()
            print("========================================")
        except ValidationError as e:
            print("Validation error:")
            for err in e.errors():
                print(f"    - {err['loc'][0]}: {err['msg']}")


def main() -> None:
    """
    宇宙ステーションの重要データの検証システム
    """

    print("Space Station Data Validation\n"
          "========================================")

    target_data = loading_json("space_stations.json")
    invalid_data = loading_json("invalid_stations.json")

    valid_station_data(target_data)
    valid_station_data(invalid_data)


if __name__ == "__main__":
    main()
