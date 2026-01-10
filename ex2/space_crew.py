#!/usr/bin/env python3
import sys  # 強制終了するためにつかう
try:  # .pydanticがインストールされているか確認
    from pydantic import BaseModel, Field, ValidationError, model_validator
except ImportError as e:
    print(f"ImportError: {e}")
    print("pydanticをインストールする必要があります。")
    print("ルートディレクトリにて以下のコマンドを実行してください。")
    print("    python3 -m venv m9_ven")
    print("    source m9_ven/bin/activate")
    print("    pip install pydantic")
    sys.exit(1)

from pathlib import Path
from datetime import datetime
from enum import Enum
import json


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


class Crew_Rank(str, Enum):
    """
    クルーの階級を定義
    """

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """
    クルーメンバーのテンプレート
    pydantic.BaseBodelを継承し、テンプレートどおりかの検証を担う

        • member_id: String, 3-10 characters
        • name: String, 2-50 characters
        • rank: Rank enum
        • age: Integer, 18-80 years
        • specialization: String, 3-30 characters
        • years_experience: Integer, 0-50 years
        • is_active: Boolean, defaults to True
    """

    member_id: str = Field(min_length=3,
                           max_length=10,
                           description="メンバーID")
    name: str = Field(min_length=2,
                      max_length=50,
                      description="メンバー名")
    rank: Crew_Rank
    age: int = Field(ge=18,
                     le=80,
                     description="年齢")
    specialization: str = Field(min_length=3,
                                max_length=30,
                                description="専門性")
    years_experience: int = Field(ge=0,
                                  le=50,
                                  description="経験年数")
    is_active: bool = True


class SpaceMission(BaseModel):
    """
    ミッションのテンプレート
    pydantic.BaseBodelを継承し、テンプレートどおりかの検証を担う

        • mission_id: String, 5-15 characters
        • mission_name: String, 3-100 characters
        • destination: String, 3-50 characters
        • launch_date: DateTime
        • duration_days: Integer, 1-3650 days (max 10 years)
        • crew: List of CrewMember, 1-12 members
        • mission_status: String, defaults to "planned"
        • budget_millions: Float, 1.0-10000.0 million dollars
    """

    mission_id: str = Field(min_length=5,
                            max_length=15,
                            description="ミッションID")
    mission_name: str = Field(min_length=3,
                              max_length=100,
                              description="ミッション名")
    destination: str = Field(min_length=3,
                             max_length=50,
                             description="行き先")
    launch_date: datetime
    duration_days: int = Field(ge=1,
                               le=3650,
                               description="期間 最大10年")
    crew: list[CrewMember] = Field(min_length=1,
                                   max_length=12,
                                   description="クルー")
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0,
                                   le=10000.0,
                                   description="資金")

    @model_validator(mode="after")
    def after_valid_contact_data(self) -> "SpaceMission":
        """
        ４つの項目を追加検証する

            • Mission ID must start with "M"
            • Must have at least one Commander or Captain
            • Long missions (> 365 days) need 50% experienced crew (5+ years)
            • All crew members must be active
        """

        if not self.mission_id.startswith("M"):
            raise ValueError("Contact ID must start with 'M'")

        if not any(m.rank in (Crew_Rank.CAPTAIN, Crew_Rank.COMMANDER)
                   for m in self.crew):
            raise ValueError("Must have at least one Commander or Captain")

        if 365 < self.duration_days:
            veteran_crew = [m for m in self.crew if 5 <= m.years_experience]
            if not 50 <= len(veteran_crew) / len(self.crew) * 100:
                raise ValueError(
                    "Long missions (> 365 days) "
                    "need 50% experienced crew (5+ years)")

        for m in self.crew:
            if not m.is_active:
                raise ValueError("All crew members must be active")

        return self


def valid_mission_data(contact_data: list) -> None:
    """
    渡されたmissionデータを検証後、printする
    属性が足りなかったり、エラーだったらその都度エラーを吐く
    """

    for data in contact_data:
        try:
            contact = SpaceMission(**data)
            print("Valid mission created:\n"
                  f"Mission: {contact.mission_name}\n"
                  f"ID: {contact.mission_id}\n"
                  f"Destination: {contact.destination}\n"
                  f"Duration: {contact.duration_days} days\n"
                  f"Budget: ${contact.budget_millions}M\n"
                  f"Crew size: {len(contact.crew)}\n"
                  "Crew members:")
            for member in contact.crew:
                print(f"- {member.name} ({member.rank}) "
                      f"- {member.specialization}")
            print()
            print("========================================")

        except ValidationError as e:
            print("Validation error:")
            for err in e.errors():
                location = err["loc"][0] if err["loc"] else "Model Rules"
                print(f"    - {location}: {err['msg']}")


def main() -> None:
    """
    未知との遭遇ログの検証システム
    """

    print("Space Mission Crew Validation\n"
          "========================================")

    target_data = loading_json("space_missions.json")
    # invalid_data = loading_json("invalid_missions.json")

    valid_mission_data(target_data)
    # valid_mission_data(invalid_data.json)


if __name__ == "__main__":
    main()
