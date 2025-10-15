# Игра Wordle - Угадай слово из 5 букв
print("=== Игра Wordle ===")
print("Угадай слово из 5 букв!")
print("После каждой попытки ты увидишь:")
print("[X] - буква на правильном месте")
print("(X) - буква есть в слове, но на другой позиции")
print(" X  - буквы нет в слове")
print("")

# Список слов для игры
slova = ['лотос', 'столп', 'комод', 'рамка', 'ветер', 'речка', 'солнце', 'дверь', 'окно', 'книга']

# Компьютер загадывает случайное слово
import random
zagadannoe_slovo = random.choice(slova)

print(f"Компьютер загадал слово из 5 букв. У тебя 6 попыток!")

# Основной цикл игры
popytka = 1
while popytka <= 6:
    print(f"\n--- Попытка {popytka} ---")
    
    # Получаем слово от игрока
    while True:
        predpolozhenie = input("Введи слово из 5 букв: ").lower()
        if len(predpolozhenie) == 5:
            break
        else:
            print("Слово должно быть из 5 букв! Попробуй еще раз.")
    
    # Проверяем, угадал ли игрок слово
    if predpolozhenie == zagadannoe_slovo:
        print(f"Поздравляю! Ты угадал слово '{zagadannoe_slovo}' за {popytka} попыток!")
        break
    
    # Анализируем буквы и создаем подсказки
    resultat = []  # Сюда будем складывать подсказки
    ispolzovannye_bukvy = []  # Для учета уже использованных букв
    
    # Сначала отмечаем буквы на правильных местах
    for i in range(5):
        if predpolozhenie[i] == zagadannoe_slovo[i]:
            resultat.append(f"[{predpolozhenie[i]}]")
            ispolzovannye_bukvy.append(predpolozhenie[i])
        else:
            resultat.append("?")  # Временно ставим знак вопроса
    
    # Теперь проверяем буквы, которые есть в слове, но на других местах
    for i in range(5):
        if resultat[i] == "?":  # Если буква еще не обработана
            bukva = predpolozhenie[i]
            
            # Считаем, сколько раз эта буква должна быть отмечена
            vsego_v_slove = zagadannoe_slovo.count(bukva)
            uzhe_otmecheno = ispolzovannye_bukvy.count(bukva)
            
            if bukva in zagadannoe_slovo and uzhe_otmecheno < vsego_v_slove:
                resultat[i] = f"({bukva})"
                ispolzovannye_bukvy.append(bukva)
            else:
                resultat[i] = f" {bukva} "  # Буквы нет в слове
    
    # Выводим результат
    print("Результат:", " ".join(resultat))
    
    popytka += 1

# Если попытки закончились
if popytka > 6:
    print(f"\nК сожалению, попытки закончились!")
    print(f"Загаданное слово было: '{zagadannoe_slovo}'")

print("\nСпасибо за игру!")