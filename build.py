# -*- coding: utf-8 -*-
"""Генерує два дизайни сайту Sunny: /a (Ранок) і /b (Полудень) + сторінку вибору."""
import os, json, html, shutil
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
e = html.escape

PAGES = [  # slug, назва в меню, заголовок, підзаголовок
    ('index', 'Головна', '', ''),
    ('catalog', 'Каталог', 'Каталог продукції', 'Внутрішній і зовнішній сонцезахист: системи, тканини, автоматика та комплектація.'),
    ('about', 'Про компанію', 'Про компанію', SLOGAN),
    ('works', 'Наші роботи', 'Наші роботи', 'Реалізовані проєкти внутрішнього та зовнішнього сонцезахисту.'),
    ('dealers', 'Дилерам', 'Дилерам', 'Умови співпраці, каталоги тканин, рекламна підтримка та корисні матеріали.'),
    ('reviews', 'Відгуки', 'Відгуки клієнтів', 'Що кажуть про нас ті, хто вже обрав Sunny.'),
    ('faq', 'Питання-відповідь', 'Питання-відповідь', 'Відповіді на найчастіші запитання про штори, тканини та системи.'),
    ('contacts', 'Контакти', 'Контакти', 'Оптовий відділ і салони-партнери по всій Україні.'),
    ('news', 'Новини', 'Новини', f'Новинки колекції, зміни асортименту та події компанії — {NEWS_TOTAL} публікацій.'),
    ('stock', 'Акції', 'Акції', 'Актуальні знижки та спеціальні пропозиції.'),
    ('articles', 'Статті', 'Статті', f'Поради з вибору та догляду — {ARTICLES_TOTAL} статей від експертів Sunny.'),
    ('certificates', 'Сертифікати', 'Сертифікати', 'Сертифікати постачальників і документи відповідності нашої продукції.'),
]
MAIN_NAV = ['catalog', 'about', 'works', 'dealers', 'reviews', 'faq', 'contacts']
SUB_NAV = ['news', 'stock', 'articles', 'certificates']
P = {p[0]: p for p in PAGES}
href = lambda s: 'index.html' if s == 'index' else s + '.html'
tel = lambda p: 'tel:+' + ''.join(c for c in p if c.isdigit())

SUN_SVG = '<svg class="sun" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="9" fill="#FFC21A"/><g stroke="#FF8A1F" stroke-width="3" stroke-linecap="round"><path d="M20 3v5M20 32v5M3 20h5M32 20h5M8 8l3.5 3.5M28.5 28.5L32 32M8 32l3.5-3.5M28.5 11.5L32 8"/></g></svg>'
LOGO = f'<a class="logo" href="index.html">{SUN_SVG}<span>SUNNY</span></a>'

# ---------------- спільні блоки ----------------
def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11: return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return few
    return many

def cat_cards(items, base):
    out = []
    for n, c, i, slug in items:
        cnt = f'{c} тканин' if n == 'Каталог тканин' else f'{c} {plural(c, "позиція", "позиції", "позицій")}'
        out.append(f'<a class="card" href="{base}{slug}" target="_blank" rel="noopener"><div class="media"><img loading="lazy" src="{img(i)}" alt=""></div><div class="cbody"><h3>{e(n)}</h3><span class="count">{cnt}</span></div></a>')
    return '<div class="cards">' + ''.join(out) + '</div>'

def posts(items):
    return '<div class="posts">' + ''.join(
        f'<a class="post" href="{p["href"]}" target="_blank" rel="noopener"><div class="media"><img loading="lazy" src="{p["img"]}" alt=""></div><div class="pbody"><time>{p["date"]}</time><h3>{e(p["title"])}</h3></div></a>'
        for p in items) + '</div>'

def reviews(items):
    return '<div class="reviews">' + ''.join(
        f'<figure class="review"><div class="stars" aria-label="5 з 5">★★★★★</div><blockquote>{e(t)}</blockquote><figcaption><span class="ava">{e(n[0])}</span><b>{e(n)}</b><time>{d}</time></figcaption></figure>'
        for n, d, t in items) + '</div>'

def faq(items):
    return '<div class="faq">' + ''.join(
        f'<details{" open" if k == 0 else ""}><summary><span>{e(q)}</span><i></i></summary><p>{e(a)}</p></details>' for k, (q, a) in enumerate(items)) + '</div>'

