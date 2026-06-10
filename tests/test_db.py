import pytest
from db.backend.memory import StudentDatabase, JsonStudentDatabase, CsvStudentDatabase, DatabaseError


@pytest.fixture
def mem_db():
    return StudentDatabase()


def test_create_record_validation():
    """Проверка валидации обязательных строковых полей."""
    db = StudentDatabase()
    with pytest.raises(ValueError, match="не может быть пустым"):
        db.create_record(1, " ", "Ivanov", 20, "m")


def test_create_and_select(mem_db):
    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    assert len(mem_db.select_record()) == 1


def test_negative_age(mem_db):
    with pytest.raises(ValueError):
        mem_db.create_record(1, "A", "B", -1, "m")


def test_sort_records(mem_db):
    mem_db.create_record(2, "B", "B", 25, "m")
    mem_db.create_record(1, "A", "A", 20, "m")
    res = mem_db.sort_records("id")
    assert res[0][0] == 1


def test_sort_records_invalid_field_raises_error(mem_db):
    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    with pytest.raises(ValueError, match="Недопустимое поле для сортировки"):
        mem_db.sort_records("wrong_field")


def test_select_non_indexed_fields(mem_db):
    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    res_name = mem_db.select_record(first_name="Ivan")
    assert len(res_name) == 1


def test_indexing_via_public_select(mem_db):
    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    mem_db.create_record(2, "Anna", "Petrova", 22, "f")
    # Проверка работы через публичный контракт select_record
    assert len(mem_db.select_record(id=1)) == 1
    assert len(mem_db.select_record(sex="m")) == 1


def test_json_db_save_and_load(tmp_path):
    file_path = tmp_path / "test_students.json"
    db1 = JsonStudentDatabase(filename=str(file_path))
    db1.create_record(1, "Ivan", "Ivanov", 20, "m")

    db2 = JsonStudentDatabase(filename=str(file_path))
    records = db2.select_record()
    assert len(records) == 1
    assert records[0] == (1, "Ivan", "Ivanov", 20, "m")


def test_json_db_invalid_format_raises_error(tmp_path):
    file_path = tmp_path / "corrupted.json"
    with open(file_path, "w") as f:
        f.write("{ невалидный json }")
    with pytest.raises(DatabaseError):
        JsonStudentDatabase(filename=str(file_path))


def test_csv_db_save_and_load_with_schema(tmp_path):
    """Проверяем, что CSV теперь сохраняет и восстанавливает и схему и записи."""
    file_path = tmp_path / "test_students.csv"
    db1 = CsvStudentDatabase(filename=str(file_path))
    db1.create_record(5, "Anna", "Sidorova", 22, "f")

    db2 = CsvStudentDatabase(filename=str(file_path))
    records = db2.select_record()
    assert len(records) == 1
    assert db2._columns == ["id", "first_name", "second_name", "age", "sex"]


def test_custom_indexed_fields():
    # Инициализируем базу только с одним индексом по имени
    db = StudentDatabase(indexed_fields=["first_name"])
    db.create_record(1, "Ivan", "Ivanov", 20, "m")

    # Поиск должен успешно отработать через кастомный индекс
    res = db.select_record(first_name="Ivan")
    assert len(res) == 1


def test_invalid_index_field_raises_error():
    with pytest.raises(DatabaseError, match="Невозможно создать индекс"):
        StudentDatabase(indexed_fields=["unexisting_field"])


def test_csv_db_invalid_format_raises_error(tmp_path):
    file_path = tmp_path / "corrupted.csv"
    with open(file_path, "w", encoding='utf-8') as f:
        f.write("id,first_name,second_name,age,sex\n")  # заголовок
        f.write("строка,без,чисел,для,парсинга\n")  # битая строка

    with pytest.raises(DatabaseError, match="Ошибка при чтении CSV файла"):
        CsvStudentDatabase(filename=str(file_path))
