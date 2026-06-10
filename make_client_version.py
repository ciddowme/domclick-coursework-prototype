# -*- coding: utf-8 -*-
"""Сборка клиентской версии прототипа «Домовой центр» (вариант «Пульс дома»).

Из учебной версии (domclick_myhome_after_1to1.html) убираются аннотации,
страница перекомпоновывается под пользовательский флоу:
hero-агрегат (оценка квартиры, прогресс месяца, экономия) → лента задач
со статусами → рекомендации с причинами → история квартиры → «Сломалось дома».
Результат: domclick_myhome_client.html.

Запуск: /usr/bin/python3 make_client_version.py  (нужны bs4 + lxml)
"""
import sys

from bs4 import BeautifulSoup, Comment

SRC = "prototype/domclick_myhome_after_1to1.html"
DST = "prototype/domclick_myhome_client.html"

soup = BeautifulSoup(open(SRC, encoding="utf-8").read(), "lxml")

MISSES = []


def kill(*selectors):
    for sel in selectors:
        for el in soup.select(sel):
            el.decompose()


def frag(html):
    """Фрагмент → список тегов (html.parser не оборачивает в <html><body>)."""
    return list(BeautifulSoup(html, "html.parser").children)


def block_by_h3(substr):
    for b in soup.select(".oc-after-block"):
        h = b.find("h3")
        if h and substr in h.get_text():
            return b
    print(f"FAILED: не найден блок «{substr}»")
    sys.exit(1)


def must(selector, root=None):
    el = (root or soup).select_one(selector)
    if el is None:
        print(f"FAILED: не найден {selector}")
        sys.exit(1)
    return el


# ---------- 1. Удаляем учебные элементы ----------
kill(
    ".coursework-static-note",          # плашка «Статичная учебная копия»
    ".oc-aside-card.oc-aside-logic",    # карточка «Логика первой версии»
    ".oc-real-badge",                   # бейдж «Новая вкладка внутри…»
    ".oc-after-eyebrow",                # «Гипотеза на основе исследования»
    ".oc-research",                     # внутренние метрики
    ".oc-proof",                        # «Почему именно так…»
    ".oc-note",                         # «Вывод из исследования…»
    ".oc-mini-status",                  # подсказка про плашки
    "#oc-flow-history",                 # секция «было/стало»
    ".oc-actions",                      # ряд-дубль Сантехник/Электрик/Клининг
)
for btn in soup.select('[data-oc-target="oc-flow-history"]'):
    btn.decompose()

# ---------- 2. Aside: компактная карточка квартиры + нативные виджеты ----------
aside = must(".oc-aside-card")
must(".oc-aside-title", aside).string = "Ваша квартира"
must(".oc-aside-text", aside).string = "улица Примерная, 10, кв. 1 · 61,4 м² · 14/18 этаж"
must(".oc-aside-list", aside).decompose()
must(".oc-aside-link", aside).decompose()
for el in frag(
    '<div class="oc-sync">✓ Данные о квартире обновляются из СберБанк Онлайн</div>'):
    aside.append(el)
