import json
from abc import ABC
from typing import List

from .data_manager_interface import DataManagerInterface


class JSONDataManager(DataManagerInterface, ABC):
    def __init__(self, file_name, id_key):
        self._file_name = file_name
        self._id_key = id_key

    def _read_file(self) -> List[dict] | None:
        try:
            with open(self._file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return None
        except FileExistsError:
            return None

    def _write_file(self, items: List[dict]) -> bool | None:
        try:
            with open(self._file_name, 'w', encoding='utf-8') as file:
                json.dump(items, file)
                return True
        except FileNotFoundError:
            return None
        except FileExistsError:
            return None

    def get_all_data(self) -> List[dict] | None:
        return self._read_file()

    def get_item_by_id(self, item_id) -> dict | None:
        items = self._read_file()
        if items:
            for item in items:
                if item[self._id_key] == item_id:
                    return item
        return None

    def generate_new_id(self, items: list, key=None) -> int:
        if items:
            return max(item[key or self._id_key] for item in items) + 1
        return 1

    def add_item(self, new_item: dict) -> bool:
        items = self._read_file()
        new_item.update({self._id_key: self.generate_new_id(items)})
        items.append(new_item)
        self._write_file(items)
        return True

    def update_item(self, updated_item: dict) -> bool | None:
        items = self._read_file()
        for item in items:
            if item[self._id_key] == updated_item[self._id_key]:
                item.update(updated_item)
                self._write_file(items)
                return True
        return None

    def delete_item(self, item_id: int) -> bool | None:
        items = self._read_file()
        if items:
            for item in items:
                if item[self._id_key] == item_id:
                    items.remove(item)
                    self._write_file(items)
                    return True
        return None
