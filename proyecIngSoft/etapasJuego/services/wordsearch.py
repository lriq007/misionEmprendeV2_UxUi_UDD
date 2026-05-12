"""
Board generation for the word-search stage.
Port of logicaJuegosCopy/juegos/juegoSopaLetras.py adapted for Django.
"""
from __future__ import annotations

from random import choice, randint
from string import ascii_uppercase
from typing import Optional


def generate_board(
    words: list[str],
    size: int = 12,
) -> tuple[list[list[str]], dict[str, list[list[int]]]]:
    """
    Generate a word-search board with all words placed.

    Returns:
        board  – size×size grid of uppercase letters
        positions – {WORD: [[r,c], [r,c], …]} mapping for validation
    """
    words = [w.upper().strip() for w in words]
    board: list[list[str]] = [[""] * size for _ in range(size)]
    positions: dict[str, list[list[int]]] = {}

    # Place longest words first (fewer conflicts)
    for word in sorted(words, key=len, reverse=True):
        _place_word(board, word, size, positions)

    _fill_empty(board, size)
    return board, positions


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]


def _place_word(
    board: list[list[str]],
    word: str,
    size: int,
    positions: dict[str, list[list[int]]],
) -> None:
    for _ in range(300):
        dr, dc = choice(_DIRECTIONS)
        r = randint(0, size - 1)
        c = randint(0, size - 1)
        cells = _calc_positions(word, r, c, dr, dc, size)
        if cells and _can_place(board, word, cells):
            for letter, (row, col) in zip(word, cells):
                board[row][col] = letter
            positions[word] = [[row, col] for row, col in cells]
            return
    raise ValueError(f"No se pudo ubicar la palabra '{word}' en el tablero.")


def _calc_positions(
    word: str,
    r: int,
    c: int,
    dr: int,
    dc: int,
    size: int,
) -> Optional[list[tuple[int, int]]]:
    cells = []
    for i in range(len(word)):
        nr, nc = r + dr * i, c + dc * i
        if not (0 <= nr < size and 0 <= nc < size):
            return None
        cells.append((nr, nc))
    return cells


def _can_place(
    board: list[list[str]],
    word: str,
    cells: list[tuple[int, int]],
) -> bool:
    for letter, (r, c) in zip(word, cells):
        existing = board[r][c]
        if existing not in ("", letter):
            return False
    return True


def _fill_empty(board: list[list[str]], size: int) -> None:
    for r in range(size):
        for c in range(size):
            if board[r][c] == "":
                board[r][c] = choice(ascii_uppercase)
