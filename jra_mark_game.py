#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JRA マークカード 塗り方練習ゲーム（初心者向け）

出された指示どおりにマークカードを塗って「採点」を押すだけ。
Python標準の tkinter だけで動きます。

    python3 jra_mark_game.py
"""
import random
import sys
import time
from math import comb
try:
    import tkinter as tk
    from tkinter import font as tkfont
except ModuleNotFoundError:  # ロジック部分だけテストしたい環境用
    tk = tkfont = None

# ───────────────────────── 定数 ─────────────────────────
VENUES = ["中山", "東京", "京都", "阪神", "福島", "新潟", "中京", "小倉", "札幌", "函館"]
TYPES = ["単勝", "複勝", "枠連", "馬連", "馬単", "ワイド", "3連複", "3連単"]
UNITS = [("万円", 10000), ("千円", 1000), ("百円", 100)]
AMT_ROWS = [[30, 20, 10, 5], [4, 3, 2, 1]]
AMT_VALUES = [30, 20, 10, 5, 4, 3, 2, 1]
CIRC = "①②③④"
LINES = 4

LEVELS = {
    "レベル1 入門（単勝・複勝）": 1,
    "レベル2 初級（馬連・ワイド・枠連・馬単）": 2,
    "レベル3 中級（ボックス・3連複・馬単）": 3,
    "レベル4 上級（3連単フォーメーション等）": 4,
}

# ───────────────────────── 問題生成 ─────────────────────────
def _fmt(s):
    return "・".join(str(x) for x in sorted(s))


def count_points(ty, mode, blocks):
    A, B, C = blocks
    if ty == "3連単":
        return len({(a, b, c) for a in A for b in B for c in C if len({a, b, c}) == 3})
    if ty == "馬単":
        return len({(a, b) for a in A for b in B if a != b})
    if ty in ("馬連", "ワイド"):
        return comb(len(A), 2) if mode == "ボックス" else 1
    if ty == "3連複":
        if mode == "ボックス":
            return comb(len(A), 3)
        if mode == "軸1頭ながし":
            return comb(len(B), 2)
        return 1
    return 1


def make_line(ty, mode, heads):
    pool = list(range(1, heads + 1))

    def pick(n, ex=()):
        cand = [x for x in pool if x not in ex]
        return set(random.sample(cand, min(n, len(cand))))

    A, B, C = set(), set(), set()
    if ty in ("単勝", "複勝"):
        A = pick(1)
    elif ty == "枠連":
        A = set(random.sample(range(1, 9), 2))
    elif ty in ("馬連", "ワイド"):
        A = pick(2) if mode == "通常" else pick(random.choice([3, 4]))
    elif ty == "馬単":
        if mode == "通常":
            A = pick(1)
            B = pick(1, ex=A)
        else:
            A = pick(random.choice([1, 1, 2]))
            B = pick(random.choice([1, 2, 3]), ex=A)
    elif ty == "3連複":
        if mode == "通常":
            A = pick(3)
        elif mode == "ボックス":
            A = pick(random.choice([4, 4, 5]))
        else:
            A = pick(1)
            B = pick(random.choice([2, 3, 4]), ex=A)
    elif ty == "3連単":
        A = pick(random.choice([1, 1, 2]))
        B = pick(random.choice([2, 2, 3]), ex=() if random.random() < 0.35 else A)
        C = pick(random.choice([2, 3, 4]), ex=() if random.random() < 0.35 else (A | B))
    return [A, B, C]


def gen_task(level):
    venue = random.randrange(len(VENUES))
    race = random.randint(1, 12)
    heads = random.randint(8, 18)
    if level == 1:
        ty = random.choice(["単勝", "複勝"]); mode = "通常"; nl = 1
        amounts = [100, 200, 300, 500]
    elif level == 2:
        ty = random.choice(["馬連", "ワイド", "枠連", "馬単"]); mode = "通常"
        nl = random.choice([1, 2]); amounts = [100, 200, 300, 500, 1000]
    elif level == 3:
        ty = random.choice(["馬連", "ワイド", "3連複", "馬単"])
        if ty == "馬単":
            mode = "フォーメーション"
        elif ty == "3連複":
            mode = random.choice(["通常", "ボックス", "軸1頭ながし"])
        else:
            mode = random.choice(["通常", "ボックス"])
        nl = random.choice([1, 2, 3]); amounts = [100, 200, 300, 500, 1000]
    else:
        ty = random.choice(["3連単", "3連単", "3連単", "3連複", "馬単"])
        if ty == "3連複":
            mode = random.choice(["ボックス", "軸1頭ながし"])
        else:
            mode = "フォーメーション"
        nl = random.choice([2, 3, 4]); amounts = [100, 200, 300, 500, 1000, 1500, 2000]

    lines = []
    seen = set()
    tries = 0
    while len(lines) < nl and tries < 200:
        tries += 1
        bl = make_line(ty, mode, heads)
        pts = count_points(ty, mode, bl)
        if pts < 1 or pts > 12:
            continue
        key = tuple(tuple(sorted(b)) for b in bl)
        if key in seen:
            continue
        seen.add(key)
        lines.append({"blocks": bl, "amount": random.choice(amounts), "points": pts})
    prev = level >= 2 and random.random() < 0.15
    return {"level": level, "venue": venue, "race": race, "type": ty,
            "mode": mode, "prev": prev, "lines": lines}


def describe_line(ty, mode, bl):
    A, B, C = bl
    if ty in ("単勝", "複勝"):
        return f"{_fmt(A)}番"
    if ty == "枠連":
        a, b = sorted(A)
        return f"{a}枠 - {b}枠"
    if ty in ("馬連", "ワイド"):
        return f"ボックス {_fmt(A)}" if mode == "ボックス" else "-".join(str(x) for x in sorted(A))
    if ty == "馬単":
        return f"1着 {_fmt(A)} → 2着 {_fmt(B)}"
    if ty == "3連複":
        if mode == "通常":
            return "-".join(str(x) for x in sorted(A))
        if mode == "ボックス":
            return f"ボックス {_fmt(A)}"
        return f"軸 {_fmt(A)} ― 相手 {_fmt(B)}"
    return f"1着 {_fmt(A)} → 2着 {_fmt(B)} → 3着 {_fmt(C)}"


def how_to(ty, mode):
    if ty in ("単勝", "複勝"):
        return "1着欄に馬番を1つ塗る"
    if ty == "枠連":
        return "1着欄に枠番を2つ塗る（枠番は1〜8）"
    if ty in ("馬連", "ワイド") or (ty == "3連複" and mode == "通常"):
        return "1着欄に馬番をまとめて塗る"
    if mode == "ボックス":
        return "1着欄にボックスの馬番を全部塗る"
    if ty == "3連複":
        return "1着欄＝軸馬、2着欄＝相手馬を塗る"
    if ty == "馬単":
        return "1着欄＝1着の馬、2着欄＝2着の馬を塗る"
    return "着順ごとに1着欄・2着欄・3着欄へ塗る"


def task_text(t):
    ty, mode = t["type"], t["mode"]
    head = f"【指示】{VENUES[t['venue']]} {t['race']}レース　{ty}"
    if mode != "通常":
        head += f"（{mode}）"
    if t["prev"]:
        head += "　※前日発売"
    rows = [head]
    total = 0
    for i, ln in enumerate(t["lines"]):
        rows.append(f" {CIRC[i]} {describe_line(ty, mode, ln['blocks'])}"
                    f"　各{ln['amount']:,}円（{ln['points']}通り）")
        total += ln["amount"] * ln["points"]
    rows.append(f"　　合計 {total:,}円　／　塗り方: {how_to(ty, mode)}")
    return "\n".join(rows)


# ───────────────────────── 採点ロジック ─────────────────────────
def canon_amount(a):
    """金額 → (単位の倍率, [金額欄の数字])。標準的な塗り方。"""
    for _, m in UNITS:
        if a % m == 0 and a // m <= 30:
            u = m
            break
    else:
        u = 100
    v = a // u
    digits = []
    for d in AMT_VALUES:
        while v >= d:
            digits.append(d)
            v -= d
    return u, digits


def marked_amount(on, L):
    units = [k[2] for k in on if k[0] == "unit" and k[1] == L]
    digits = [k[2] for k in on if k[0] == "amt" and k[1] == L]
    if len(units) != 1 or not digits:
        return None
    return sum(digits) * units[0]


def full_expected(task):
    ks = {("venue", task["venue"]), ("race", task["race"]), ("type", task["type"])}
    if task["prev"]:
        ks.add(("prev",))
    for L, ln in enumerate(task["lines"]):
        for b in range(3):
            for n in ln["blocks"][b]:
                ks.add(("h", L, b, n))
        u, digits = canon_amount(ln["amount"])
        ks.add(("unit", L, u))
        for d in digits:
            ks.add(("amt", L, d))
    return ks


def diff_keys(task, on):
    """(塗り忘れ, 余計な塗り) を返す。金額は値が合っていれば別の塗り方でもOK。"""
    exp = full_expected(task)
    amount_ok = {L: marked_amount(on, L) == ln["amount"] for L, ln in enumerate(task["lines"])}
    missing, extra = set(), set()
    for k in exp - on:
        if k[0] in ("unit", "amt") and amount_ok.get(k[1], False):
            continue
        missing.add(k)
    for k in on - exp:
        if k[0] in ("unit", "amt") and amount_ok.get(k[1], False):
            continue
        extra.add(k)
    return missing, extra


def check_marks(task, on):
    """[(項目名, 合否, 正解の説明)] を返す。"""
    res = []

    def got(p):
        return {k[1] for k in on if k[0] == p}

    v = task["venue"]
    res.append(("場名", got("venue") == {v}, f"{VENUES[v]}を1つ塗る"))
    res.append(("レース番号", got("race") == {task["race"]}, f"{task['race']}を1つ塗る"))
    res.append(("式別", got("type") == {task["type"]}, f"{task['type']}を1つ塗る"))
    if task["prev"]:
        res.append(("前日発売", ("prev",) in on, "前日発売を塗る"))
    else:
        res.append(("前日発売", ("prev",) not in on, "前日発売は塗らない"))

    n = len(task["lines"])
    for L in range(n):
        ln = task["lines"][L]
        ok = True
        for b in range(3):
            g = {k[3] for k in on if k[0] == "h" and k[1] == L and k[2] == b}
            if g != ln["blocks"][b]:
                ok = False
        exp_txt = " / ".join(f"{['1着','2着','3着'][b]}欄: {_fmt(ln['blocks'][b])}"
                             for b in range(3) if ln["blocks"][b])
        res.append((f"{CIRC[L]}行 馬番", ok, exp_txt))
        res.append((f"{CIRC[L]}行 金額", marked_amount(on, L) == ln["amount"],
                    f"{ln['amount']:,}円（例: {_amt_example(ln['amount'])}）"))
    if n < LINES:
        stray = any(k[0] in ("h", "amt", "unit", "ura") and k[1] >= n for k in on)
        res.append(("使わない行", not stray, f"{CIRC[n]}行目以降は空欄のまま"))
    res.append(("ウラ", not any(k[0] == "ura" for k in on), "今回ウラは塗らない"))
    return res


def _amt_example(a):
    u, digits = canon_amount(a)
    name = {10000: "万円", 1000: "千円", 100: "百円"}[u]
    return "＋".join(str(d) for d in digits) + f" と {name}"


# ───────────────────────── GUI ─────────────────────────
W, H = 1210, 640
CARD = "#eaf5bd"
BOX = "#f4fad8"
ORANGE = "#e8791a"
INK = "#1b1b1b"


def jp_font(root):
    fams = set(tkfont.families(root))
    for n in ("Meiryo", "Yu Gothic UI", "Hiragino Sans", "Hiragino Kaku Gothic ProN",
              "Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic", "IPAGothic",
              "TakaoGothic", "MS Gothic"):
        if n in fams:
            return n
    return "TkDefaultFont"


class MarkCardGame:
    def __init__(self, root):
        self.root = root
        root.title("JRA マークカード練習ゲーム")
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.S = max(0.5, min(1.0, (sw - 30) / W, (sh - 280) / H))
        self.fam = jp_font(root)
        self.on, self.pos, self.items = set(), {}, {}
        self.task = None
        self.t0 = time.time()
        self.peeked = False
        self.played = 0
        self.perfect = 0
        self.streak = 0
        self._build_ui()
        self._draw_card()
        self.new_task()

    # ---- UI ----
    def _build_ui(self):
        f = self.fam
        top = tk.Frame(self.root, padx=8, pady=6)
        top.pack(fill="x")
        self.lbl_task = tk.Label(top, text="", justify="left", anchor="w",
                                 font=(f, 14, "bold"), bg="#fffbe6",
                                 relief="groove", padx=10, pady=6)
        self.lbl_task.pack(side="left", fill="x", expand=True)

        side = tk.Frame(top)
        side.pack(side="right", padx=6)
        self.level_var = tk.StringVar(value=list(LEVELS)[0])
        om = tk.OptionMenu(side, self.level_var, *LEVELS, command=lambda _: self.new_task())
        om.config(font=(f, 10))
        om.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)
        for i, (txt, cmd) in enumerate([("採点する", self.evaluate),
                                        ("答えを見る", self.show_answer),
                                        ("塗り直す", self.clear_marks),
                                        ("次の問題", self.new_task)]):
            tk.Button(side, text=txt, font=(f, 11, "bold"), width=9,
                      command=cmd).grid(row=1 + i // 2, column=i % 2, padx=2, pady=2)
        self.lbl_stat = tk.Label(side, text="", font=(f, 9), fg="#555")
        self.lbl_stat.grid(row=3, column=0, columnspan=2)

        self.lbl_result = tk.Label(self.root, text="", justify="left", anchor="w",
                                   font=(f, 11), padx=10,
                                   wraplength=int(W * self.S))
        self.lbl_result.pack(fill="x")
        self.cv = tk.Canvas(self.root, width=int(W * self.S), height=int(H * self.S),
                            bg=CARD, highlightthickness=0)
        self.cv.pack(padx=4, pady=4)

    # ---- 描画ヘルパー ----
    def _s(self, *v):
        return [x * self.S for x in v]

    def _font(self, size, bold=False):
        return (self.fam, max(7, int(size * self.S)), "bold" if bold else "normal")

    def _rect(self, x1, y1, x2, y2, **kw):
        return self.cv.create_rectangle(*self._s(x1, y1, x2, y2), **kw)

    def _text(self, x, y, t, size=11, bold=False, fill=INK, **kw):
        return self.cv.create_text(*self._s(x, y), text=t, font=self._font(size, bold),
                                   fill=fill, **kw)

    def _mark(self, key, cx, cy, label="", w=24, h=34, size=11):
        oid = self.cv.create_oval(*self._s(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
                                  outline=ORANGE, width=2, fill=CARD)
        tid = self.cv.create_text(*self._s(cx, cy), text=label, fill=ORANGE,
                                  font=self._font(size, True))
        for i in (oid, tid):
            self.cv.tag_bind(i, "<Button-1>", lambda e, k=key: self.toggle(k))
        self.items[key] = (oid, tid)
        self.pos[key] = (cx, cy, w, h)

    def _draw_card(self):
        self._rect(2, 2, W - 2, H - 2, fill=CARD, outline="#555", width=2)

        # 前日発売
        self._rect(10, 8, 96, 128, fill=BOX, outline="#555")
        self._text(53, 30, "前日\n発売", 11, True)
        self._mark(("prev",), 53, 88, w=26, h=40)

        # 場名
        self._rect(100, 8, 650, 128, fill=BOX, outline="#555")
        self._text(375, 22, "場　名", 12, True)
        for i, name in enumerate(VENUES):
            cx = 127 + 54 * i
            self._text(cx, 56, name, 12, True)
            self._mark(("venue", i), cx, 96)

        # レース番号
        self._rect(660, 8, 942, 128, fill=BOX, outline="#555")
        self._text(801, 22, "レース番号", 12, True)
        for n in range(1, 13):
            r, c = divmod(n - 1, 6)
            self._mark(("race", n), 683 + 46 * c, 58 + 44 * r, str(n), w=26, h=32, size=12)

        # 式別
        self._rect(950, 8, 1204, 128, fill=BOX, outline="#555")
        self._text(1077, 17, "式　別", 12, True)
        for i, name in enumerate(TYPES):
            r, c = divmod(i, 4)
            cx = 981 + 62 * c
            self._text(cx, 40 + 46 * r, name, 11, True)
            self._mark(("type", name), cx, 64 + 46 * r, w=24, h=26)

        # 見出し
        for b in range(3):
            self._text(14 + b * 300 + 138, 146, f"{b + 1}着・{b + 1}頭目", 11, True)
        self._text(915, 146, "ウラ", 10, True)
        self._text(1004, 146, "金額", 11, True)
        self._text(1126, 146, "単位", 11, True)

        # 4行
        for L in range(LINES):
            y0 = 158 + L * 120
            self._rect(6, y0, W - 6, y0 + 114, fill=BOX, outline="#888")
            self._text(10, y0 + 9, CIRC[L], 10, True, anchor="w")
            for b in range(3):
                bx = 14 + b * 300
                self._rect(bx, y0 + 4, bx + 280, y0 + 110, outline="#bbb")
                for n in range(1, 19):
                    r, c = divmod(n - 1, 9)
                    self._mark(("h", L, b, n), bx + 18 + c * 30, y0 + 32 + r * 48,
                               str(n), w=24, h=34, size=10)
            self._mark(("ura", L), 915, y0 + 57, "ウ\nラ", w=28, h=52, size=10)
            for r, row in enumerate(AMT_ROWS):
                for c, val in enumerate(row):
                    self._mark(("amt", L, val), 950 + c * 36, y0 + 32 + r * 48,
                               str(val), w=28, h=34, size=10)
            for c, (name, mult) in enumerate(UNITS):
                self._mark(("unit", L, mult), 1090 + c * 36, y0 + 57,
                           name[0] + "\n円", w=28, h=52, size=10)

    # ---- 操作 ----
    def _paint(self, key):
        oid, tid = self.items[key]
        on = key in self.on
        self.cv.itemconfig(oid, fill=INK if on else CARD)
        self.cv.itemconfig(tid, fill="#cfcfcf" if on else ORANGE)

    def toggle(self, key):
        self.cv.delete("fb")
        if key in self.on:
            self.on.remove(key)
        else:
            self.on.add(key)
        self._paint(key)

    def clear_marks(self):
        self.cv.delete("fb")
        keys = list(self.on)
        self.on.clear()
        for k in keys:
            self._paint(k)
        self.lbl_result.config(text="")

    def new_task(self):
        self.clear_marks()
        self.task = gen_task(LEVELS[self.level_var.get()])
        self.lbl_task.config(text=task_text(self.task))
        self.t0 = time.time()
        self.peeked = False
        self._update_stat()

    def _update_stat(self):
        self.lbl_stat.config(text=f"全問正解 {self.perfect}/{self.played}問　連続 {self.streak}")

    def _ring(self, key, color, dash=None):
        cx, cy, w, h = self.pos[key]
        m = 6
        self.cv.create_oval(*self._s(cx - w / 2 - m, cy - h / 2 - m, cx + w / 2 + m, cy + h / 2 + m),
                            outline=color, width=3, dash=dash, tags="fb")

    def show_answer(self):
        self.cv.delete("fb")
        self.peeked = True
        for k in full_expected(self.task):
            self._ring(k, "#1f6fe0", (4, 3))
        self.lbl_result.config(fg="#1f6fe0",
                               text="青い点線が正解の位置です。塗ってから「採点する」を押してみましょう"
                                    "（答えを見た問題は成績に数えません）")

    def evaluate(self):
        self.cv.delete("fb")
        res = check_marks(self.task, self.on)
        ok = sum(1 for _, g, _ in res if g)
        total = len(res)
        sec = time.time() - self.t0
        missing, extra = diff_keys(self.task, self.on)
        for k in missing:
            self._ring(k, "#1f6fe0", (4, 3))
        for k in extra:
            self._ring(k, "#e02020")
        if ok == total:
            msg = f"🎉 全問正解！  {ok}/{total}項目　所要時間 {sec:.0f}秒"
            color = "#168a2e"
        else:
            bad = [f"✗ {name}: {exp}" for name, g, exp in res if not g]
            msg = f"採点 {ok}/{total}項目　所要時間 {sec:.0f}秒\n" + "\n".join(bad) + \
                  "\n（赤い輪＝余計に塗った所／青い点線＝塗り忘れ）"
            color = "#c03030"
        self.lbl_result.config(text=msg, fg=color)
        if not self.peeked:
            self.played += 1
            if ok == total:
                self.perfect += 1
                self.streak += 1
            else:
                self.streak = 0
            self._update_stat()
            self.peeked = True  # 同じ問題の再採点は成績に数えない


def main():
    root = tk.Tk()
    MarkCardGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
