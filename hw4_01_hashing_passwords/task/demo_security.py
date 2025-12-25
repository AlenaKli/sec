#!/usr/bin/env python3
import time
from user import InMemoryUserStorage
import auth
from config import config

def show_delay_calculations():
    print("=== Расчет задержек по формуле 1.5^n + 1 ===")
    for n in range(1, 6):
        delay = auth.calculate_delay(n)
        print(f"Попытка {n}: {delay:.2f} секунд")
    print()

def demonstrate_registration():
    print("=== 1. Регистрация пользователя ===")
    storage = InMemoryUserStorage()
    
    try:
        user = auth.register_user(
            storage, 
            "test_user", 
            "test@example.com", 
            "StrongPass123!"
        )
        print(f"✓ Создан пользователь: {user.username}")
        print(f"✓ Email: {user.email}")
        print(f"✓ Хеш начинается с: {user.password_hash[:20]}...")
        print(f"✓ Неудачных попыток: {user.failed_attempts}")
        print()
        return storage, user.username
    except ValueError as e:
        print(f"✗ Ошибка: {e}")
        return None, None

def demonstrate_failed_attempts(storage, username):
    print("=== 2. Демонстрация неудачных попыток ===")
    
    print("Симулируем 3 неудачные попытки входа:")
    start_time = time.time()
    
    for i in range(1, 4):
        print(f"\nПопытка {i}:")
        result = auth.verify_credentials(storage, username, f"wrong{i}")
        print(f"  Результат: {'Успех' if result else 'Неудача'}")
        
        user = auth.User.load(storage, username)
        if user:
            print(f"  Счетчик попыток: {user.failed_attempts}")
            print(f"  Текущая задержка: {user.backoff_seconds:.2f}с")
    
    total_time = time.time() - start_time
    print(f"\nОбщее время с задержками: {total_time:.2f} секунд")
    print()

def demonstrate_successful_login(storage, username):
    print("=== 3. Успешный вход ===")
    
    print("Попытка входа с правильным паролем:")
    result = auth.verify_credentials(storage, username, "StrongPass123!")
    
    if result:
        print("✓ Вход успешен!")
        user = auth.User.load(storage, username)
        print(f"✓ Счетчик попыток сброшен: {user.failed_attempts}")
        print(f"✓ Задержка обнулена: {user.backoff_seconds}")
    else:
        print("✗ Вход не удался")
    print()

def demonstrate_admin_function(storage, username):
    print("=== 4. Административная функция ===")
    
    print("Имитация сброса счетчика администратором:")
    success = auth.reset_failed_attempts(storage, username, admin="admin_user")
    
    if success:
        print("✓ Счетчик сброшен администратором")
    else:
        print("✗ Ошибка сброса")
    print()

def check_logs():
    print("=== 5. Проверка логов ===")
    import os
    if os.path.exists('logs'):
        log_files = os.listdir('logs')
        if log_files:
            latest = max([os.path.join('logs', f) for f in log_files], key=os.path.getmtime)
            print(f"✓ Логи созданы: {latest}")
            print("  Содержимое логов (первые 5 строк):")
            print("  " + "-"*40)
            try:
                with open(latest, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 5:
                            print(f"  {line.strip()}")
                        else:
                            break
            except:
                print("  Не удалось прочитать файл логов")
        else:
            print("✗ Файлы логов не найдены")
    else:
        print("✗ Папка logs не существует")
    print()

def main():
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ СИСТЕМЫ БЕЗОПАСНОСТИ (Вариант 4)")
    print("="*60 + "\n")
    
    show_delay_calculations()
    
    storage, username = demonstrate_registration()
    if not storage:
        return
    
    demonstrate_failed_attempts(storage, username)
    demonstrate_successful_login(storage, username)
    demonstrate_admin_function(storage, username)
    check_logs()
    
    print("="*60)
    print("Демонстрация завершена!")
    print("Проверьте папку 'logs/' для детального просмотра записей")
    print("="*60)

if __name__ == "__main__":
    main()