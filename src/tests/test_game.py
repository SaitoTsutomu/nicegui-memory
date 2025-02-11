# flake8: noqa: S101
"""テスト"""

from collections import Counter
from unittest.mock import patch

from nicegui_memory import Game


def test_game_build() -> None:
    """game.build()で、Cardがペアで作成されることをテスト"""
    game = Game()
    game.sizes = 3, 4  # 3行4列のカード
    with patch("nicegui_memory.memory.Card") as card_class:
        game.build(None)
    # call_args.args[1]は、カードの識別番号
    c = Counter(call_args.args[1] % 26 for call_args in card_class.call_args_list)
    assert [*c.values()] == [2, 2, 2, 2, 2, 2], "ペアになってない"
