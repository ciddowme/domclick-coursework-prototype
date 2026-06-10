# -*- coding: utf-8 -*-
"""Сборка клиентской версии прототипа «Домовой центр».

Из учебной версии (domclick_myhome_after_1to1.html) убираются все аннотации
для жюри/команды (бейджи «НОВОЕ», «Гипотеза…», внутренние метрики, «было/стало»),
тексты переписываются на клиентские, зелёная подсветка нового заменяется
нативным стилем карточек Домклик. Результат: domclick_myhome_client.html.

Запуск: /usr/bin/python3 make_client_version.py  (нужны bs4 + lxml)
"""
import sys

from bs4 import BeautifulSoup

SRC = "prototype/domclick_myhome_after_1to1.html"
DST = "prototype/domclick_myhome_client.html"

soup = BeautifulSoup(open(SRC, encoding="utf-8").read(), "lxml")

# ---------- 1. Удаляем учебные элементы ----------
def kill(*selectors):
    for sel in selectors:
        for el in soup.select(sel):
            el.decompose()

kill(
    ".coursework-static-note",          # плашка «Статичная учебная копия»
    ".oc-aside-card.oc-aside-logic",    # карточка «Логика первой версии»
    ".oc-real-badge",                   # бейдж «Новая вкладка внутри…»
    ".oc-after-eyebrow",                # «Гипотеза на основе исследования»
    ".oc-research",                     # внутренние метрики (942 тыс., 6 491…)
    ".oc-proof",                        # «Почему именно так…»
    ".oc-note",                         # «Вывод из исследования…»
    ".oc-mini-status",                  # «Нажмите на любую плашку — прототип покажет…»
    "#oc-flow-history",                 # секция «было/стало»
)
# кнопка «Почему это лучше» (вела на удалённую секцию)
for btn in soup.select('[data-oc-target="oc-flow-history"]'):
    btn.decompose()

# ---------- 2. Переписываем тексты на клиентские ----------
MISSES = []

def set_text(selector, old_substr, new_text):
    for el in soup.select(selector):
        if old_substr in el.get_text():
            el.string = new_text
            return True
    MISSES.append(f"{selector} :: {old_substr[:40]}")
    print(f"  !! не найдено: {selector} :: {old_substr[:40]}")
    return False

set_text(".oc-after-sub", "Решение - добавить",
         "Оплачивайте ЖКУ, передавайте показания и решайте бытовые вопросы — "
         "всё по вашему адресу и в пару касаний.")

set_text(".oc-section-label", "Ядро регулярного возврата", "улица Примерная, 10, кв. 1")
set_text(".oc-block-sub", "Блок выводит задачи",
         "Напомним о платежах, показаниях и сроках — и поможем закрыть всё сразу.")

set_text(".oc-section-label", "Контекстная монетизация", "Рекомендации для вашей квартиры")
set_text(".oc-block-sub", "Не холодная витрина",
         "Подсказываем услуги в нужный момент — адрес и параметры квартиры уже заполнены.")

set_text(".oc-section-label", "Сценарий: ЖКУ и показания", "ЖКУ и счётчики")
set_text(".oc-block-sub", "ЖКУ выбран как главный частотный",
         "Начисления, оплата и передача показаний — в одном месте, с напоминаниями каждый месяц.")

set_text(".oc-section-label", "Сценарий: бытовые задачи", "Бытовые услуги")
set_text(".oc-block-sub", "Мастер и клининг взяты",
         "Мастер на час, клининг и подготовка квартиры к сдаче — по вашему адресу.")

set_text(".oc-aside-text", "ЖКУ и показания дают регулярный вход",
         "Оплата, показания и важные сроки по вашей квартире — в одном месте.")

# контекстные подписи
set_text(".oc-context-item span", "Адрес и объект уже подставлены",
         "Выберите проблему и удобное время — адрес уже заполнен.")
set_text(".oc-action span", "Когда есть протечка, счетчики или поверка",
         "Протечки, смесители и поверка счётчиков")
set_text(".oc-action span", "Когда проблема привязана к конкретной квартире",
         "Розетки, освещение и проводка")

# служебный тег «триггер» → понятный клиенту
for em in soup.select("em.oc-tag"):
    if em.get_text(strip=True) == "триггер":
        em.string = "поверка"

# ---------- 3. Нативный стиль вместо «зелёной подсветки нового» ----------
override = soup.new_tag("style", id="oc-client-overrides")
override.string = """
/* Клиентская версия: нативные карточки Домклик вместо подсветки нового */
.oc-after-card.oc-proposed{border:1px solid #e7ece9;box-shadow:0 8px 24px rgba(23,33,43,.08);background:#fff;}
.oc-after-card.oc-proposed:after{content:none!important;}
.oc-aside-card{border:1px solid #e7ece9;box-shadow:0 8px 24px rgba(23,33,43,.08);background:#fff;}
.oc-aside-card:after{content:none!important;}
.oc-after-block.oc-proposed-block:after{content:none!important;}
.oc-after-block.oc-proposed-block{border:1px solid #e7ece9;background:#fff;}
.oc-after-head{margin-bottom:14px;}
/* мягкая нативная подсветка при переходе к сценарию вместо жирной зелёной рамки */
.oc-focus{outline:none!important;border:1px solid #21a038!important;background:#fff!important;
  box-shadow:0 0 0 1px #21a038, 0 8px 24px rgba(23,33,43,.08)!important;}
"""
soup.head.append(override)
# скролл к сценариям уже делает родной скрипт прототипа (openScenario + .oc-focus);
# свой слушатель не добавляем — родной перехватывает клики в capture-фазе.

# ---------- 5. Служебное: noindex + честный комментарий ----------
meta = soup.new_tag("meta")
meta.attrs["name"] = "robots"
meta.attrs["content"] = "noindex, nofollow"
soup.head.insert(0, meta)
from bs4 import Comment
soup.body.insert(0, Comment(
    " Учебный прототип курсового проекта ВШБ НИУ ВШЭ (команда 2). "
    "Не является сайтом domclick.ru. Демонстрация концепции «Домовой центр». "))

if MISSES:
    print(f"FAILED: {len(MISSES)} замен не нашли цель — файл не сохраняю")
    sys.exit(1)

open(DST, "w", encoding="utf-8").write(str(soup))
print("SAVED:", DST)