# виджеты колонки: страховка (текст родного виджета ДомКлик, вырезанного при
# санитизации) + документы, кредит под залог и дом — нативный набор раздела
aside.insert_after(*frag(
    '<div class="oc-aside-card oc-ins"><div class="oc-aside-kicker">Страхование</div>'
    '<h3 class="oc-aside-title">Защитите квартиру за 1 ₽</h3>'
    '<p class="oc-aside-text">Акция действует до 12 мая — первый месяц страховки за 1 ₽.</p>'
    '<em class="oc-cta oc-cta-light">Подробнее</em></div>'
    '<div class="oc-aside-card oc-ins"><div class="oc-aside-kicker">Документы</div>'
    '<h3 class="oc-aside-title">Архив квартиры — 12 файлов</h3>'
    '<p class="oc-aside-text">Выписка ЕГРН, акты мастеров, полис и договоры — в одном месте.</p>'
    '<em class="oc-cta oc-cta-light">Открыть архив</em></div>'
    '<div class="oc-aside-card oc-ins"><div class="oc-aside-kicker">Кредит</div>'
    '<h3 class="oc-aside-title">Кредит под залог квартиры</h3>'
    '<p class="oc-aside-text">До 7,4 млн ₽ под залог вашей квартиры — решение онлайн.</p>'
    '<em class="oc-cta oc-cta-light">Рассчитать</em></div>'
    '<div class="oc-aside-card oc-ins"><div class="oc-aside-kicker">Дом и район</div>'
    '<h3 class="oc-aside-title">Ваш дом: рейтинг 4,6</h3>'
    '<p class="oc-aside-text">Плановое отключение горячей воды 15–17 июня — напомним заранее.</p>'
    '<em class="oc-cta oc-cta-light">Все события дома</em></div>'))

# ---------- 3. Шапка: hero «Пульс дома» вместо сабтайтла-лендинга ----------
head = must(".oc-after-head")
sub = head.select_one(".oc-after-sub")
if sub:
    sub.decompose()
head.append(frag(
    '<div class="oc-pulse">'
    '<div class="oc-pulse-status"><i class="oc-dot"></i>С домом всё в порядке'
    '<span class="oc-pulse-addr">улица Примерная, 10, кв. 1</span></div>'
    '<div class="oc-pulse-grid">'
    '<div class="oc-pulse-tile"><span class="oc-pulse-label">Оценка квартиры</span>'
    '<b class="oc-pulse-num">9,24 млн ₽</b>'
    '<span class="oc-pulse-note oc-up">+312 000 ₽ за год (+3,5%)</span></div>'
    '<div class="oc-pulse-tile"><span class="oc-pulse-label">Май по дому</span>'
    '<b class="oc-pulse-num">1 из 3</b>'
    '<span class="oc-pulse-bar"><i style="width:33%"></i></span>'
    '<span class="oc-pulse-note">следующее — показания до 25 мая</span></div>'
    '<div class="oc-pulse-tile"><span class="oc-pulse-label">Сэкономлено с Домклик</span>'
    '<b class="oc-pulse-num">3 412 ₽</b>'
    '<span class="oc-pulse-note">за 2026 год · пеней 0 ₽</span></div>'
    '</div></div>')[0])

# ---------- 4. «Сегодня по дому»: статусы + три задачи с кнопками ----------
today = block_by_h3("Сегодня по дому")
today["id"] = "oc-block-today"
must(".oc-section-label", today).decompose()      # адрес теперь в hero
must(".oc-block-sub", today).string = "Напомним о платежах, показаниях и сроках — и поможем закрыть всё сразу."
btnrow = today.select_one(".oc-btnrow")
if btnrow:
    btnrow.decompose()
for t in today.select("button.oc-task"):
    t.decompose()
for el in frag(
    '<div class="oc-task oc-done"><div class="oc-ico">✓</div>'
    '<div><b>Показания за апрель переданы</b><span>3 мая · на 4 дня раньше срока</span></div>'
    '<em class="oc-done-mark">Готово</em></div>'
    '<div class="oc-task"><div class="oc-ico">₽</div>'
    '<div><b>ЖКУ за апрель — 7 840 ₽</b><span>−12% к марту · без задолженности</span></div>'
    '<em class="oc-cta">Оплатить</em></div>'
    '<div class="oc-task"><div class="oc-ico">💧</div>'
    '<div><b>Показания счётчиков</b><span>ХВС, ГВС и электричество · до 25 мая</span></div>'
    '<em class="oc-cta">Передать</em></div>'
    '<div class="oc-task"><div class="oc-ico">🛠</div>'
    '<div><b>Поверка счётчика ХВС</b><span>через 42 дня · напомним заранее</span></div>'
    '<em class="oc-cta">Записаться</em></div>'):
    today.append(el)

