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
    """Абстрактный базовый класс СУБД с универсальным механизмом индексации."""

    def __init__(self, indexed_fields: Optional[list[str]] = None):
        self._students: list[StudentRecord] = []
        self._columns = ["id", "first_name", "second_name", "age", "sex"]

        # Динамическая инициализация индексов (Доп. задание на 5 баллов)
        self.indexed_fields = indexed_fields or ["id", "sex"]
        for field in self.indexed_fields:
            if field not in self._columns:
                raise DatabaseError(f"Невозможно создать индекс по несуществующему полю: '{field}'")

        # Словарь индексов вида: { 'название_поля': { 'значение_ключа': [записи] } }
        self._indexes: dict[str, dict[any, list[StudentRecord]]] = {
            field: {} for field in self.indexed_fields
        }

    def _rebuild_indexes(self) -> None:
        """Полная пересборка всех зарегистрированных индексов."""
        for field in self.indexed_fields:
            self._indexes[field].clear()
        for record in self._students:
            self._add_to_index(record)

    def _add_to_index(self, record: StudentRecord) -> None:
        """Динамическое добавление записи во все активные индексы."""
        for field in self.indexed_fields:
            field_idx = self._columns.index(field)
            key_value = record[field_idx]

            if key_value not in self._indexes[field]:
                self._indexes[field][key_value] = []
            self._indexes[field][key_value].append(record)

    def create_record(self, student_id: int, first_name: str,
                      second_name: str, age: int, sex: str) -> StudentRecord:
        # Валидация обязательных строковых полей (Замечание ревью)
        if not first_name.strip():
            raise ValueError("Поле first_name не может быть пустым.")
        if not second_name.strip():
            raise ValueError("Поле second_name не может быть пустым.")
        if not sex.strip():
            raise ValueError("Поле sex не может быть пустым.")
        if age < 0:
            raise ValueError("Поле age не может быть отрицательным.")

        # Быстрая проверка уникальности ID через динамический индекс (если он активен)
        if "id" in self._indexes and student_id in self._indexes["id"]:
            raise ValueError(f"Запись с id={student_id} уже существует.")
        elif any(rec[0] == student_id for rec in self._students):
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

    def select_record(self, **filters) -> list[StudentRecord]:
        """Выборка данных с автоматическим подбором лучшего доступного индекса."""
        if not filters or all(v is None for v in filters.values()):
            return self._students.copy()

        # Ищем подходящий индекс среди переданных фильтров
        best_field = None
        for field in self.indexed_fields:
            if filters.get(field) is not None:
                best_field = field
                break

        # Определяем начальное подмножество записей для перебора
        if best_field:
            field_val = filters[best_field]
            source_set = self._indexes[best_field].get(field_val, [])
        else:
            source_set = self._students

        result = []
        for record in source_set:
            match = True
            for field, val in filters.items():
                if val is None:
                    continue
                if field not in self._columns:
                    continue
                field_idx = self._columns.index(field)
                if record[field_idx] != val:
                    match = False
                    break
            if match:
                result.append(record)
        return result

    def sort_records(self, field: str, reverse: bool = False) -> list[StudentRecord]:
        # Построение маппинга динамически на основе единой схемы self._columns (Замечание ревью)
        if field not in self._columns:
            raise ValueError(f"Недопустимое поле для сортировки: '{field}'. Доступны: {self._columns}")
        index = self._columns.index(field)
        return sorted(self._students, key=lambda record: record[index], reverse=reverse)

    @abc.abstractmethod
    def _save_data(self) -> None:
        """Абстрактный интерфейсный метод сохранения."""
        pass


class StudentDatabase(BaseStudentDatabase):
    """In-Memory реализация СУБД."""

    def _save_data(self) -> None:
        pass


class JsonStudentDatabase(BaseStudentDatabase):
    """Файловая JSON СУБД со структурированной схемой таблицы."""

    def __init__(self, filename: str = "students.json", indexed_fields: Optional[list[str]] = None):
        super().__init__(indexed_fields=indexed_fields)
        self.filename = filename
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                self._columns = payload.get("columns", self._columns)
                raw_records = payload.get("records", [])
                self._students = [tuple(item) for item in raw_records]
                self._rebuild_indexes()
        except (json.JSONDecodeError, IOError) as e:
            raise DatabaseError(f"Ошибка при чтении JSON файла: {e}")

    def _save_data(self) -> None:
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                payload = {"columns": self._columns, "records": self._students}
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except IOError as e:
            raise DatabaseError(f"Ошибка при записи JSON файла: {e}")


class CsvStudentDatabase(BaseStudentDatabase):
    """Файловая CSV СУБД с сохранением заголовка структуры колонок."""

    def __init__(self, filename: str = "students.csv", indexed_fields: Optional[list[str]] = None):
        super().__init__(indexed_fields=indexed_fields)
        self.filename = filename
        self._load_data()

    def _parse_csv_row(self, row: list[str]) -> StudentRecord:
        """Отдельный чистый метод десериализации, парсинга и типизации строки CSV."""
        return (int(row[0]), row[1].strip(), row[2].strip(), int(row[3]), row[4].strip())

    def _load_data(self) -> None:
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if not rows:
                    return

                # Читаем метаданные схемы из первой строки (Замечание ревью)
                self._columns = rows[0]

                self._students = []
                for row in rows[1:]:
                    if not row or len(row) < 5:
                        continue
                    self._students.append(self._parse_csv_row(row))
                self._rebuild_indexes()
        except (IOError, ValueError, IndexError) as e:
            raise DatabaseError(f"Ошибка при чтении CSV файла: {e}")

    def _save_data(self) -> None:
        try:
            with open(self.filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                # Первой строкой пишем структуру (схему) таблицы
                writer.writerow(self._columns)
                writer.writerows(self._students)
        except IOError as e:
            raise DatabaseError(f"Ошибка при записи CSV файла: {e}")
