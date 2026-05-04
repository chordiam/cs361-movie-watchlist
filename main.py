"""
Movie Watchlist App — Milestone #1
CS361 | Sprint 1: Add Movie, View Watchlist, Mark as Watched
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json, os, time, math
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_OK = True
except ImportError:
    PIL_OK = False

DATA_FILE = "watchlist.json"

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK    = "#0a0e1a"
BG_MID     = "#111827"
BG_CARD    = "#1a2540"
BG_CARD2   = "#1f2e4e"
PURPLE     = "#7c6cf0"
PURPLE2    = "#5a4fcf"
TEAL       = "#00d4c8"
ORANGE     = "#ff8c42"
GRAY_BTN   = "#253450"
RED        = "#e84545"
TEXT_WHITE = "#ffffff"
TEXT_SUB   = "#7a96be"
TEXT_HINT  = "#b0a4ff"
WARN_BG    = "#2a1a0a"
WARN_FG    = "#ff8c42"
BORDER     = "#1e3058"

GENRES = ["Action","Comedy","Drama","Horror","Sci-Fi","Thriller",
          "Romance","Documentary","Animation","Fantasy","Mystery","Other"]

# Fake movie poster colors — simulate a grid of colourful posters
POSTER_COLORS = [
    ["#1a1a2e","#16213e","#0f3460","#533483"],
    ["#2d132c","#ee4540","#c72c41","#801336"],
    ["#0d0d0d","#1a1a1a","#f5a623","#f76b1c"],
    ["#0f2027","#203a43","#2c5364","#4ca1af"],
    ["#141e30","#243b55","#0052d4","#4364f7"],
    ["#200122","#6f0000","#c94b4b","#4b134f"],
    ["#093028","#237a57","#11998e","#38ef7d"],
    ["#1a1a2e","#e94560","#0f3460","#16213e"],
    ["#0d1b2a","#1b2838","#c3073f","#950740"],
    ["#1c1c1c","#3d3d3d","#ff6b6b","#feca57"],
    ["#2c003e","#1a0533","#8e44ad","#6c3483"],
    ["#001f3f","#003366","#ff851b","#ff4136"],
]

POSTER_LABELS = [
    "ACTION\nHERO","THE\nDARK","EPIC\nQUEST","NIGHT\nFALL",
    "HORIZON","SILENT\nSTORM","LOST\nWORLD","EDGE\nOF TIME",
    "RISING\nSUN","NEON\nDREAM","PURPLE\nRAIN","DEEP\nBLUE",
]

# ── Persistence ───────────────────────────────────────────────────────────────
def load_watchlist():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_watchlist(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Label-based button (bypasses macOS color overrides on tk.Button) ──────────
def btn(parent, text, cmd, bg=PURPLE, fg=TEXT_WHITE, fs=11, px=18, py=9):
    hv = _darken(bg)
    lbl = tk.Label(parent, text=text, bg=bg, fg=fg,
                   font=("Helvetica", fs, "bold"),
                   padx=px, pady=py, cursor="hand2")
    lbl.bind("<Button-1>", lambda e: cmd())
    lbl.bind("<Enter>",    lambda e: lbl.config(bg=hv))
    lbl.bind("<Leave>",    lambda e: lbl.config(bg=bg))
    return lbl

def _darken(c):
    try:
        h = c.lstrip("#")
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return f"#{max(0,r-30):02x}{max(0,g-30):02x}{max(0,b-30):02x}"
    except Exception:
        return c

def hsep(parent, color=BORDER, h=1):
    tk.Frame(parent, bg=color, height=h).pack(fill="x")

def spacer(parent, h=10):
    tk.Frame(parent, bg=parent.cget("bg"), height=h).pack()


# ══════════════════════════════════════════════════════════════════════════════
#  SPLASH / HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════════
BG_IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg.png")

class SplashScreen(tk.Frame):
    def __init__(self, master, on_enter):
        super().__init__(master, bg=BG_DARK)
        self.on_enter  = on_enter
        self._bg_raw   = None
        self._bg_photo = None
        self._load_bg()
        self._build()

    def _load_bg(self):
        if not PIL_OK:
            return
        try:
            self._bg_raw = Image.open(BG_IMAGE_PATH).convert("RGBA")
        except Exception:
            self._bg_raw = None

    def _build(self):
        self.canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.canvas.delete("all")
        w = event.width
        h = event.height

        if self._bg_raw and PIL_OK:
            bg = self._bg_raw.resize((w, h), Image.LANCZOS)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            steps = 80
            for i in range(steps):
                ratio = i / steps
                if ratio < 0.45:
                    alpha = 245
                elif ratio < 0.72:
                    alpha = int(245 - (ratio - 0.45) / 0.27 * 220)
                else:
                    alpha = int(25 * (1 - (ratio - 0.72) / 0.28))
                alpha = max(0, min(255, alpha))
                x0 = int(i * w / steps)
                x1 = int((i+1) * w / steps)
                draw.rectangle([x0, 0, x1, h], fill=(10, 14, 26, alpha))
            composite = Image.alpha_composite(bg, overlay).convert("RGB")
            self._bg_photo = ImageTk.PhotoImage(composite)
            self.canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)
        else:
            self.canvas.create_rectangle(0, 0, w, h, fill=BG_DARK, outline="")

        # Solid left panel
        panel_w = int(w * 0.44)
        self.canvas.create_rectangle(0, 0, panel_w, h, fill=BG_DARK, outline="")

        # ── Left content ──────────────────────────────────────────────────────
        cx   = panel_w // 2
        pad  = 40
        ty   = int(h * 0.22)

        # 🎬 icon
        self.canvas.create_text(cx, ty,
            text="🎬", font=("Helvetica", 52), fill=TEXT_WHITE, anchor="center")

        # App title
        self.canvas.create_text(cx, ty + 80,
            text="My Movie", font=("Helvetica", 36, "bold"),
            fill=TEXT_WHITE, anchor="center")
        self.canvas.create_text(cx, ty + 126,
            text="Watchlist", font=("Helvetica", 36, "bold"),
            fill=PURPLE, anchor="center")

        # Divider line
        self.canvas.create_line(
            cx - 60, ty + 162, cx + 60, ty + 162,
            fill=BORDER, width=2)

        # Tagline
        self.canvas.create_text(cx, ty + 192,
            text="Track movies you want to watch.\nAdd, organize, never forget a title.",
            font=("Helvetica", 14), fill=TEXT_SUB,
            justify="center", anchor="center")

        # IH#1 — benefit note
        self.canvas.create_text(cx, ty + 258,
            text="✨  No account needed. Totally local.",
            font=("Helvetica", 12, "italic"), fill=TEAL,
            anchor="center")

        # IH#2 — cost note
        self.canvas.create_text(cx, ty + 290,
            text="💾  Your data stays on this device only.",
            font=("Helvetica", 12), fill=TEXT_SUB, anchor="center")

        # "Enter" button — draw as a canvas rectangle + text, clickable
        bw, bh_size = 220, 52
        bx1 = cx - bw//2
        bx2 = cx + bw//2
        by1 = ty + 330
        by2 = by1 + bh_size

        self._btn_rect = self.canvas.create_rectangle(
            bx1, by1, bx2, by2,
            fill=PURPLE, outline="", tags="enterbtn")
        self._btn_text = self.canvas.create_text(
            cx, by1 + bh_size//2,
            text="▶   Go to My Watchlist",
            font=("Helvetica", 14, "bold"),
            fill=TEXT_WHITE, tags="enterbtn")

        self.canvas.tag_bind("enterbtn", "<Button-1>", lambda e: self.on_enter())
        self.canvas.tag_bind("enterbtn", "<Enter>",
                             lambda e: self.canvas.itemconfig(self._btn_rect, fill=PURPLE2))
        self.canvas.tag_bind("enterbtn", "<Leave>",
                             lambda e: self.canvas.itemconfig(self._btn_rect, fill=PURPLE))

        # Version / footer
        self.canvas.create_text(cx, h - 20,
            text="v1.0.0  •  CS361 Milestone #1",
            font=("Helvetica", 10), fill=TEXT_SUB, anchor="center")


# ══════════════════════════════════════════════════════════════════════════════
#  ADD MOVIE SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class AddMovieScreen(tk.Frame):
    def __init__(self, master, on_back, on_add):
        super().__init__(master, bg=BG_MID)
        self.on_back = on_back
        self.on_add  = on_add
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=14)
        hdr.pack(fill="x")
        back = tk.Label(hdr, text="← Back", bg=BG_DARK, fg=TEXT_HINT,
                        font=("Helvetica", 13, "bold"), cursor="hand2", padx=18)
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self.on_back())
        back.bind("<Enter>",    lambda e: back.config(fg=TEXT_WHITE))
        back.bind("<Leave>",    lambda e: back.config(fg=TEXT_HINT))
        tk.Label(hdr, text="Add a Movie", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        hsep(self, BG_DARK)

        # IH#6 step indicator
        step = tk.Frame(self, bg="#0d1525", pady=12)
        step.pack(fill="x")
        tk.Label(step, text="① Enter Title    →    ② Choose Genre    →    ③ Confirm",
                 bg="#0d1525", fg=TEXT_HINT, font=("Helvetica", 13, "italic")).pack()
        hsep(self)

        body = tk.Frame(self, bg=BG_MID, padx=52, pady=32)
        body.pack(fill="both", expand=True)

        # IH#1 benefit
        tk.Label(body,
                 text="✨  Saves to your local watchlist — no account, no data shared.",
                 bg=BG_MID, fg=TEAL, font=("Helvetica", 14, "italic"),
                 wraplength=520, justify="center").pack(pady=(0,8))

        # IH#2 cost
        tk.Label(body,
                 text="💾  Stored only on this device. No internet required.",
                 bg=BG_MID, fg=TEXT_SUB, font=("Helvetica", 13)).pack(pady=(0,24))

        hsep(body)
        spacer(body, 20)

        # Title
        tk.Label(body, text="Movie Title *", bg=BG_MID, fg=TEXT_WHITE,
                 font=("Helvetica", 14, "bold"), anchor="w").pack(fill="x")
        spacer(body, 6)

        self.title_var = tk.StringVar()
        self.entry = tk.Entry(body, textvariable=self.title_var,
                              bg=BG_CARD, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                              relief="flat", font=("Helvetica", 15),
                              highlightthickness=2,
                              highlightbackground=PURPLE,
                              highlightcolor=TEAL)
        self.entry.pack(fill="x", ipady=13)
        self.entry.insert(0, "e.g. The Godfather")
        self.entry.config(fg=TEXT_SUB)
        self.entry.bind("<FocusIn>",  self._ph_clear)
        self.entry.bind("<FocusOut>", self._ph_restore)

        spacer(body, 22)

        # Genre
        gf = tk.Frame(body, bg=BG_MID)
        gf.pack(fill="x")
        tk.Label(gf, text="Genre", bg=BG_MID, fg=TEXT_WHITE,
                 font=("Helvetica", 14, "bold")).pack(side="left")
        tk.Label(gf, text="  (optional)", bg=BG_MID, fg=TEXT_SUB,
                 font=("Helvetica", 12, "italic")).pack(side="left")
        spacer(body, 6)

        self.genre_var = tk.StringVar()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                        fieldbackground=BG_CARD, background=BG_CARD,
                        foreground=TEXT_WHITE, selectbackground=PURPLE,
                        selectforeground=TEXT_WHITE, bordercolor=BORDER,
                        arrowcolor=TEXT_WHITE)
        style.map("Dark.TCombobox", fieldbackground=[("readonly", BG_CARD)])

        self.combo = ttk.Combobox(body, textvariable=self.genre_var,
                                  values=GENRES, state="readonly",
                                  font=("Helvetica", 13), style="Dark.TCombobox")
        self.combo.set("Select genre...")
        self.combo.pack(fill="x", ipady=9)

        spacer(body, 30)

        bf = tk.Frame(body, bg=BG_MID)
        bf.pack(fill="x")
        cancel_b = btn(bf, "Cancel", self.on_back, bg=GRAY_BTN, fs=13, px=24, py=13)
        cancel_b.pack(side="left", expand=True, fill="x", padx=(0,12))
        add_b = btn(bf, "➕  Add to Watchlist", self._submit, bg=PURPLE, fs=13, px=24, py=13)
        add_b.pack(side="left", expand=True, fill="x")

        # IH#8 warning
        self.warn = tk.Frame(body, bg=WARN_BG, pady=12, padx=16)
        tk.Label(self.warn, text="⚠️   Title is required before adding a movie.",
                 bg=WARN_BG, fg=WARN_FG, font=("Helvetica", 14, "bold")).pack()

    def _ph_clear(self, _=None):
        if self.entry.get() == "e.g. The Godfather":
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT_WHITE)

    def _ph_restore(self, _=None):
        if not self.entry.get():
            self.entry.insert(0, "e.g. The Godfather")
            self.entry.config(fg=TEXT_SUB)

    def _submit(self):
        t = self.title_var.get().strip()
        if not t or t == "e.g. The Godfather":
            self.warn.pack(fill="x", pady=(18,0))
            return
        self.warn.pack_forget()
        g = self.genre_var.get()
        if g == "Select genre...":
            g = ""
        self.on_add(t, g)


# ══════════════════════════════════════════════════════════════════════════════
#  MOVIE DETAIL SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class MovieDetailScreen(tk.Frame):
    def __init__(self, master, movie, on_back, on_toggle, on_remove):
        super().__init__(master, bg=BG_MID)
        self.movie     = movie
        self.on_back   = on_back
        self.on_toggle = on_toggle
        self.on_remove = on_remove
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=BG_DARK, pady=14)
        hdr.pack(fill="x")
        back = tk.Label(hdr, text="← Back", bg=BG_DARK, fg=TEXT_HINT,
                        font=("Helvetica", 13, "bold"), cursor="hand2", padx=18)
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self.on_back())
        back.bind("<Enter>",    lambda e: back.config(fg=TEXT_WHITE))
        back.bind("<Leave>",    lambda e: back.config(fg=TEXT_HINT))
        tk.Label(hdr, text="Movie Detail", bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Helvetica", 16, "bold")).pack(side="left")
        hsep(self, BG_DARK)

        body = tk.Frame(self, bg=BG_MID, padx=56, pady=40)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=self.movie["title"], bg=BG_MID, fg=TEXT_WHITE,
                 font=("Helvetica", 28, "bold"), anchor="w",
                 wraplength=540, justify="left").pack(fill="x")
        spacer(body, 12)

        if self.movie.get("genre"):
            tk.Label(body, text=f"  {self.movie['genre']}  ",
                     bg=TEAL, fg=BG_DARK, font=("Helvetica", 12, "bold"),
                     padx=12, pady=5).pack(anchor="w")
            spacer(body, 16)

        is_w    = self.movie.get("watched", False)
        stat_bg = "#08281f" if is_w else BG_CARD
        stat_fg = TEAL      if is_w else TEXT_SUB
        stat_txt = "✓  Watched" if is_w else "○  Unwatched"
        tk.Label(body, text=stat_txt, bg=stat_bg, fg=stat_fg,
                 font=("Helvetica", 14, "bold"), pady=12, padx=18).pack(fill="x")

        spacer(body, 24)
        hsep(body)
        spacer(body, 24)

        # IH#5 toggle
        tog_text = "↩  Mark as Unwatched" if is_w else "✓  Mark as Watched"
        tog_bg   = GRAY_BTN if is_w else PURPLE
        btn(body, tog_text, lambda: self.on_toggle(self.movie),
            bg=tog_bg, fs=14, py=14).pack(fill="x")

        tk.Label(body, text="You can reverse this — click again to toggle.",
                 bg=BG_MID, fg=TEXT_HINT,
                 font=("Helvetica", 12, "italic")).pack(pady=(10,32))

        # IH#8 remove
        remove_wrap = tk.Frame(body, bg="#180c0c", pady=18, padx=16)
        remove_wrap.pack(fill="x")
        btn(remove_wrap, "🗑   Remove from Watchlist", self._remove,
            bg=RED, fs=14, py=13).pack(fill="x")
        tk.Label(remove_wrap,
                 text="⚠  A confirmation dialog will appear before removal.",
                 bg="#180c0c", fg="#d07070",
                 font=("Helvetica", 12, "italic")).pack(pady=(10,0))

    def _remove(self):
        if messagebox.askyesno("Remove Movie",
                               f"Remove \"{self.movie['title']}\" from your watchlist?",
                               icon="warning"):
            self.on_remove(self.movie)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class MainScreen(tk.Frame):
    def __init__(self, master, watchlist, on_add, on_detail, on_toggle, on_remove):
        super().__init__(master, bg=BG_MID)
        self.watchlist  = watchlist
        self.on_add     = on_add
        self.on_detail  = on_detail
        self.on_toggle  = on_toggle
        self.on_remove  = on_remove
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        self._tab_btns  = {}
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎬  My Movie Watchlist",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Helvetica", 18, "bold")).pack(side="left", padx=20)
        hsep(self, BG_DARK)

        # IH#1 benefit banner
        banner = tk.Frame(self, bg="#0d1525", pady=13)
        banner.pack(fill="x")
        tk.Label(banner,
                 text="Track movies you want to watch — add, organize, and never forget a title again.",
                 bg="#0d1525", fg=TEXT_HINT,
                 font=("Helvetica", 13, "italic")).pack()
        hsep(self)

        # IH#4 search bar
        sf = tk.Frame(self, bg=BG_MID, padx=18, pady=13)
        sf.pack(fill="x")
        sc = tk.Frame(sf, bg=BG_CARD,
                      highlightbackground=BORDER, highlightthickness=1)
        sc.pack(fill="x")
        tk.Label(sc, text="🔍", bg=BG_CARD, fg=TEXT_SUB,
                 font=("Helvetica", 15)).pack(side="left", padx=(13,4))
        tk.Entry(sc, textvariable=self.search_var,
                 bg=BG_CARD, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                 relief="flat", font=("Helvetica", 14),
                 ).pack(side="left", fill="x", expand=True, ipady=11, padx=6)

        # IH#3 filter tabs
        tf = tk.Frame(self, bg=BG_MID, padx=18, pady=8)
        tf.pack(fill="x")
        for label in ("All", "Unwatched", "Watched"):
            b = tk.Label(tf, text=label, cursor="hand2",
                         font=("Helvetica", 13, "bold"), padx=20, pady=9)
            b.pack(side="left", padx=(0,8))
            b.bind("<Button-1>", lambda e, l=label: self._set_filter(l))
            self._tab_btns[label] = b
        self._style_tabs()
        hsep(self)

        # Scrollable list
        lc = tk.Frame(self, bg=BG_MID)
        lc.pack(fill="both", expand=True, padx=18, pady=10)
        canvas = tk.Canvas(lc, bg=BG_MID, highlightthickness=0)
        sb = ttk.Scrollbar(lc, orient="vertical", command=canvas.yview)
        self.lf = tk.Frame(canvas, bg=BG_MID)
        self.lf.bind("<Configure>",
                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.lf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Footer
        hsep(self)
        footer = tk.Frame(self, bg=BG_DARK, pady=14)
        footer.pack(fill="x")
        btn(footer, "＋  Add Movie", self.on_add,
            bg=ORANGE, fg=BG_DARK, fs=14, px=30, py=13
            ).pack(side="right", padx=20)

        self._refresh()

    def _set_filter(self, label):
        self.filter_var.set(label)
        self._style_tabs()
        self._refresh()

    def _style_tabs(self):
        cur = self.filter_var.get()
        for label, b in self._tab_btns.items():
            if label == cur:
                b.config(bg=PURPLE, fg=TEXT_WHITE)
            else:
                b.config(bg=BG_CARD, fg=TEXT_SUB)

    def _refresh(self):
        for w in self.lf.winfo_children():
            w.destroy()
        f     = self.filter_var.get()
        query = self.search_var.get().strip().lower()
        filtered = [
            m for m in self.watchlist
            if (f == "All"
                or (f == "Watched"   and m.get("watched"))
                or (f == "Unwatched" and not m.get("watched")))
            and (not query or query in m["title"].lower())
        ]
        if not filtered:
            msg = ("Your watchlist is empty.\nPress  ＋ Add Movie  to get started!"
                   if not self.watchlist else
                   "No movies match your current search or filter.")
            tk.Label(self.lf, text=msg, bg=BG_MID, fg=TEXT_SUB,
                     font=("Helvetica", 14, "italic"),
                     wraplength=440, justify="center", pady=60).pack()
            return
        for movie in filtered:
            self._card(movie)

    def _card(self, movie):
        is_w    = movie.get("watched", False)
        card_bg = BG_CARD2 if is_w else BG_CARD

        outer = tk.Frame(self.lf, bg=BORDER, pady=1)
        outer.pack(fill="x", pady=4)
        card = tk.Frame(outer, bg=card_bg, pady=14, padx=18)
        card.pack(fill="x")

        left = tk.Frame(card, bg=card_bg)
        left.pack(side="left", fill="both", expand=True)

        badge_bg  = "#08281f" if is_w else "#1a2a46"
        badge_fg  = TEAL      if is_w else TEXT_SUB
        badge_txt = "✓ Watched" if is_w else "○ Unwatched"
        tk.Label(left, text=badge_txt, bg=badge_bg, fg=badge_fg,
                 font=("Helvetica", 11, "bold"), padx=10, pady=4).pack(anchor="w")
        spacer(left, 5)

        # IH#3 clickable title → detail
        tl = tk.Label(left, text=movie["title"], bg=card_bg,
                      fg=TEXT_WHITE, font=("Helvetica", 16, "bold"),
                      cursor="hand2", anchor="w")
        tl.pack(fill="x")
        tl.bind("<Button-1>", lambda e, m=movie: self.on_detail(m))
        tl.bind("<Enter>",    lambda e: tl.config(fg=TEXT_HINT))
        tl.bind("<Leave>",    lambda e: tl.config(fg=TEXT_WHITE))

        if movie.get("genre"):
            tk.Label(left, text=movie["genre"], bg=card_bg,
                     fg=TEXT_SUB, font=("Helvetica", 13)).pack(anchor="w")

        # IH#7 toggle from card
        right = tk.Frame(card, bg=card_bg)
        right.pack(side="right", padx=(12,0))
        tog_text = "Mark Unwatched" if is_w else "Mark Watched"
        tog_bg   = GRAY_BTN if is_w else PURPLE
        btn(right, tog_text, lambda m=movie: self.on_toggle(m),
            bg=tog_bg, fs=12, px=14, py=9).pack()


# ══════════════════════════════════════════════════════════════════════════════
#  APP CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        root.title("My Movie Watchlist")
        root.geometry("800x600")
        root.configure(bg=BG_DARK)
        root.resizable(True, True)

        t0 = time.time()
        self.watchlist = load_watchlist()
        print(f"[INFO] Loaded in {(time.time()-t0)*1000:.1f} ms")

        self.frame = None
        self._splash()

    def _clear(self):
        if self.frame:
            self.frame.destroy()

    def _splash(self):
        self._clear()
        self.frame = SplashScreen(self.root, on_enter=self._main)
        self.frame.pack(fill="both", expand=True)

    def _main(self):
        self._clear()
        self.frame = MainScreen(self.root, self.watchlist,
                                on_add    = self._add_screen,
                                on_detail = self._detail_screen,
                                on_toggle = self._toggle,
                                on_remove = self._remove)
        self.frame.pack(fill="both", expand=True)

    def _add_screen(self):
        self._clear()
        self.frame = AddMovieScreen(self.root,
                                    on_back = self._main,
                                    on_add  = self._add_movie)
        self.frame.pack(fill="both", expand=True)

    def _detail_screen(self, movie):
        self._clear()
        self.frame = MovieDetailScreen(self.root, movie,
                                       on_back   = self._main,
                                       on_toggle = self._toggle_detail,
                                       on_remove = self._remove)
        self.frame.pack(fill="both", expand=True)

    def _add_movie(self, title, genre):
        """US1 — Add Movie"""
        self.watchlist.append({"title": title, "genre": genre, "watched": False})
        save_watchlist(self.watchlist)
        self._main()

    def _toggle(self, movie):
        """US3 — Mark as Watched/Unwatched"""
        movie["watched"] = not movie.get("watched", False)
        save_watchlist(self.watchlist)
        self._main()

    def _toggle_detail(self, movie):
        movie["watched"] = not movie.get("watched", False)
        save_watchlist(self.watchlist)
        self._detail_screen(movie)

    def _remove(self, movie):
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            save_watchlist(self.watchlist)
        self._main()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