# ---------- 5. Рекомендации: причина → совет → выгода ----------
rec = block_by_h3("Сервисы из события")
must(".oc-section-label", rec).decompose()
must("h3", rec).string = "Рекомендации для вашей квартиры"
must(".oc-block-sub", rec).string = "Подсказываем в нужный момент — по событиям вашей квартиры."
ctx = must(".oc-context", rec)
ctx.clear()
for el in frag(
    '<button class="oc-context-item oc-clickable" data-oc-target="oc-flow-services" type="button">'
    '<div class="oc-why">Расход ГВС +18% к марту</div>'
    '<div><b>Проверьте смеситель</b><span>Возможна протечка · сантехник в четверг, от 1 200 ₽</span></div></button>'
    '<button class="oc-context-item oc-clickable" data-oc-target="oc-flow-services" type="button">'
    '<div class="oc-why">Поверка через 42 дня</div>'
    '<div><b>Запишитесь в мае</b><span>Слоты у мастеров в мае на 15% дешевле</span></div></button>'
    '<button class="oc-context-item oc-clickable" data-oc-target="oc-flow-services" type="button">'
    '<div class="oc-why">Вы смотрели раздел «Аренда»</div>'
    '<div><b>Сдайте квартиру с Домклик</b><span>Пакет подготовки 12 900 ₽ — окупается за 4 дня аренды</span></div></button>'):
    ctx.append(el)

# ---------- 6. «Оплата и показания» → «История квартиры» (актив, не дубль) ----------
hist = block_by_h3("Оплата и показания")
hist["id"] = "oc-history"
must(".oc-section-label", hist).string = "История квартиры"
must("h3", hist).string = "Паспорт квартиры заполнен на 80%"
must(".oc-block-sub", hist).string = "12 документов и актов в архиве — пригодятся при продаже или сдаче."
for t in hist.select("div.oc-task"):
    t.decompose()
for el in frag(
    '<div class="oc-tl">'
    '<div class="oc-tl-item"><span class="oc-tl-date">3 мая</span>'
    '<div><b>Показания переданы</b><span>12 месяцев подряд без пропусков</span></div></div>'
    '<div class="oc-tl-item"><span class="oc-tl-date">12 апр</span>'
    '<div><b>Поверка ГВС пройдена</b><span>акт мастера — в архиве квартиры</span></div></div>'
    '<div class="oc-tl-item"><span class="oc-tl-date">фев</span>'
    '<div><b>Замена смесителя</b><span>мастер Домклик · гарантия до 02.2027</span></div></div>'
    '<div class="oc-tl-item"><span class="oc-tl-date">янв</span>'
    '<div><b>Страховка продлена</b><span>полис действует до января 2027</span></div></div>'
    '</div>'):
    hist.append(el)

# ---------- 7. «Сломалось дома»: мастера + экстренный режим (по сценарию 4.5) ----------
svc = block_by_h3("Сломалось дома")
must(".oc-section-label", svc).string = "Бытовые услуги"
must(".oc-block-sub", svc).string = "Мастер по вашему адресу — параметры квартиры уже заполнены."
sctx = must(".oc-context", svc)
sctx.clear()
for el in frag(
    '<div class="oc-flow-item"><div class="oc-ico">💧</div>'
    '<div><b>Сантехник</b><span>Протечки, смесители, краны</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    '<div class="oc-flow-item"><div class="oc-ico">⚡</div>'
    '<div><b>Электрик</b><span>Розетки, освещение, проводка</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    '<div class="oc-flow-item"><div class="oc-ico">🧹</div>'
    '<div><b>Клининг</b><span>После ремонта, перед сдачей или регулярно</span></div>'
    '<em class="oc-cta">Заказать</em></div>'
    '<div class="oc-flow-item oc-sos"><div class="oc-ico">🚨</div>'
    '<div><b>Авария: прорыв трубы или замыкание</b>'
    '<span>Сразу соединим с дежурной службой и подскажем, как перекрыть воду</span></div>'
    '<em class="oc-cta oc-cta-sos">Позвонить</em></div>'):
    sctx.append(el)

