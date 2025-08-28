from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import sqlite3
import random

# Создание базы данных
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Таблица продуктов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT NOT NULL
        )
    """)

    # Таблица рецептов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipe_title TEXT NOT NULL,
            recipe_text TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Список продуктов", callback_data="products")],
        [InlineKeyboardButton("🍳 Рецепты", callback_data="recipes")],
        [InlineKeyboardButton("➕ Добавить продукт", callback_data="add_product")],
        [InlineKeyboardButton("📝 Добавить рецепт", callback_data="add_recipe")],
        [InlineKeyboardButton("📊 Мои данные", callback_data="my_data")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Я бот для людей с железодефицитной анемией.\n\nВыбери действие:",
        reply_markup=reply_markup,
    )

# Обработка нажатий кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":
        await products(query, context)
    elif query.data == "recipes":
        await recipes(query, context)
    elif query.data == "add_product":
        await add_product_start(query, context)
    elif query.data == "add_recipe":
        await add_recipe_start(query, context)
    elif query.data == "my_data":
        await my_data(query, context)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Доступные команды:\n"
        "• Помощь — справка\n"
        "• Список продуктов — разрешённые продукты\n"
        "• Рецепт — случайный рецепт\n"
        "• Добавить продукт — добавить свой продукт\n"
        "• Добавить рецепт — добавить свой рецепт\n"
        "• Мои данные — посмотреть свои данные"
    )
    await update.message.reply_text(text)

# Команда /products
async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products_list = [
        "Говядина (печёная, тушёная)",
        "Баранина",
        "Курица (грудка, филе)",
        "Свинина",
        "Фасоль",
        "Чечевица",
        "Шпинат",
        "Курага",
        "Инжир",
        "Морковь",
        "Яблоки",
        "Гранаты",
        "Семена тыквы",
        "Семена подсолнечника",
        "Сыр",
        "Яичный желток",
        "Сухие фрукты",
        "Творог",
    ]

    message = "Разрешённые продукты (богатые железом):\n\n"
    for product in products_list:
        message += f"• {product}\n"

    await update.message.reply_text(message)

# Команда /recipes
async def recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("recipes.txt", "r", encoding="utf-8") as file:
            content = file.read()
        
        # Исправленное разделение рецептов
        recipes = []
        current_recipe = ""
        
        for line in content.split('\n'):
            if line.strip() == '' and current_recipe.strip():
                recipes.append(current_recipe.strip())
                current_recipe = ""
            else:
                current_recipe += line + '\n'
        
        # Добавляем последний рецепт, если он есть
        if current_recipe.strip():
            recipes.append(current_recipe.strip())
        
        if not recipes:
            await update.message.reply_text("Рецепты не найдены.")
            return
        
        recipe = random.choice(recipes)
        await update.message.reply_text(recipe)
        
    except FileNotFoundError:
        await update.message.reply_text("Файл с рецептами не найден.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

# Начало добавления продукта
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши название продукта, который хочешь добавить:"
    )

# Сохранение продукта
async def add_product_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    product_name = update.message.text.strip()

    if not product_name:
        await update.message.reply_text("Пожалуйста, напиши название продукта.")
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO products (user_id, product_name) VALUES (?, ?)",
        (user_id, product_name),
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Продукт '{product_name}' добавлен в список!")

# Начало добавления рецепта
async def add_recipe_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши название рецепта:")

# Сохранение рецепта (часть 1)
async def add_recipe_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    title = update.message.text.strip()

    if not title:
        await update.message.reply_text("Пожалуйста, напиши название рецепта.")
        return

    # Сохраняем название и ждём текст
    context.user_data["recipe_title"] = title
    await update.message.reply_text(
        "Теперь напиши текст рецепта (ингредиенты и способ приготовления):"
    )

# Сохранение рецепта (часть 2)
async def add_recipe_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    recipe_text = update.message.text.strip()

    if not recipe_text:
        await update.message.reply_text("Пожалуйста, напиши текст рецепта.")
        return

    title = context.user_data.get("recipe_title")
    if not title:
        await update.message.reply_text("Ошибка: не указано название рецепта.")
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO recipes (user_id, recipe_title, recipe_text) VALUES (?, ?, ?)",
        (user_id, title, recipe_text),
    )
    conn.commit()
    conn.close()

    del context.user_data["recipe_title"]

    await update.message.reply_text(f"✅ Рецепт '{title}' добавлен!")

# Команда /my_data
async def my_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Получаем продукты
    cursor.execute("SELECT product_name FROM products WHERE user_id = ?", (user_id,))
    products = cursor.fetchall()

    # Получаем рецепты
    cursor.execute("SELECT recipe_title FROM recipes WHERE user_id = ?", (user_id,))
    recipes = cursor.fetchall()

    conn.close()

    message = "Твои данные:\n\n"

    if products:
        message += "Продукты:\n"
        for p in products:
            message += f"• {p[0]}\n"
    else:
        message += "Продукты: нет\n"

    if recipes:
        message += "\nРецепты:\n"
        for r in recipes:
            message += f"• {r[0]}\n"
    else:
        message += "\nРецепты: нет\n"

    await update.message.reply_text(message)

# Главная функция
def main():
    init_db()  # Инициализация базы данных

    app = (
        Application.builder()
        .token("8155218325:AAEsKVp-WgpaQPT9557pvl6Naf_lLE73bm4")
        .build()
    )

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add_product", add_product_start))
    app.add_handler(CommandHandler("add_recipe", add_recipe_start))
    app.add_handler(CommandHandler("my_data", my_data))
    
    # Обработчик кнопок
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запуск бота
    app.run_polling()

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь вводит текст, но не команду
    if "recipe_title" in context.user_data:
        await add_recipe_text_handler(update, context)
    else:
        await add_product_handler(update, context)

if __name__ == "__main__":
    main()
    