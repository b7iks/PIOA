type StudentRecord = tuple[int, str, str, int, str]

Student: list[StudentRecord] = []

def create_record(
    student_id: int,   # Уникальный идентификатор записи
    first_name: str,   # Имя
    second_name: str,  # Фамилия
    age: int,          # Возраст
    sex: str,          # Пол
) -> StudentRecord:
    """
    Создаёт новую запись и добавляет её в таблицу Student.

    Выполняется валидация возраста и проверка уникальности идентификатора.
    В случае нарушения условий возбуждается исключение ValueError.
    """

    # Проверка корректности возраста.
    # Возраст не может быть отрицательным значением.
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным.")

    # Проверка уникальности идентификатора.
    # Функция any() возвращает True, если хотя бы один элемент
    # последовательности удовлетворяет условию.
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")

    # Формирование новой записи.
    # Метод strip() удаляет пробельные символы
    # в начале и в конце строки.
    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    # Добавление записи в таблицу.
    Student.append(new_record)

    # Возврат созданной записи.
    return new_record

def select_record(
    student_id: int | None = None,   # Фильтр по идентификатору
    first_name: str | None = None,   # Фильтр по имени
    second_name: str | None = None,  # Фильтр по фамилии
    age: int | None = None,          # Фильтр по возрасту
    sex: str | None = None,          # Фильтр по полу
) -> list[StudentRecord]:
    """
    Выполняет выборку записей из таблицы Student
    в соответствии с переданными фильтрами.

    Если фильтры не заданы, возвращается копия всей таблицы.
    """

    # Проверка отсутствия всех фильтров.
    # В этом случае возвращается копия списка,
    # чтобы предотвратить изменение исходной таблицы
    # внешним кодом.
    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return Student.copy()

    # Формирование результирующего списка.
    result: list[StudentRecord] = []

    # Итерация по всем записям таблицы.
    for record in Student:

        # Проверка соответствия каждому фильтру.
        # Если фильтр задан и запись ему не соответствует,
        # выполняется переход к следующей итерации цикла.

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

        # Если запись удовлетворяет всем заданным условиям,
        # она добавляется в результирующий список.
        result.append(record)

    # Возврат списка найденных записей.
    return result