# ---------- 8. CSS: нативный стиль + новые компоненты ----------
override = soup.new_tag("style", id="oc-client-overrides")
override.string = """
/* Клиентская версия: нативные карточки Домклик вместо подсветки нового */
.oc-after-card.oc-proposed{border:1px solid #e7ece9;box-shadow:0 8px 24px rgba(23,33,43,.08);background:#fff;}
.oc-after-card.oc-proposed:after{content:none!important;}
.oc-aside-card{border:1px solid #e7ece9;box-shadow:0 8px 24px rgba(23,33,43,.08);background:#fff;}
.oc-aside-card:after{content:none!important;}
.oc-after-block.oc-proposed-block:after{content:none!important;}
.oc-after-block.oc-proposed-block{border:1px solid #e7ece9;background:#fff;}
.oc-after-head{margin-bottom:14px;display:block!important;}
.oc-after-head h1,.oc-after-head h2{margin-bottom:10px;}
.oc-focus{outline:none!important;border:1px solid #21a038!important;background:#fff!important;
  box-shadow:0 0 0 1px #21a038, 0 8px 24px rgba(23,33,43,.08)!important;}
/* секции друг под другом во всю ширину — карточки не пляшут по высоте */
.oc-after-grid{grid-template-columns:1fr!important;}
/* лейблы секций: спокойный оверлайн */
.oc-section-label{background:transparent;color:#7b8a81;padding:0;border-radius:0;
  font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;}
/* hero «Пульс дома» */
.oc-pulse{margin-top:14px;}
.oc-pulse-status{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;color:#17212b;}
.oc-dot{width:10px;height:10px;border-radius:50%;background:#21a038;flex-shrink:0;}
.oc-pulse-addr{margin-left:auto;font-weight:400;font-size:13px;color:#7b8a81;}
.oc-pulse-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;}
.oc-pulse-tile{display:flex;flex-direction:column;gap:4px;background:#f7faf8;border:1px solid #edf1ef;
  border-radius:16px;padding:14px 16px;min-width:0;}
.oc-pulse-label{font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#7b8a81;}
.oc-pulse-num{font-size:22px;font-weight:800;color:#17212b;line-height:1.1;}
.oc-pulse-note{font-size:12px;color:#7b8a81;line-height:1.3;}
.oc-pulse-note.oc-up{color:#0b7f2a;font-weight:700;}
.oc-pulse-bar{display:block;height:6px;border-radius:3px;background:#e3ebe6;overflow:hidden;margin:2px 0;}
.oc-pulse-bar i{display:block;height:100%;background:#21a038;border-radius:3px;}
/* строки задач: жёсткая сетка иконка|текст|кнопка */
.oc-task{text-align:left;grid-template-columns:40px 1fr auto;}
.oc-task>div:nth-child(2){min-width:0;}
.oc-task b{font-size:14.5px;}
.oc-task span{font-size:12.5px;}
.oc-task.oc-done{background:#f7faf8;border-style:dashed;}
.oc-task.oc-done .oc-ico{background:#e8f6ec;color:#0b7f2a;font-weight:800;}
.oc-done-mark{font-style:normal;font-size:12.5px;font-weight:700;color:#0b7f2a;justify-self:end;}
/* кнопки действий */
em.oc-cta{font-style:normal;display:inline-flex;align-items:center;justify-content:center;
  height:34px;padding:0 14px;border-radius:10px;background:#21a038;color:#fff;
  font-weight:700;font-size:13px;white-space:nowrap;justify-self:end;flex-shrink:0;}
em.oc-cta-light{background:#e8f6ec;color:#0b7f2a;margin-top:10px;}
em.oc-cta-sos{background:#e54d42;}
/* рекомендации: бейдж-причина сверху, карточки равной структуры */
button.oc-context-item{display:flex;flex-direction:column;align-items:stretch;gap:8px;text-align:left;}
button.oc-context-item:after{content:none!important;}
.oc-why{align-self:flex-start;font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;
  color:#8a6d1f;background:#fdf3d7;border-radius:8px;padding:4px 8px;}
button.oc-context-item>div:nth-child(2){display:flex;flex-direction:column;gap:3px;}
button.oc-context-item b{font-size:14px;color:#17212b;}
button.oc-context-item span{font-size:12.5px;color:#7b8a81;line-height:1.35;}
/* услуги «Сломалось дома» */
.oc-flow-item{display:flex;gap:12px;align-items:center;background:#fff;
  border:1px solid #edf1ef;border-radius:16px;padding:13px;margin-top:10px;}
.oc-flow-item>div:nth-child(2){flex:1;min-width:0;display:flex;flex-direction:column;gap:2px;}
.oc-flow-item b{font-size:14px;color:#17212b;}
.oc-flow-item span{font-size:12.5px;color:#7b8a81;line-height:1.35;}
.oc-flow-item .oc-ico{width:40px;height:40px;border-radius:12px;background:#f2f7f4;
  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.oc-flow-item.oc-sos{background:#fdf2f1;border-color:#f6d9d6;}
.oc-flow-item.oc-sos .oc-ico{background:#fbe4e2;}
/* история-таймлайн */
.oc-tl{margin-top:12px;border-left:2px solid #e3ebe6;padding-left:14px;display:flex;flex-direction:column;gap:12px;}
.oc-tl-item{position:relative;display:flex;gap:12px;align-items:baseline;}
.oc-tl-item:before{content:'';position:absolute;left:-19px;top:4px;width:8px;height:8px;border-radius:50%;
  background:#21a038;border:2px solid #fff;}
.oc-tl-date{flex-shrink:0;width:52px;font-size:12px;font-weight:700;color:#7b8a81;}
.oc-tl-item>div{display:flex;flex-direction:column;gap:1px;}
.oc-tl-item b{font-size:14px;color:#17212b;}
.oc-tl-item span{font-size:12.5px;color:#7b8a81;}
/* aside */
.oc-sync{margin-top:12px;font-size:12.5px;color:#0b7f2a;background:#f0faf3;border-radius:10px;padding:8px 10px;}
.oc-aside-card.oc-ins{margin-top:8px;}
/* телефон: плитки пульса и всё прочее в столбец */
@media(max-width:1100px){
  .oc-pulse-grid{grid-template-columns:1fr;}
  .oc-pulse-addr{display:none;}
  .oc-task{grid-template-columns:40px 1fr auto;}
}
"""
soup.head.append(override)
# скролл к сценариям делает родной скрипт прототипа (openScenario + .oc-focus)

# ---------- 9. Служебное: noindex + честный комментарий ----------
meta = soup.new_tag("meta")
meta.attrs["name"] = "robots"
meta.attrs["content"] = "noindex, nofollow"
soup.head.insert(0, meta)
soup.body.insert(0, Comment(
    " Учебный прототип курсового проекта ВШБ НИУ ВШЭ (команда 2). "
    "Не является сайтом domclick.ru. Демонстрация концепции «Домовой центр». "
    "Все цифры — демонстрационные данные. "))

# ---------- 10. Контроль ----------
for ref in soup.select("[data-oc-target]"):
    t = ref.get("data-oc-target")
    if not soup.find(id=t):
        MISSES.append(f"dangling target: {t}")

if MISSES:
    print(f"FAILED: {len(MISSES)} проблем — файл не сохраняю")
    for m in MISSES:
        print("  -", m)
    sys.exit(1)

open(DST, "w", encoding="utf-8").write(str(soup))
print("SAVED:", DST)
