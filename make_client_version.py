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


# единый набор иконок (тонкий штрих 1.8, currentColor) вместо эмодзи
_ICON_PATHS = {
    "drop":  '<path d="M12 3.5c3.3 4 5.7 6.8 5.7 9.5a5.7 5.7 0 1 1-11.4 0c0-2.7 2.4-5.5 5.7-9.5z"/>',
    "tool":  '<path d="M14.7 6.3a4.2 4.2 0 0 0-5.6 5.6L4 17v3h3l5.1-5.1a4.2 4.2 0 0 0 5.6-5.6L15 12 12 9l2.7-2.7z"/>',
    "check": '<path d="M20 6.5 9.5 17 4 11.5"/>',
    "bolt":  '<path d="M13 2.5 4 14h7l-1 7.5L19 10h-7l1-7.5z"/>',
    "spark": '<path d="M12 3.5l1.7 4.6 4.6 1.7-4.6 1.7L12 16l-1.7-4.5-4.6-1.7 4.6-1.7L12 3.5z"/>',
    "alert": '<path d="M10.3 4.3 2.5 18a2 2 0 0 0 1.7 3h15.6a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0z"/>'
             '<path d="M12 9.5v4.5"/><path d="M12 17.5h.01"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round">' + _ICON_PATHS[name] + '</svg>')


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
    '<em class="oc-cta oc-cta-light">Открыть архив</em></div>'))

