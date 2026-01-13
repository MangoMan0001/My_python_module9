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

from typing import Optional
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
        print("    tar -xzf data_generator.tar")
        print("    rm data_generator.tar")
        print("    mkdir tools")
        print("    mv data_*.py tools")
        print("    python tools/data_exporter.py")
        print("    mv generated_data tools")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


class ContactType(str, Enum):
    """
    エイリアンと遭遇したシチュエーションを定義
    """

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """
    遭遇ログのテンプレート
    pydantic.MaseBodelを継承し、テンプレートどおりかの検証を担う

        • contact_id: String, 5-15 characters
        • timestamp: DateTime of contact
        • location: String, 3-100 characters
        • contact_type: ContactType enum
        • signal_strength: Float, 0.0-10.0 scale
        • duration_minutes: Integer, 1-1440 (max 24 hours)
        • witness_count: Integer, 1-100 people
        • message_received: Optional string, max 500 characters
        • is_verified: Boolean, defaults to False
    """

    contact_id: str = Field(min_length=5,
                            max_length=15,
                            description="エイリアンコンタクトID")
    timestamp: datetime
    location: str = Field(min_length=3,
                          max_length=100,
                          description="コンタクトロケーション")
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0,
                                   le=10.0,
                                   description="通信強度")
    duration_minutes: int = Field(ge=1,
                                  le=1440,
                                  description="通信時間最大24時間")
    witness_count: int = Field(ge=1,
                               le=100,
                               description="目撃者の人数")
    message_received: Optional[str] = Field(max_length=500,
                                            description="受信メッセージ")
    is_verified: bool = Field(default=False,
                              description="検証済みか")

    # .これがafterでついているとAlianContactで型検証し終わってから追加で検証してくれる
    # .条件が他属性に依存する場合に用いられる
    @model_validator(mode="after")
    def after_valid_contact_data(self) -> "AlienContact":
        """
        ４つの項目を追加検証する

            • Contact ID must start with "AC" (Alien Contact)
            • Physical contact reports must be verified
            • Telepathic contact requires at least 3 witnesses
            • Strong signals (> 7.0) should include received messages
        """

        # .ここでValueErrorを吐くと、pydanticが勝手にValidationErrorにしてくれる
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")

        if self.contact_type == "physical" and not self.is_verified:
            raise ValueError(
                "Physical contact reports must be verified explicitly.")

        if self.contact_type == "telepathic" and not 3 <= self.witness_count:
            raise ValueError("Telepathic contact requires at "
                             f"least 3 witnesses (got {self.witness_count}).")

        if 7 <= self.signal_strength and not self.message_received:
            raise ValueError("Strong signals (> 7.0) must "
                             "include a received message.")

        return self


def valid_contact_data(contact_data: list) -> None:
    """
    渡された遭遇データを検証後、printする
    属性が足りなかったり、エラーだったらその都度エラーを吐く
    """

    for data in contact_data:
        try:
            contact = AlienContact(**data)
            print("Valid contact created:\n"
                  f"ID: {contact.contact_id}\n"
                  f"Type: {contact.contact_type}\n"
                  f"Time: {contact.timestamp}\n"
                  f"Location: {contact.location}\n"
                  f"Signal: {contact.signal_strength}%\n"
                  f"Duration: {contact.duration_minutes} minutes%\n"
                  f"Witnesses: {contact.witness_count}"
                  f"Message: {contact.message_received}"
                  f"Verified: {contact.is_verified}")
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

    print("Alien Contact Log Validation\n"
          "========================================")

    target_data = loading_json("alien_contacts.json")
    invalid_data = loading_json("invalid_contacts.json")

    valid_contact_data(target_data)
    valid_contact_data(invalid_data)


if __name__ == "__main__":
    main()
