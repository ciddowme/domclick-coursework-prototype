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

set_text(".oc-block-sub", "Блок выводит задачи",
         "Напомним о платежах, показаниях и сроках — и поможем закрыть всё сразу.")

set_text(".oc-block-sub", "Не холодная витрина",
         "Подсказываем услуги в нужный момент — адрес и параметры квартиры уже заполнены.")

set_text(".oc-section-label", "Сценарий: ЖКУ и показания", "ЖКУ и счётчики")
set_text(".oc-block-sub", "ЖКУ выбран как главный частотный",
         "Начисления, оплата и передача показаний — в одном месте, с напоминаниями каждый месяц.")

set_text(".oc-section-label", "Сценарий: бытовые задачи", "Бытовые услуги")
set_text(".oc-block-sub", "Мастер и клининг взяты",
         "Мастер на час, клининг и подготовка квартиры к сдаче — по вашему адресу.")

# ---------- 3. Перекомпоновка: один источник задач, действие в каждой строке ----------
def frag(html):
    """Фрагмент → список тегов (html.parser не оборачивает в <html><body>)."""
    return list(BeautifulSoup(html, "html.parser").children)

def block_by_h3(substr):
    for b in soup.select(".oc-after-block"):
        h = b.find("h3")
        if h and substr in h.get_text():
            return b
    raise SystemExit(f"FAILED: не найден блок «{substr}»")

# 3.1 aside: вместо дубля списка задач — карточка квартиры со ссылкой на задачи
aside = soup.select_one(".oc-aside-card")
aside.select_one(".oc-aside-title").string = "Ваша квартира"
aside.select_one(".oc-aside-text").string = "улица Примерная, 10, кв. 1 · 61,4 м² · 14/18 этаж"
aside.select_one(".oc-aside-list").decompose()
alink = aside.select_one(".oc-aside-link")
alink.string = "3 задачи на май — открыть"
alink["data-oc-target"] = "oc-block-today"
alink["href"] = "#oc-block-today"

# 3.2 «Сегодня по дому»: адресный чип не нужен (адрес в карточке слева),
# у каждой задачи — своя кнопка действия, общий ряд кнопок убираем
today = block_by_h3("Сегодня по дому")
today["id"] = "oc-block-today"
today.select_one(".oc-section-label").decompose()
btnrow = today.select_one(".oc-btnrow")
if btnrow: btnrow.decompose()
CTA_BY_TASK = [("Передать показания", "Передать"),
               ("Оплатить ЖКУ", "Оплатить"),
               ("поверк", "Записаться")]
for t in today.select("button.oc-task"):
    tag = t.select_one("em.oc-tag")
    if tag: tag.decompose()
    txt = t.get_text()
    for needle, word in CTA_BY_TASK:
        if needle.lower() in txt.lower():
            t.append(frag(f'<em class="oc-cta">{word}</em>')[0])
            break
    if "поверк" in txt.lower():  # поверка — это про счётчики, ведём в блок ЖКУ
        t["data-oc-target"] = "oc-flow-jku"
        t.find("b").string = "Поверка счётчика ХВС"
        t.find("span").string = "Через 42 дня · запись к мастеру за пару минут"

# 3.3 «Сервисы из события» → «Рекомендации»; карточку-дубль поверки
# заменяем рекомендацией из события (рост расходов → умный дом)
rec = block_by_h3("Сервисы из события")
rec.select_one(".oc-section-label").decompose()
rec.find("h3").string = "Рекомендации для вашей квартиры"
items = rec.select(".oc-context-item")
items[0].select("b")[0].string = "Расходы за апрель"
items[0].select("span")[0].string = "Сравните с прошлым месяцем и включите автонапоминания."
ic1 = items[1].find("div")
ic1.string = "🛡"
items[1].select("b")[0].string = "Умный дом для квартиры"
items[1].select("span")[0].string = "Датчики протечки и умные счётчики — расходы под контролем."
items[1]["data-oc-target"] = "oc-flow-jku"

# 3.4 ряд «Сантехник/Электрик/Клининг» — дубль блока «Сломалось дома», убираем
soup.select_one(".oc-actions").decompose()

# 3.5 «Оплата и показания»: вместо процессных шагов — действия с кнопками
jkublk = block_by_h3("Оплата и показания")
for t in jkublk.select("div.oc-task"):
    t.decompose()
