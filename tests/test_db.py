import pytest
from db.backend.memory import StudentDatabase


@pytest.fixture
def db():
    """Фикстура для создания свежего объекта базы перед каждым тестом."""
    return StudentDatabase()


def test_create_record_success(db):
    """Проверка успешного добавления записи."""
    record = db.create_record(1, "Ivan", "Ivanov", 20, "m")
    assert record == (1, "Ivan", "Ivanov", 20, "m")
    assert len(db.select_record()) == 1


def test_duplicate_id_raises_error(db):
    """Проверка ошибки при одинаковых ID."""
    db.create_record(1, "Ivan", "Ivanov", 20, "m")
    with pytest.raises(ValueError, match="уже существует"):
        db.create_record(1, "Petr", "Petrov", 21, "m")


def test_negative_age_raises_error(db):
    """Проверка ошибки при отрицательном возрасте."""
    with pytest.raises(ValueError, match="не может быть отрицательным"):
        db.create_record(2, "Ivan", "Ivanov", -5, "m")


def test_select_all_records(db):
    """Проверка получения всех записей."""
    db.create_record(1, "A", "A", 20, "m")
    db.create_record(2, "B", "B", 21, "f")
    assert len(db.select_record()) == 2


def test_select_with_filter(db):
    """Проверка работы фильтров (поиск)."""
    db.create_record(1, "Ivan", "Ivanov", 20, "m")
    db.create_record(2, "Maria", "Ivanova", 22, "f")

    # Ищем по фамилии
    results = db.select_record(second_name="Ivanova")
    assert len(results) == 1
    assert results[0][1] == "Maria"


def test_select_empty_result(db):
    """Проверка случая, когда по фильтру ничего не найдено."""
    db.create_record(1, "Ivan", "Ivanov", 20, "m")
    results = db.select_record(student_id=999)
    assert len(results) == 0