def partners():
    return '<div class="partners">' + ''.join(f'<span title="{e(n)}"><img loading="lazy" src="{u}" alt="{e(n)}"></span>' for n, u in PARTNERS) + '</div>'

def stats():
    return '<div class="stats">' + ''.join(f'<div class="stat"><b>{a}</b><span>{e(b)}</span></div>' for a, b in STATS) + '</div>'

def form(title, fields, button, note='* Всі поля обов\'язкові для заповнення', cls=''):
    f = []
    for kind, label in fields:
        if kind == 'textarea':
            f.append(f'<label class="full"><span>{label}</span><textarea required></textarea></label>')
        else:
            f.append(f'<label><span>{label}</span><input type="{kind}" required></label>')
    return f'<form class="form {cls}" data-demo><h3>{title}</h3><div class="fields">{"".join(f)}</div><div class="fend"><small>{note}</small><button class="btn">{button}</button></div><p class="ok" hidden>Дякуємо! Це демо-версія дизайну — форма нічого не надсилає.</p></form>'

COOP_FORM = lambda: form('Заявка на співпрацю', [('text', 'ПІБ'), ('email', 'E-mail'), ('textarea', 'Текст заявки')], 'Відправити')

def calc():
    return '''<form class="calc" data-calc><h3>Розрахунок вартості</h3>
<label class="full"><span>Тип виробу</span><select required><option value="">— Виберіть тип виробу —</option><option>Рулонні штори</option><option>Захисні штори</option><option>Воротні системи</option></select></label>
<label><span>Ширина, см</span><input type="number" min="10" max="1000" required></label>
<label><span>Висота, см</span><input type="number" min="10" max="1000" required></label>
<button class="btn">Розрахувати вартість</button>
<p class="out" hidden></p></form>'''

def services():
    rows = [('📏', 'Виклик замірника', 'Майстер приїде, зробить точні заміри та підкаже систему.'),
            ('📞', 'Зворотний дзвінок', 'Залиште номер — менеджер передзвонить у робочий час.'),
            ('🧮', 'Розрахунок вартості', 'Вкажіть тип виробу та розміри — підготуємо прорахунок.')]
    return '<div class="services">' + ''.join(f'<a class="service" href="#svc" data-open="{k}"><span class="ico">{i}</span><b>{t}</b><span>{d}</span></a>' for k, (i, t, d) in enumerate(rows)) + '</div>'

def svc_modal():
    return f'''<dialog class="modal" id="svc"><button class="x" aria-label="Закрити" data-close>×</button>
<div class="mpanel" data-panel="0">{form('Виклик замірника', [('text', "Ім'я"), ('tel', 'Телефон'), ('text', 'Місто, адреса')], 'Відправити', '')}</div>
<div class="mpanel" data-panel="1">{form('Зворотний дзвінок', [('text', "Ім'я"), ('tel', 'Телефон')], 'Передзвоніть мені', '')}</div>
<div class="mpanel" data-panel="2">{calc()}</div></dialog>'''

# ---------------- тіла сторінок ----------------
def sec(title, body, kicker='', cls='', more='', id_=''):
    k = f'<span class="kicker">{kicker}</span>' if kicker else ''
    m = f'<a class="more" href="{more[1]}">{more[0]} →</a>' if more else ''
    i = f' id="{id_}"' if id_ else ''
    return f'<section class="sec {cls}"{i}><div class="wrap"><div class="sec-head"><div>{k}<h2>{title}</h2></div>{m}</div>{body}</div></section>'

