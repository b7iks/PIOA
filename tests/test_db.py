import pytest
import os
import json
from db.backend.memory import StudentDatabase, JsonStudentDatabase, CsvStudentDatabase


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

    with pytest.raises(RuntimeError, match="Ошибка при чтении JSON файла"):
        JsonStudentDatabase(filename=str(file_path))



def test_csv_db_save_and_load(tmp_path):
    file_path = tmp_path / "test_students.csv"

    db1 = CsvStudentDatabase(filename=str(file_path))
    db1.create_record(5, "Anna", "Sidorova", 22, "f")

    db2 = CsvStudentDatabase(filename=str(file_path))
    records = db2.select_record()

    assert len(records) == 1
    assert records[0] == (5, "Anna", "Sidorova", 22, "f")
    assert isinstance(records[0][0], int)
    assert isinstance(records[0][3], int)


def test_csv_db_invalid_format_raises_error(tmp_path):

    file_path = tmp_path / "corrupted.csv"
    with open(file_path, "w") as f:
        f.write("строка,без,чисел,для,парсинга\n")

    with pytest.raises(RuntimeError, match="Ошибка при чтении CSV файла"):
        CsvStudentDatabase(filename=str(file_path))



@pytest.fixture
def mem_db():
    return StudentDatabase()


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

    def test_indexing_mechanism_on_create(mem_db):

        mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")

        assert 1 in mem_db._index_id
        assert "m" in mem_db._index_sex
        assert len(mem_db._index_sex["m"]) == 1

    def test_select_utilizes_id_index(mem_db):
        mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
        mem_db.create_record(2, "Anna", "Petrova", 22, "f")


        res = mem_db.select_record(student_id=2)
        assert len(res) == 1
        assert res[0][1] == "Anna"

    def test_select_utilizes_sex_index(mem_db):
        mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
        mem_db.create_record(2, "Anna", "Petrova", 22, "f")
        mem_db.create_record(3, "Petr", "Sidorov", 23, "m")


        res = mem_db.select_record(sex="m")
        assert len(res) == 2
        assert res[0][0] == 1
        assert res[1][0] == 3

    def test_file_db_rebuilds_indexes_on_load(tmp_path):

        file_path = tmp_path / "indexed_students.json"


        db1 = JsonStudentDatabase(filename=str(file_path))
        db1.create_record(10, "Elena", "Smirnova", 19, "f")

        db2 = JsonStudentDatabase(filename=str(file_path))

        assert 10 in db2._index_id
        assert db2._index_id[10][1] == "Elena"


def test_sort_records_invalid_field_raises_error(mem_db):

    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    with pytest.raises(ValueError, match="Недопустимое поле для сортировки"):
        mem_db.sort_records("wrong_field")


def test_select_non_indexed_fields(mem_db):

    mem_db.create_record(1, "Ivan", "Ivanov", 20, "m")
    mem_db.create_record(2, "Petr", "Petrov", 21, "m")

    res_name = mem_db.select_record(first_name="Petr")
    assert len(res_name) == 1
    assert res_name[0][1] == "Petr"

    res_sub = mem_db.select_record(second_name="Ivanov")
    assert len(res_sub) == 1

    res_age = mem_db.select_record(age=21)
    assert len(res_age) == 1


def test_csv_db_rebuilds_indexes_on_load(tmp_path):

    file_path = tmp_path / "indexed_students.csv"


    db1 = CsvStudentDatabase(filename=str(file_path))
    db1.create_record(15, "Oleg", "Olegov", 25, "m")

    db2 = CsvStudentDatabase(filename=str(file_path))

    assert 15 in db2._index_id
    assert db2._index_id[15] == (15, "Oleg", "Olegov", 25, "m")

