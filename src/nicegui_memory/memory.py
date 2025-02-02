"""Memory Game"""

import asyncio
import random
from enum import IntEnum
from math import prod
from typing import Final, Literal

from nicegui import elements, ui

CARD_CODE: Final[int] = 127136


class Suit(IntEnum):
    """トランプのスーツ"""

    Spade = 0
    Heart = 1
    Diamond = 2
    Club = 3


# トランプの数字
type Rank = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


class Card(ui.element):
    """カード"""

    def __init__(self, click, num: int):
        """表と裏のdivタグを作成"""
        super().__init__("div")
        self.num = num
        suit = num // 13
        rank = num % 13 + 1
        char = chr(CARD_CODE + suit * 16 + rank + (rank > 11))  # noqa: PLR2004
        color = "black" if suit in {Suit.Spade, Suit.Club} else "red-10"
        with self.classes("card").on("click", lambda: click(self)):
            ui.label(chr(CARD_CODE)).classes("face front text-blue-10")
            ui.label(char).classes(f"face back text-{color}")

    def flip(self):
        """カードをひっくり返す"""
        self.classes(toggle="flipped")

    @property
    def flipped(self):
        """表かどうか"""
        return "flipped" in self.classes


class Game(ui.element):
    """ゲーム"""

    size: tuple[int, int] = 3, 4
    player: Literal[0, 1]
    points: list[int]
    message: str
    message_ui: elements.label
    opened: Card | None
    in_click: bool

    def start(self, dialog):
        """新規ゲーム"""
        self.player = 1
        self.points = [0, 0]
        self.build(dialog)
        self.turn()
        self.in_click = False
        dialog.close()

    def turn(self):
        """手番交代"""
        self.player = 1 - self.player
        self.message = f"Player {self.player + 1}'s turn"
        color = ["text-green-10", "text-orange-10"][self.player]
        self.message_ui.classes(color, remove="text-green-10 text-orange-10")
        self.opened = None

    def build(self, dialog):
        """GUI作成"""
        nums = [*range(52)]
        random.shuffle(nums)
        nums = nums[: prod(self.size) // 2]
        nums *= 2
        random.shuffle(nums)
        self.clear()
        with self:
            self.message_ui = ui.label().bind_text(self, "message").classes("text-2xl")
            with ui.column():
                for _ in range(self.size[0]):
                    with ui.row():
                        for _ in range(self.size[1]):
                            Card(self.click, nums.pop())
            if dialog is not None:
                with ui.row().classes("m-4"):
                    ui.button("New Game", on_click=dialog.open)

    async def click(self, card: Card):
        """クリック時の処理"""
        if card.flipped or self.in_click:
            return
        self.in_click = True
        card.flip()
        if self.opened is None:
            self.opened = card
        elif card.num != self.opened.num:  # ハズレ
            await asyncio.sleep(1)
            self.opened.flip()
            card.flip()
            self.turn()
        else:  # アタリ
            color = f"bg-{['green', 'orange'][self.player]}-2"
            self.opened.classes(color)
            card.classes(color)
            self.points[self.player] += 2
            self.opened = None
            self.judge()
        self.in_click = False

    def judge(self):
        """判定してメッセージ設定"""
        if sum(self.points) == prod(self.size):
            self.message_ui.classes(remove="text-green-10 text-orange-10")
            if self.points[0] > self.points[1]:
                self.message = "Player 1 won."
            elif self.points[0] < self.points[1]:
                self.message = "Player 2 won."
            else:
                self.message = "Draw."


def main():
    """ゲーム実行"""
    ui.add_css("""
    .card {
        width: 68px;
        height: 112px;
        perspective: 1000px;
    }

    .face {
        position: absolute;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 8em;
        backface-visibility: hidden;
        transition: transform 0.6s;
    }

    .back {
        transform: rotateY(180deg);
    }

    .card.flipped .front {
        transform: rotateY(180deg);
    }

    .card.flipped .back {
        transform: rotateY(0);
    }
    """)

    game = Game()
    with ui.dialog() as dialog, ui.card():  # 新規ゲームのダイアログ
        ui.label("New Game").classes("text-2xl")
        with ui.row():
            ui.label("Size")
            ui.select({(3, 4): "3 x 4", (4, 5): "4 x 5", (5, 8): "5 x 8"}).bind_value(game, "size")
        ui.button("Start", on_click=lambda: game.start(dialog))
    game.start(dialog)
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
