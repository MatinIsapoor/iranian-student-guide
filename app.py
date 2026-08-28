"""
راهنمای دانشجویان ایرانی خارج از کشور
یک اپلیکیشن ساده‌ی Flask برای نمایش راهنمای زندگی دانشجویی در کشورهای مختلف
"""

import json
import re
from pathlib import Path
from flask import Flask, render_template, abort
from markupsafe import Markup

app = Flask(__name__)

DATA_PATH = Path(__file__).parent / "data" / "guides.json"

_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def linkify(text):
    """تبدیل لینک‌های به‌سبک مارک‌داون [متن](آدرس) به تگ <a> با باز شدن در تب جدید"""
    if not text:
        return text
    replaced = _LINK_PATTERN.sub(
        r'<a href="\2" target="_blank" rel="noopener">\1</a>', text
    )
    return Markup(replaced)


app.jinja_env.filters["linkify"] = linkify


CATEGORY_META = {
    "shopping": {"icon": "🛒", "class": "icon-shopping"},
    "housing": {"icon": "🏠", "class": "icon-housing"},
}


def load_guides():
    """خواندن داده‌های راهنما از فایل JSON"""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    """صفحه‌ی اصلی: لیست کشورها + بخش عمومی قدم‌های اول"""
    guides = load_guides()
    general = guides.pop("general", None)
    return render_template("index.html", countries=guides, general=general)


@app.route("/country/<country_code>")
def country_page(country_code):
    """صفحه‌ی یک کشور خاص: لیست دسته‌بندی‌ها"""
    guides = load_guides()
    country = guides.get(country_code)
    if not country:
        abort(404)
    return render_template(
        "country.html", country=country, country_code=country_code, category_meta=CATEGORY_META
    )


@app.route("/country/<country_code>/<category>")
def category_page(country_code, category):
    """صفحه‌ی یک دسته‌بندی خاص (مثلاً خرید و زندگی روزمره)"""
    guides = load_guides()
    country = guides.get(country_code)
    if not country:
        abort(404)
    cat_data = country.get("categories", {}).get(category)
    if not cat_data:
        abort(404)
    return render_template(
        "guide.html",
        country=country,
        country_code=country_code,
        category=cat_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
