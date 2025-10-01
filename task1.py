import random

# Главная функция, с которой начинается программа
def main():
    # Заводим переменные для подсчета статистики
    # Сколько всего игр сыграно
    games_count = 0
    # Сумма всех попыток во всех играх
    all_attempts = 0
    # Самое маленькое число попыток (пока ставим очень большое число)
    best_game = 1000000
    # Самое большое число попыток
    worst_game = 0
    
    # Бесконечный цикл, чтобы можно было играть много раз
    while True:
        # Спрашиваем у пользователя, сколько цифр должно быть в числе
        print("Выбери сложность: 3, 4 или 5 цифр?")
        difficulty = input("Введи число: ")
        
        # Проверяем, что ввели правильное число
        if difficulty not in ["3", "4", "5"]:
            print("Нужно ввести 3, 4 или 5!")
            continue  # Начинаем цикл заново
        
        # Превращаем текст в число
        n = int(difficulty)
        
        # Делаем список цифр от 0 до 9
        numbers_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        # Перемешиваем цифры случайным образом
        random.shuffle(numbers_list)
        
        # Берем первые n цифр из перемешанного списка
        secret_number = ""
        for i in range(n):
            secret_number += numbers_list[i]
        
        # Счетчик попыток для этой игры
        attempts = 0
        print(f"Я загадал число из {n} цифр. Попробуй угадать!")
        
        # Цикл для угадывания числа
        while True:
            # Просим пользователя ввести число
            user_guess = input("Твой вариант: ")
            
            # Проверяем, что ввели правильное количество цифр
            if len(user_guess) != n:
                print(f"Нужно ввести ровно {n} цифр!")
                continue
            
            # Проверяем, что ввели только цифры
            if not user_guess.isdigit():
                print("Нужно вводить только цифры!")
                continue
            
            # Проверяем, что все цифры разные
            has_duplicates = False
            for i in range(len(user_guess)):
                for j in range(i + 1, len(user_guess)):
                    if user_guess[i] == user_guess[j]:
                        has_duplicates = True
            
            if has_duplicates:
                print("Все цифры должны быть разными!")
                continue
            
            attempts += 1  # Увеличиваем счетчик попыток
            
            # Считаем коров (цифра на своем месте)
            cows = 0
            # Считаем быков (цифра есть в числе, но не на своем месте)
            bulls = 0
            
            # Проверяем каждую цифру
            for i in range(n):
                # Если цифра стоит на правильном месте - это корова
                if user_guess[i] == secret_number[i]:
                    cows += 1
                # Если цифра есть в загаданном числе, но не на своем месте - это бык
                elif user_guess[i] in secret_number:
                    bulls += 1
            
            # Показываем результат
            print(f"Коров: {cows}, Быков: {bulls}")
            
            # Если все цифры на своих местах - победа!
            if cows == n:
                print(f"Ура! Ты угадал за {attempts} попыток!")
                break
        
        # Обновляем статистику после игры
        games_count += 1
        all_attempts += attempts
        
        # Обновляем лучший результат
        if attempts < best_game:
            best_game = attempts
        
        # Обновляем худший результат
        if attempts > worst_game:
            worst_game = attempts
        
        # Считаем среднее количество попыток
        if games_count > 0:
            average_attempts = all_attempts / games_count
        else:
            average_attempts = 0
        
        # Показываем статистику
        print("\n=== Статистика ===")
        print(f"Всего игр: {games_count}")
        print(f"Лучшая игра: {best_game} попыток")
        print(f"Худшая игра: {worst_game} попыток")
        print(f"Среднее: {average_attempts:.1f} попыток")
        
        # Спрашиваем, хочет ли пользователь играть еще
        print("\nХочешь сыграть еще раз?")
        answer = input("Введи 'да' или 'нет': ").lower()
        
        if answer in ["да", "д", "yes", "y"]:
            print("\n" + "="*30)
            print("Начинаем новую игру!")
        else:
            print("Спасибо за игру! До свидания!")
            break

# Запускаем игру
if __name__ == "__main__":
    main()