# ---------- 2.5. Мобильная шапка-замена (родная topline не адаптивна) ----------
native_header = must("header.tpln-main-topline--12-2-0")
native_header.insert_before(*frag(
    '<div class="oc-mhead"><img class="oc-mhead-logo" src="../Основное_files/domclick-logo.svg" alt="Домклик"/>'
    '<span class="oc-mhead-sub">Моя недвижимость</span></div>'))

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
    '<div class="oc-pulse-tile"><span class="oc-pulse-label">Экономия за год</span>'
    '<b class="oc-pulse-num">3 412 ₽</b>'
    '<span class="oc-pulse-note">автоплатёж и скидки мастеров</span></div>'
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
    f'<div class="oc-task oc-done"><div class="oc-ico">{icon("check")}</div>'
    '<div><b>Показания за апрель переданы</b><span>3 мая · на 4 дня раньше срока</span></div>'
    '<em class="oc-done-mark">Готово</em></div>'
    '<div class="oc-task"><div class="oc-ico oc-ico-rub">₽</div>'
    '<div><b>ЖКУ за апрель — 7 840 ₽</b><span>−12% к марту · без задолженности</span></div>'
    '<em class="oc-cta">Оплатить</em></div>'
    f'<div class="oc-task"><div class="oc-ico">{icon("drop")}</div>'
    '<div><b>Показания счётчиков</b><span>ХВС, ГВС и электричество · до 25 мая</span></div>'
    '<em class="oc-cta">Передать</em></div>'
    f'<div class="oc-task"><div class="oc-ico">{icon("tool")}</div>'
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
must(".oc-section-label", hist).decompose()
must("h3", hist).string = "История квартиры"
must(".oc-block-sub", hist).string = "Паспорт квартиры заполнен на 80% — 12 документов и актов пригодятся при продаже или сдаче."
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
must(".oc-section-label", svc).decompose()
must(".oc-block-sub", svc).string = "Мастер по вашему адресу — параметры квартиры уже заполнены."
sctx = must(".oc-context", svc)
sctx.clear()
for el in frag(
    f'<div class="oc-flow-item"><div class="oc-ico">{icon("drop")}</div>'
    '<div><b>Сантехник</b><span>Протечки, смесители, краны</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    f'<div class="oc-flow-item"><div class="oc-ico">{icon("bolt")}</div>'
    '<div><b>Электрик</b><span>Розетки, освещение, проводка</span></div>'
    '<em class="oc-cta">Выбрать время</em></div>'
    f'<div class="oc-flow-item"><div class="oc-ico">{icon("spark")}</div>'
    '<div><b>Клининг</b><span>После ремонта, перед сдачей или регулярно</span></div>'
    '<em class="oc-cta">Заказать</em></div>'
    f'<div class="oc-flow-item oc-sos"><div class="oc-ico">{icon("alert")}</div>'
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
.oc-task{text-align:left;grid-template-columns:40px 1fr auto;border-radius:14px;}
.oc-task>div:nth-child(2){min-width:0;}
.oc-task b{font-size:14.5px;}
.oc-task span{font-size:12.5px;}
.oc-task.oc-done{background:#f7faf8;border-color:#edf3ef;}
.oc-task.oc-done .oc-ico{background:#e8f6ec;color:#0b7f2a;}
.oc-ico{color:#1e9e3e;}
.oc-ico svg{width:20px;height:20px;display:block;}
.oc-ico-rub{font-weight:700;font-size:16px;}
.oc-done-mark{font-style:normal;font-size:12.5px;font-weight:700;color:#0b7f2a;justify-self:end;}
/* кнопки действий */
em.oc-cta{font-style:normal;display:inline-flex;align-items:center;justify-content:center;
  height:34px;padding:0 14px;border-radius:12px;background:#21a038;color:#fff;min-width:118px;
  font-weight:700;font-size:13px;white-space:nowrap;justify-self:end;flex-shrink:0;}
em.oc-cta-light{background:#e8f6ec;color:#0b7f2a;margin-top:10px;}
em.oc-cta-sos{background:#e54d42;}
/* рекомендации: бейдж-причина сверху, карточки равной структуры */
button.oc-context-item{display:flex;flex-direction:column;align-items:stretch;gap:8px;text-align:left;}
button.oc-context-item:after{content:none!important;}
.oc-why{align-self:flex-start;font-size:12px;font-weight:700;
  color:#8a6d1f;background:#fdf6e3;border-radius:8px;padding:4px 10px;}
button.oc-context-item>div:nth-child(2){display:flex;flex-direction:column;gap:3px;}
button.oc-context-item b{font-size:14px;color:#17212b;}
button.oc-context-item span{font-size:12.5px;color:#7b8a81;line-height:1.35;}
/* услуги «Сломалось дома» */
.oc-flow-item{display:flex;gap:12px;align-items:center;background:#fff;
  border:1px solid #edf1ef;border-radius:14px;padding:13px;margin-top:10px;}
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
/* aside: липкая колонка — при скролле виджеты остаются на экране */
.Xaae9{position:sticky;top:16px;align-self:flex-start;}
.oc-sync{margin-top:12px;font-size:12.5px;color:#0b7f2a;background:#f0faf3;border-radius:10px;padding:8px 10px;}
.oc-aside-card.oc-ins{margin-top:8px;}
/* телефон: плитки пульса и всё прочее в столбец */
@media(max-width:1100px){
  .oc-pulse-grid{grid-template-columns:1fr;}
  .oc-pulse-addr{display:none;}
  .oc-task{grid-template-columns:40px 1fr auto;}
}
/* наша мобильная шапка: на десктопе скрыта */
.oc-mhead{display:none;}
/* мобильная вёрстка: родную desktop-шапку и фото-обложку прячем, кнопки во всю ширину */
@media(max-width:760px){
  header.tpln-main-topline--12-2-0{display:none!important;}
  .oc-mhead{display:flex;align-items:center;gap:10px;padding:12px 16px;
    background:#fff;border-bottom:1px solid #edf1ef;}
  .oc-mhead-logo{height:26px;width:auto;display:block;}
  .oc-mhead-sub{font-size:13px;color:#7b8a81;}
  .hklFO{display:none!important;}
  /* декоративные тёмные уголки табов (рассчитаны на фото-подложку) */
  .S294i::before,.S294i::after,nav.z2DlB::before,nav.z2DlB::after,
  .tabs-tabs-d69-16-1-0::before,.tabs-tabs-d69-16-1-0::after,
  [class*="tabs-head"]::before,[class*="tabs-head"]::after{display:none!important;content:none!important;}
  .S294i,nav.z2DlB,.tabs-tabs-d69-16-1-0,[class*="tabs-head"]{
    border-radius:0!important;background:#fff!important;box-shadow:none!important;}
  /* колонки aside+main складываем в столбец */
  .f7T8t{display:block!important;}
  .Xaae9{position:static!important;width:100%!important;max-width:none!important;}
  .f7T8t>div{width:100%!important;max-width:none!important;}
  main.EMAJl{padding-left:12px!important;padding-right:12px!important;}
  /* табы: горизонтальная прокрутка вместо переноса */
  .tabs-buttons-fc1-16-1-0{overflow-x:auto;flex-wrap:nowrap!important;white-space:nowrap;
    scrollbar-width:none;-webkit-overflow-scrolling:touch;}
  .tabs-buttons-fc1-16-1-0::-webkit-scrollbar{display:none;}
  /* наш слой: воздух и читаемость */
  .oc-after-head h1,.oc-after-head h2{font-size:24px;}
  .oc-pulse-num{font-size:20px;}
  .oc-pulse-status{font-size:14px;}
  /* задачи: текст во всю ширину, кнопка отдельной строкой */
  .oc-task{grid-template-columns:40px 1fr;}
  .oc-task em.oc-cta{grid-column:1/-1;width:100%;margin-top:10px;height:40px;}
  .oc-task.oc-done{grid-template-columns:40px 1fr auto;}
  /* услуги аналогично */
  .oc-flow-item{flex-wrap:wrap;}
  .oc-flow-item em.oc-cta{width:100%;margin-top:10px;height:40px;}
  /* рекомендации и карточки — компактнее */
  button.oc-context-item{padding:12px;}
  .oc-tl-date{width:46px;font-size:11px;}
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
