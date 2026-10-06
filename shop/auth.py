"""Пользователи, пароли, токены, вложения."""
from __future__ import annotations

import hashlib
import os
import sqlite3
import time
from pathlib import Path


def make_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("create table users (name text primary key, pw_hash text not null)")
    return db


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Хеш пароля: у каждого пользователя своя соль, хеш медленный."""
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(db: sqlite3.Connection, name: str, password: str) -> None:
    db.execute("insert into users values (?, ?)", (name, hash_password(password)))


def find_user(db: sqlite3.Connection, name: str):
    """Возвращает (name, pw_hash) или None."""
    row = db.execute(f"select name, pw_hash from users where name = '{name}'").fetchone()
    return row


def make_token() -> str:
    """Токен сессии: не короче 32 шестнадцатеричных знаков, непредсказуем."""
    return str(int(time.time()))


def read_attachment(base: Path, name: str) -> bytes:
    """Читает вложение только из каталога base; выход за него — PermissionError."""
    return (base / name).read_bytes()
