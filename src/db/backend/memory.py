import abc
import csv
import json
import os
from typing import Optional

StudentRecord = tuple[int, str, str, int, str]


class DatabaseError(Exception):
    """Кастомное исключение для ошибок базы данных."""
    pass


class BaseStudentDatabase(abc.ABC):
    """Абстрактный базовый класс СУБД с поддержкой автоматической индексации."""

    def __init__(self):
        self._students: list[StudentRecord] = []
        self._index_id: dict[int, StudentRecord] = {}
        self._index_sex: dict[str, list[StudentRecord]] = {}
        # Описываем структуру таблицы, как требует методичка
        self._columns = ["id", "first_name", "second_name", "age", "sex"]

    def _rebuild_indexes(self) -> None:
        """Полная пересборка индексов."""
        self._index_id.clear()
        self._index_sex.clear()
        for record in self._students:
            self._add_to_index(record)

    def _add_to_index(self, record: StudentRecord) -> None:
        """Добавление записи в индексы."""
        rec_id, _, _, _, sex = record
        self._index_id[rec_id] = record
        if sex not in self._index_sex:
            self._index_sex[sex] = []
        self._index_sex[sex].append(record)

    def create_record(self, student_id: int, first_name: str,
                      second_name: str, age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise ValueError("Поле age не может быть отрицательным.")

        if student_id in self._index_id:
            raise ValueError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._students.append(new_record)
        self._add_to_index(new_record)
        self._save_data()
        return new_record

    def select_record(self, student_id: Optional[int] = None,
                      first_name: Optional[str] = None,
                      second_name: Optional[str] = None,
                      age: Optional[int] = None,
                      sex: Optional[str] = None) -> list[StudentRecord]:
        if all(v is None for v in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()

        if student_id is not None:
            indexed_record = self._index_id.get(student_id)
            source_set = [indexed_record] if indexed_record else []
        elif sex is not None:
            source_set = self._index_sex.get(sex, [])
        else:
            source_set = self._students

        result = []
        for record in source_set:
            # Переносим continue на новые строки для соответствия PEP 8 (исправление E701)
            if student_id is not None and record[0] != student_id:
                continue
            if first_name is not None and record[1] != first_name:
                continue
            if second_name is not None and record[2] != second_name:
                continue
            if age is not None and record[3] != age:
                continue
            if sex is not None and record[4] != sex:
                continue
            result.append(record)
        return result

    def sort_records(self, field: str, reverse: bool = False) -> list[StudentRecord]:
        mapping = {'id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
        if field not in mapping:
            raise ValueError(f"Недопустимое поле для сортировки: '{field}'")
        index = mapping[field]
        return sorted(self._students, key=lambda record: record[index], reverse=reverse)

    @abc.abstractmethod
    def _save_data(self) -> None:
        """Абстрактный метод для сохранения данных на диск."""
        pass


class StudentDatabase(BaseStudentDatabase):
    """In-Memory реализация СУБД."""

    def _save_data(self) -> None:
        pass  # Для оперативной памяти сохранение — пустая операция


class JsonStudentDatabase(BaseStudentDatabase):
    """Файловая JSON СУБД с сохранением структуры таблицы."""

    def __init__(self, filename: str = "students.json"):
        super().__init__()
        self.filename = filename
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                # Извлекаем схему и записи согласно методичке
                raw_records = payload.get("records", [])
                self._columns = payload.get("columns", self._columns)
                self._students = [tuple(item) for item in raw_records]
                self._rebuild_indexes()
        except (json.JSONDecodeError, IOError) as e:
            raise DatabaseError(f"Ошибка при чтении JSON файла: {e}")

    def _save_data(self) -> None:
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                # Храним объект вида {"columns": [...], "records": [...]}
                payload = {
                    "columns": self._columns,
                    "records": self._students
                }
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except IOError as e:
            raise DatabaseError(f"Ошибка при записи JSON файла: {e}")


class CsvStudentDatabase(BaseStudentDatabase):
    """Файловая CSV СУБД."""

    def __init__(self, filename: str = "students.csv"):
        super().__init__()
        self.filename = filename
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                self._students = []
                for row in reader:
                    if not row or len(row) < 5:
                        continue
                    self._students.append((int(row[0]), row[1].strip(), row[2].strip(), int(row[3]), row[4].strip()))
                self._rebuild_indexes()
        except (IOError, ValueError, IndexError) as e:
            raise DatabaseError(f"Ошибка при чтении CSV файла: {e}")

    def _save_data(self) -> None:
        try:
            with open(self.filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(self._students)
        except IOError as e:
            raise DatabaseError(f"Ошибка при записи CSV файла: {e}")
