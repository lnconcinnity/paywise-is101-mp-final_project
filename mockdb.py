from typing import Callable, Optional

class Table:
    def __init__(self):
        self.rows = {}
        self.next_id = 0

    def insert(self, row: dict) -> int:
        row_id = self.next_id
        self.next_id += 1
        self.rows[row_id] = row
        return row_id

    def delete(self, row_id: int):
        del self.rows[row_id]

    def update(self, row_id: int, **changes):
        self.rows[row_id].update(changes)

    def select(self, where: Callable[[dict], bool]=None, order_by: Optional[str]=None, reverse: bool=False):
        rows = [r for r in self.rows.values() if where is None or where(r)]
        if order_by:
            rows.sort(key=lambda r: r[order_by], reverse=reverse)
        return rows

    def find(self, where: Callable[[dict], bool]=None):
        for row_id, row in self.rows.items():
            if where is None or where(row):
                return row_id, row
        return None, None