def body_catalog():
    return (sec('Внутрішній сонцезахист', '<p class="lead">Цікаві інтер\'єрні рішення. Величезний вибір систем і тканин: рулонні та римські штори, День-Ніч, плісе та багато іншого.</p>' + cat_cards(INSIDE, INSIDE_URL), 'Для дому та офісу', id_='inside')
            + sec('Зовнішній сонцезахист', '<p class="lead">Захист від сонця, вітру й опадів, оригінальне оформлення фасаду, тераси чи кафе. Ручне або автоматичне керування.</p>' + cat_cards(OUTSIDE, OUTSIDE_URL), 'Для терас і фасадів', 'alt', id_='outside')
            + sec('Що обрати', '<div class="types">' + ''.join(f'<div class="type"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in PRODUCT_TYPES) + '</div>', 'Основні види продукції'))

def body_about():
    intro = '<div class="split"><div class="prose">' + ''.join(f'<p>{e(p)}</p>' for p in ABOUT_INTRO) + '</div><div class="photo"><img src="' + img('image/catalog/oKomp3int.jpg') + '" alt=""></div></div>'
    tasks = '<ol class="tasks">' + ''.join(f'<li>{e(t)}</li>' for t in TASKS) + '</ol><p class="note">Ми будуємо довготривалі партнерські відносини для спільного розвитку бізнесу!</p>'
    adv = '<div class="adv">' + ''.join(f'<div class="advi"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in ADVANTAGES) + '</div>'
    return (sec('Хто ми', intro, 'Команда однодумців') + sec('Основні завдання ТМ Sunny', tasks, '', 'alt')
            + sec('Переваги ТМ Sunny', adv) + sec('Наші партнери', partners(), 'Світові виробники', 'alt')
            + sec('Ми відкриті для співпраці', services()))

def body_works():
    cards = '<div class="works">' + ''.join(f'<a class="work" href="{u}" target="_blank" rel="noopener"><div class="media"><img loading="lazy" src="{i}" alt=""></div><div class="wbody"><h3>{e(t)}</h3><p>{e(d)}</p><span class="more">Дивитись галерею →</span></div></a>' for t, d, i, u in WORKS) + '</div>'
    gal = '<div class="gallery">' + ''.join(f'<img loading="lazy" src="{u}" alt="">' for u in GALLERY) + '</div>'
    return sec('Галереї проєктів', cards) + sec('Натхнення', gal, 'З наших робіт', 'alt') + sec('Хочете так само?', services())

def body_dealers():
    terms = '<div class="terms">' + ''.join(f'<div class="term"><span class="n">{k+1:02d}</span><h3>{e(t)}</h3><ul>' + ''.join(f'<li>{e(x)}</li>' for x in li) + '</ul></div>' for k, (t, li) in enumerate(DEALER_TERMS)) + '</div>'
    docs = '<div class="docs">' + ''.join(f'<a class="doc" href="{u}" target="_blank" rel="noopener"><span class="ext">{u.rsplit(".",1)[-1][:4].upper() if "." in u.rsplit("/",1)[-1] else "WEB"}</span>{e(n)}</a>' for n, u in DEALER_DOCS + DEALER_CATALOGS + DEALER_USEFUL) + '</div>'
    promo = '<div class="promo">' + ''.join(f'<img loading="lazy" src="{u}" alt="">' for u in DEALER_PROMO) + '</div><p class="note">Макет рекламних матеріалів розробляємо за індивідуальними побажаннями кожного клієнта.</p>'
    return (sec('Умови співпраці', terms) + sec('Каталоги тканин та документи', docs, 'Завантажити', 'alt')
            + sec('Рекламна продукція', promo, 'Стенди, каталоги, листівки') + sec('Наші партнери', partners(), '', 'alt')
            + sec('Стати дилером', COOP_FORM()))

def body_reviews():
    return sec('Відгуки', reviews(REVIEWS)) + sec('Залишити відгук', form('Ваш відгук', [('text', "Ім'я"), ('email', 'E-mail'), ('textarea', 'Відгук')], 'Надіслати відгук'), '', 'alt')

def body_faq():
    return sec('Часті запитання', faq(FAQ)) + sec('Не знайшли відповідь?', form('Задайте своє питання', [('text', 'ПІБ'), ('email', 'E-mail'), ('textarea', 'Ваше питання')], 'Відправити'), '', 'alt')

def body_contacts():
    opt = f'''<div class="opt">
<div class="optc main"><span class="lbl">Оптовий відділ · телефони</span>{''.join(f'<a class="bigtel" href="{tel(p)}">{p}</a>' for p in PHONES)}</div>
<div class="optc"><span class="lbl">Графік роботи</span><b class="big">9:00 — 18:00</b><div class="days"><i>Пн</i><i>Вт</i><i>Ср</i><i>Чт</i><i>Пт</i><i class="off">Сб</i><i class="off">Нд</i></div><small>Субота, неділя — вихідні</small></div>
<div class="optc"><span class="lbl">Email</span><a class="mail" href="mailto:{EMAIL}">{EMAIL}</a><span class="lbl" style="margin-top:18px">Сайт</span><span class="mail">sunny-tm.com</span></div></div>'''
    nshops = sum(len(p['s']) for r in SHOPS for p in r['p'])
    shops = f'''<div class="finder" data-finder><div class="ftools"><input type="search" placeholder="Місто, салон або вулиця…" aria-label="Пошук"><select aria-label="Область"><option value="">Усі області ({nshops})</option>{''.join(f'<option>{e(r["r"])}</option>' for r in SHOPS)}</select></div><div class="flist"></div></div>
<script>window.SHOPS={json.dumps(SHOPS, ensure_ascii=False)};</script>'''
    return sec('Контакти для оптових клієнтів', opt) + sec('Де купити вроздріб', shops, f'{len(SHOPS)} областей · {nshops} точок', 'alt') + sec('Заявка на співпрацю', COOP_FORM())

def body_posts(items, total, url):
    return sec('Останні публікації', posts(items) + f'<p class="note">Показано {len(items)} з {total}. <a href="{url}" target="_blank" rel="noopener">Архів на sunny-tm.com →</a></p>')

def body_certs():
    c = '<div class="certs">' + ''.join(f'<a class="cert" href="{big}" target="_blank" rel="noopener"><span class="media"><img loading="lazy" src="{sm}" alt=""></span><span>{e(n)}</span></a>' for n, sm, big in CERTS) + '</div>'
    return sec('Документи', c)

def body_home():
    cats = '<div class="duo">' + ''.join(f'<a class="duoc" href="catalog.html#{a}"><img loading="lazy" src="{i}" alt=""><div><span class="kicker">{k}</span><h3>{t}</h3><p>{d}</p><span class="more">Детальніше →</span></div></a>' for a, i, k, t, d in [
        ('inside', img(INSIDE[1][2]), '100+ систем', 'Внутрішній сонцезахист', "Цікаві інтер'єрні рішення. Рулонні, римські штори, День-Ніч, плісе та багато іншого."),
        ('outside', img(OUTSIDE[0][2]), 'ZIP · Refleksol · маркізи', 'Зовнішній сонцезахист', 'Захист терас, кафе та фасадів від сонця, вітру й опадів.')]) + '</div>'
    types = '<div class="types">' + ''.join(f'<div class="type"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in PRODUCT_TYPES) + '</div>'
    return (sec('Каталог продукції', cats, 'Для дому, офісу та терас', '', ('Весь каталог', 'catalog.html'))
            + sec('Чому Sunny', stats() + types, 'TM SUNNY — один з лідерів галузі сонцезахисту України', 'alt')
            + sec('Відгуки клієнтів', reviews(REVIEWS[:3]), '', '', ('Всі відгуки', 'reviews.html'))
            + sec('Новини', posts(NEWS[:3]), 'Свіже з колекції', 'alt', ('Всі новини', 'news.html'))
            + sec('Сервіс', services(), 'Почніть з простого')
            + sec('Наші партнери', partners(), 'Тканини та комплектуючі провідних світових виробників', 'alt'))

BODIES = {'catalog': body_catalog, 'about': body_about, 'works': body_works, 'dealers': body_dealers, 'reviews': body_reviews,
          'faq': body_faq, 'contacts': body_contacts, 'certificates': body_certs,
          'news': lambda: body_posts(NEWS, NEWS_TOTAL, S + '/uk/blog-headlines/news'),
          'stock': lambda: body_posts(STOCK, len(STOCK), S + '/uk/blog-headlines/stock'),
          'articles': lambda: body_posts(ARTICLES, ARTICLES_TOTAL, S + '/uk/blog-headlines/articles'),
          'index': body_home}

# ---------------- оболонки дизайнів ----------------
HEAD = lambda title, theme, fonts: f'''<!doctype html><html lang="uk" data-theme="{theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="TM SUNNY — рулонні, римські штори, плісе, День-Ніч, зовнішній сонцезахист. Концепт редизайну.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet"><link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,{SUN_SVG.replace('"', "'").replace('#', '%23').replace('class=\'sun\' ', 'xmlns=\'http://www.w3.org/2000/svg\' ')}"></head><body>'''

DEMO = '<div class="demo">Концепт редизайну · <a href="../">обрати інший дизайн</a> · <a href="https://sunny-tm.com/uk" target="_blank" rel="noopener">оригінал</a></div>'

def shell_a(slug, body):
    _, nav, title, lead = P[slug]
    navl = ''.join(f'<a href="{href(s)}"{" class=cur" if s == slug else ""}>{P[s][1]}</a>' for s in MAIN_NAV)
    subl = ''.join(f'<a href="{href(s)}"{" class=cur" if s == slug else ""}>{P[s][1]}</a>' for s in SUB_NAV)
    if slug == 'index':
        hero = f'''<section class="hero"><div class="wrap hgrid"><div class="htext"><span class="pill">TM SUNNY · сонцезахисні системи</span><h1>Для Вас ми <em>підкорюємо</em> сонце</h1>
<p>Рулонні та римські штори, День-Ніч, плісе, дерев'яні жалюзі й зовнішній сонцезахист — виготовлення за Вашими розмірами до 3 робочих днів.</p>
<div class="hbtn"><a class="btn" href="catalog.html">Каталог продукції</a><a class="btn ghost" href="contacts.html">Де купити</a></div></div>
<div class="hslides">{''.join(f'<a class="slide{" on" if k==0 else ""}" href="{s["href"]}"><img src="{s["img"]}" alt=""><span class="cap"><small>{s["kicker"]}</small><b>{s["title"]}</b>{s["text"]}</span></a>' for k, s in enumerate(SLIDES))}
<div class="dots">{''.join(f'<button aria-label="Слайд {k+1}"{" class=on" if k==0 else ""}></button>' for k in range(len(SLIDES)))}</div></div></div></section>'''
    else:
        hero = f'<section class="phead"><div class="wrap"><nav class="crumbs"><a href="index.html">Головна</a> / {nav}</nav><h1>{e(title)}</h1><p>{e(lead)}</p></div></section>'
    return (HEAD(f'{title or "Рулонні штори та сонцезахист"} — TM SUNNY', 'a', 'family=Unbounded:wght@500;600;700&family=Manrope:wght@400;500;600;700;800')
        + DEMO + f'''<div class="topbar"><div class="wrap"><a href="{tel(PHONES[0])}">☎ {PHONES[0]}</a><span>Пн–Пт 9:00–18:00</span><nav>{subl}</nav></div></div>
<header class="hdr"><div class="wrap">{LOGO}<nav class="nav">{navl}</nav><a class="btn sm" href="#svc" data-open="0">Виклик замірника</a><button class="burger" aria-label="Меню" data-burger><i></i></button></div></header>
<main>{hero}{body}</main>
<section class="cta"><div class="wrap"><div><h2>Потрібна консультація?</h2><p>Підкажемо систему, тканину та найближчий салон.</p></div><div class="ctab"><a class="btn dark" href="#svc" data-open="1">Зворотний дзвінок</a><a class="btn light" href="#svc" data-open="2">Розрахунок вартості</a></div></div></section>
<footer class="ftr"><div class="wrap fgrid"><div>{LOGO}<p>{SLOGAN}</p><p class="small">Один з лідерів галузі сонцезахисту України.</p></div>
<div><h4>Компанія</h4>{''.join(f'<a href="{href(s)}">{P[s][1]}</a>' for s in ['about','certificates','news','stock','articles'])}</div>
<div><h4>Клієнтам</h4>{''.join(f'<a href="{href(s)}">{P[s][1]}</a>' for s in ['catalog','works','reviews','faq','dealers'])}</div>
<div><h4>Опт</h4>{''.join(f'<a href="{tel(p)}">{p}</a>' for p in PHONES)}<a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
<div class="wrap fbot"><span>2026 © Sunny. Всі права захищені</span><form class="sub" data-demo><input type="email" placeholder="Підписка на новини" required><button>ОК</button><p class="ok" hidden>Дякуємо!</p></form></div></footer>
{svc_modal()}<script src="../app.js"></script></body></html>''')

def shell_b(slug, body):
    _, nav, title, lead = P[slug]
    navl = ''.join(f'<a href="{href(s)}"{" class=cur" if s == slug else ""}><small>{k+1:02d}</small>{P[s][1]}</a>' for k, s in enumerate(MAIN_NAV))
    subl = ''.join(f'<a href="{href(s)}"{" class=cur" if s == slug else ""}>{P[s][1]}</a>' for s in SUB_NAV)
    if slug == 'index':
        hero = f'''<section class="hero"><div class="sunwash" aria-hidden="true"></div><div class="wrap"><p class="eyebrow">TM SUNNY · Україна</p><h1>Для Вас ми<br>підкорюємо <span>сонце.</span></h1>
<div class="hrow"><p>Сонцезахисні системи для дому, офісу й терас. Понад 1200 тканин, 100+ систем, виготовлення до 3 робочих днів.</p><div class="hbtn"><a class="btn" href="catalog.html">Каталог</a><a class="btn line" href="#svc" data-open="0">Виклик замірника</a></div></div>
<div class="banners">{''.join(f'<a class="banner" href="{s["href"]}"><img src="{s["img"]}" alt=""><span><small>{s["kicker"]}</small>{s["title"]} →</span></a>' for s in SLIDES)}</div></div></section>'''
    else:
        hero = f'<section class="phead"><div class="sunwash" aria-hidden="true"></div><div class="wrap"><nav class="crumbs"><a href="index.html">Sunny</a> — {nav}</nav><h1>{e(title)}</h1><p>{e(lead)}</p></div></section>'
    return (HEAD(f'{title or "Сонцезахисні системи"} — TM SUNNY', 'b', 'family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600;700')
        + DEMO + f'''<aside class="side"><div class="sideTop">{LOGO}<button class="burger" aria-label="Меню" data-burger><i></i></button></div>
<nav class="nav">{navl}<div class="subnav">{subl}</div></nav>
<div class="sidefoot"><span>Оптовий відділ</span>{''.join(f'<a href="{tel(p)}">{p}</a>' for p in PHONES[:2])}<span>Пн–Пт 9:00–18:00</span></div></aside>
<div class="page"><main>{hero}{body}</main>
<section class="cta"><div class="wrap"><h2>Обирайте світло<br>на свій смак.</h2><div class="ctab"><a class="btn" href="#svc" data-open="2">Розрахувати вартість</a><a class="btn line" href="#svc" data-open="1">Передзвоніть мені</a></div></div></section>
<footer class="ftr"><div class="wrap"><div class="fgrid"><div><b class="fslogan">{SLOGAN}</b></div>
<div>{''.join(f'<a href="{href(s)}">{P[s][1]}</a>' for s in MAIN_NAV)}</div><div>{''.join(f'<a href="{href(s)}">{P[s][1]}</a>' for s in SUB_NAV)}</div>
<div>{''.join(f'<a href="{tel(p)}">{p}</a>' for p in PHONES)}<a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
<div class="fbot"><span>2026 © Sunny. Всі права захищені</span><form class="sub" data-demo><input type="email" placeholder="Підписка на новини" required><button>→</button><p class="ok" hidden>Дякуємо!</p></form></div></div></footer></div>
{svc_modal()}<script src="../app.js"></script></body></html>''')

GH = 'https://faradeycom.github.io/'
SITES = {'a': ('sunny-ranok', shell_a, 'b'), 'b': ('sunny-poluden', shell_b, 'a')}

def build():
    for d, (repo, shell, other) in SITES.items():
        # 1) підпапка загального сайту вибору: /a/, /b/
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
        # 2) самостійний сайт dist/<repo>/ — публікується окремим репозиторієм
        out = os.path.join(ROOT, 'dist', repo)
        os.makedirs(out, exist_ok=True)
        shutil.copy(os.path.join(ROOT, d, 'style.css'), out)
        shutil.copy(os.path.join(ROOT, 'app.js'), out)
        for slug, *_ in PAGES:
            page = shell(slug, BODIES[slug]())
            open(os.path.join(ROOT, d, href(slug)), 'w', encoding='utf-8', newline='\n').write(page)
            alone = (page.replace('src="../app.js"', 'src="app.js"')
                         .replace('<a href="../">обрати інший дизайн</a>',
                                  f'<a href="{GH}{SITES[other][0]}/">інший дизайн</a> · <a href="{GH}sunny-redesign/">усі варіанти</a>'))
            open(os.path.join(out, href(slug)), 'w', encoding='utf-8', newline='\n').write(alone)
        open(os.path.join(out, '.nojekyll'), 'w').close()
    print('ok', len(PAGES) * 4, 'pages')

if __name__ == '__main__':
    build()