for el in frag(
    '<div class="oc-task"><div class="oc-ico">₽</div>'
    '<div><b>ЖКУ за апрель — 7 840 ₽</b><span>Начислено без задолженности · можно включить автоплатёж</span></div>'
    '<em class="oc-cta">Оплатить</em></div>'
    '<div class="oc-task"><div class="oc-ico">💧</div>'
    '<div><b>Показания: вода и электричество</b><span>До 25 мая · напомним за три дня до срока</span></div>'
    '<em class="oc-cta">Передать</em></div>'
    '<div class="oc-task"><div class="oc-ico">🛠</div>'
    '<div><b>Поверка счётчика ХВС</b><span>Через 42 дня · проверенные мастера с гарантией</span></div>'
    '<em class="oc-cta">Записаться</em></div>'):
    jkublk.append(el)

# 3.6 «Сломалось дома»: каталог из четырёх услуг, у каждой — кнопка
svc = block_by_h3("Сломалось дома")
ctx = svc.select_one(".oc-context")
ctx.clear()
for el in frag(
    '<div class="oc-flow-item"><div class="oc-ico">💧</div>'
    '<div><b>Сантехник</b><span>Протечки, смесители и поверка — адрес уже заполнен</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    '<div class="oc-flow-item"><div class="oc-ico">⚡</div>'
    '<div><b>Электрик</b><span>Розетки, освещение и проводка</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    '<div class="oc-flow-item"><div class="oc-ico">🧹</div>'
    '<div><b>Клининг</b><span>После ремонта, перед сдачей или регулярная уборка</span></div>'
    '<em class="oc-cta">Заказать</em></div>'
    '<div class="oc-flow-item"><div class="oc-ico">🏠</div>'
    '<div><b>Подготовить к сдаче</b><span>Клининг, мелкий ремонт, фото и договор — одним пакетом</span></div>'
    '<em class="oc-cta">Собрать пакет</em></div>'):
    ctx.append(el)

# ---------- 4. Нативный стиль вместо «зелёной подсветки нового» ----------
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
/* лейблы нижних секций: спокойный оверлайн вместо псевдокнопки-чипа */
.oc-section-label{background:transparent;color:#7b8a81;padding:0;border-radius:0;
  font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;}
/* текст задач — слева (дефолт button центрирует) */
.oc-task{text-align:left;}
.oc-task>div:nth-child(2){min-width:0;}
/* кнопка действия в строке задачи/услуги */
em.oc-cta{font-style:normal;display:inline-flex;align-items:center;justify-content:center;
  height:34px;padding:0 14px;border-radius:10px;background:#21a038;color:#fff;
  font-weight:700;font-size:13px;white-space:nowrap;justify-self:end;flex-shrink:0;}
button.oc-task:hover em.oc-cta{background:#1b8a30;}
/* карточка услуги в «Сломалось дома» */
.oc-flow-item{display:flex;gap:12px;align-items:center;background:#fff;
  border:1px solid #edf1ef;border-radius:16px;padding:13px;margin-top:10px;}
.oc-flow-item>div:nth-child(2){flex:1;min-width:0;display:flex;flex-direction:column;gap:2px;}
.oc-flow-item b{font-size:14px;color:#17212b;}
.oc-flow-item span{font-size:12.5px;color:#7b8a81;line-height:1.35;}
.oc-flow-item .oc-ico{width:40px;height:40px;border-radius:12px;background:#f2f7f4;
  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
/* рекомендация: стрелка-аффорданс перехода */
button.oc-context-item{align-items:center;}
button.oc-context-item:after{content:'→';margin-left:auto;color:#21a038;font-weight:800;font-size:16px;}
/* кнопка-ссылка в карточке квартиры */
.oc-aside-link{display:inline-flex;align-items:center;justify-content:center;width:100%;
  height:44px;border-radius:14px;background:#21a038;color:#fff!important;font-weight:700;
  font-size:14px;text-decoration:none;margin-top:12px;}
/* на узких окнах родная media-query сжимает грид задач — вернуть колонку кнопки */
@media(max-width:900px){.oc-task{grid-template-columns:40px 1fr auto;}}
/* телефон (виртуальный вьюпорт ~980): блоки в одну колонку, задачи во всю ширину */
@media(max-width:1100px){.oc-after-grid{grid-template-columns:1fr!important;}}
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
