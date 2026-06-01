from typing import Optional

StudentRecord = tuple[int, str, str, int, str]


class StudentDatabase:
    def __init__(self):
        self._students: list[StudentRecord] = []

    def sort_records(self, field: str, reverse: bool = False) -> list[StudentRecord]:
        mapping = {
            'id': 0,
            'first_name': 1,
            'second_name': 2,
            'age': 3,
            'sex': 4
        }

        if field not in mapping:
            raise ValueError(f"Недопустимое поле для сортировки: '{field}'. Доступные поля: {list(mapping.keys())}")

        index = mapping[field]

        return sorted(self._students, key=lambda record: record[index], reverse=reverse)

    def create_record(self, student_id: int, first_name: str,
                      second_name: str, age: int, sex: str) -> StudentRecord:
        if age < 0:
            raise ValueError("Поле age не может быть отрицательным.")

        if any(record[0] == student_id for record in self._students):
            raise ValueError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._students.append(new_record)
        return new_record

    def select_record(self, **filters) -> list[StudentRecord]:
        if not filters or all(v is None for v in filters.values()):
            return self._students.copy()

        result = []
        for record in self._students:
            # Маппинг фильтров на индексы кортежа
            mapping = {'student_id': 0, 'first_name': 1, 'second_name': 2, 'age': 3, 'sex': 4}
            match = True
            for key, value in filters.items():
                if value is not None and record[mapping[key]] != value:
                    match = False
                    break
            if match:
                result.append(record)
        return result