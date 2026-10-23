from typing import Callable

class Table:
    def __init__(self, primary_key: str):
        assert isinstance(primary_key, str), "A primary key must be provided."
        self.rows = {}
        self.hash = {}
        self.next_id = 0
        self.primary_key = primary_key

    def insert(self, row: dict) -> int:
        row_id = self.next_id
        self.next_id += 1
        self.rows[row_id] = row
        hash_key = row[self.primary_key]
        self.hash[hash_key] = row_id
        return row_id

    def delete(self, row_id: int):
        if row_id not in self.rows:
            return
        key = self.rows[row_id][self.primary_key]
        self.hash.pop(key, None)
        del self.rows[row_id]

    def update(self, row_id: int, **changes):
        if row_id not in self.rows:
            raise KeyError(f"Row ID {row_id} does not exist.")
            
        row = self.rows[row_id]
        
        if self.primary_key in changes:
            old_key = row[self.primary_key]
            new_key = changes[self.primary_key]
            
            if old_key != new_key:
                del self.hash[old_key]
                self.hash[new_key] = row_id

        row.update(changes)

    def select(self, where: Callable[[dict], bool]=None, order_by: str | None=None, limit: int | None=None, reverse: bool=False) -> list[dict]:
        rows = [r for r in self.rows.values() if where is None or where(r)]
        if order_by: rows.sort(key=lambda r: r[order_by], reverse=reverse)
        if limit: rows = rows[:limit]
        return rows

    def find[T](self, value: T) -> int:
        if not self.has(value):
            raise KeyError(f"Cannot find row '{value}'")
        return self.hash[value]

    def has[T](self, value: T) -> bool:
        return value in self.hash