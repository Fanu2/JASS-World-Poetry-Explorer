
import sys, sqlite3, re
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextDocument
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel,
    QTextBrowser, QSplitter, QComboBox, QAbstractItemView
)

DB = Path(__file__).with_name("JASS_World_Poetry.db")

# These are structural headings/markers in some source editions.
STRUCTURAL = re.compile(
    r'^(?:TABLE OF CONTENTS|CONTENTS|INTRODUCTION|PREFACE|NOTES?|APPENDIX|'
    r'LIST OF (?:ILLUSTRATIONS|CONTENTS)|SONNETS?|CANTO\s+[IVXLCDM0-9]+|'
    r'BOOK\s+[IVXLCDM0-9]+|PART\s+[IVXLCDM0-9]+|SECTION\s+[IVXLCDM0-9]+|'
    r'\[[ivxlcdm]+\])$',
    re.I
)

def is_structural(title: str) -> bool:
    return bool(STRUCTURAL.match((title or "").strip()))

class Explorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JASS World Poetry Explorer — FINAL — 10,079 Poems")
        self.resize(1500, 900)
        self.dark = True
        self.font_size = 16
        self.current_poem_id = None
        self.bookmarks = set()
        self.con = sqlite3.connect(DB)
        self.con.row_factory = sqlite3.Row
        self.current_rows = []
        self.build_ui()
        self.apply_theme()
        self.load_languages()
        self.update_counts()

    def build_ui(self):
        root = QWidget()
        main = QVBoxLayout(root)
        main.setContentsMargins(12, 10, 12, 10)

        header = QHBoxLayout()
        title = QLabel("🌍  JASS WORLD POETRY EXPLORER")
        title.setObjectName("title")
        subtitle = QLabel("Multilingual Literary Research Workspace")
        subtitle.setObjectName("subtitle")
        header.addWidget(title)
        header.addSpacing(18)
        header.addWidget(subtitle)
        header.addStretch()

        self.lang_filter = QComboBox()
        self.lang_filter.addItem("All languages", None)
        self.lang_filter.currentIndexChanged.connect(self.on_language_filter)
        header.addWidget(self.lang_filter)
        main.addLayout(header)

        searchrow = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search poem text, titles or poets…")
        self.search.returnPressed.connect(self.search_poems)
        searchrow.addWidget(self.search, 1)
        b = QPushButton("Search"); b.clicked.connect(self.search_poems)
        clear = QPushButton("Clear"); clear.clicked.connect(self.clear_search)
        searchrow.addWidget(b); searchrow.addWidget(clear)
        main.addLayout(searchrow)

        split = QSplitter(Qt.Horizontal)

        # Left: languages
        left = QWidget(); ll = QVBoxLayout(left)
        ll.addWidget(QLabel("LANGUAGES"))
        self.languages = QListWidget()
        self.languages.itemClicked.connect(self.language_clicked)
        ll.addWidget(self.languages)
        self.language_count = QLabel("")
        ll.addWidget(self.language_count)
        split.addWidget(left)

        # Middle: works + poems
        middle = QWidget(); ml = QVBoxLayout(middle)
        ml.addWidget(QLabel("WORKS"))
        self.works = QListWidget()
        self.works.setMaximumHeight(150)
        self.works.itemClicked.connect(self.work_clicked)
        ml.addWidget(self.works)

        ml.addWidget(QLabel("POEMS"))
        self.results = QListWidget()
        self.results.itemClicked.connect(self.result_clicked)
        ml.addWidget(self.results, 1)
        self.result_count = QLabel("")
        ml.addWidget(self.result_count)
        split.addWidget(middle)

        # Right: reader
        right = QWidget(); rl = QVBoxLayout(right)
        self.info = QLabel("Select a poem")
        self.info.setObjectName("poemInfo")
        self.info.setWordWrap(True)
        rl.addWidget(self.info)

        self.reader = QTextBrowser()
        self.reader.setOpenExternalLinks(True)
        rl.addWidget(self.reader, 1)

        split.addWidget(right)
        split.setSizes([230, 450, 820])
        main.addWidget(split, 1)

        controls = QHBoxLayout()
        self.prev_btn = QPushButton("◀ Previous")
        self.next_btn = QPushButton("Next ▶")
        self.prev_btn.clicked.connect(self.prev_poem)
        self.next_btn.clicked.connect(self.next_poem)
        controls.addWidget(self.prev_btn); controls.addWidget(self.next_btn)

        copy = QPushButton("Copy Poem")
        copy.clicked.connect(self.copy_poem)
        controls.addWidget(copy)

        self.bookmark_btn = QPushButton("☆ Bookmark")
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        controls.addWidget(self.bookmark_btn)

        minus = QPushButton("A−"); minus.clicked.connect(lambda: self.change_font(-1))
        plus = QPushButton("A+"); plus.clicked.connect(lambda: self.change_font(1))
        controls.addWidget(minus); controls.addWidget(plus)

        self.theme_btn = QPushButton("☀ / ☾")
        self.theme_btn.clicked.connect(self.toggle_theme)
        controls.addWidget(self.theme_btn)

        controls.addStretch()
        self.status = QLabel("")
        controls.addWidget(self.status)
        main.addLayout(controls)

        self.setCentralWidget(root)

    def apply_theme(self):
        if self.dark:
            self.setStyleSheet("""
                QWidget { background:#0e1117; color:#e8eaf0; }
                QLineEdit, QListWidget, QTextBrowser, QComboBox {
                    background:#171c25; color:#f2f4f8; border:1px solid #303949;
                    border-radius:7px; padding:7px;
                }
                QPushButton { background:#1c2430; color:#f3f5f8;
                    border:1px solid #374255; border-radius:7px; padding:7px 12px; }
                QPushButton:hover { background:#273141; }
                QListWidget::item { padding:6px; }
                QListWidget::item:selected { background:#253957; }
                QLabel#title { font-size:23px; font-weight:700; }
                QLabel#subtitle { color:#9ba8bb; font-size:13px; }
                QLabel#poemInfo { padding:6px; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background:#f4f6f8; color:#20242b; }
                QLineEdit, QListWidget, QTextBrowser, QComboBox {
                    background:white; color:#20242b; border:1px solid #c9ced8;
                    border-radius:7px; padding:7px;
                }
                QPushButton { background:white; color:#20242b;
                    border:1px solid #c9ced8; border-radius:7px; padding:7px 12px; }
                QListWidget::item { padding:6px; }
                QListWidget::item:selected { background:#dce8f6; }
                QLabel#title { font-size:23px; font-weight:700; }
                QLabel#subtitle { color:#68717d; font-size:13px; }
                QLabel#poemInfo { padding:6px; }
            """)

    def load_languages(self):
        self.languages.clear()
        rows = self.con.execute("""
            SELECT l.language_id,l.name,COUNT(po.poem_id) n
            FROM languages l LEFT JOIN poems po ON po.language_id=l.language_id
            GROUP BY l.language_id ORDER BY l.name
        """).fetchall()
        for r in rows:
            item = QListWidgetItem(f"{r['name']}  ({r['n']})")
            item.setData(Qt.UserRole, r["language_id"])
            self.languages.addItem(item)
            self.lang_filter.addItem(r["name"], r["language_id"])
        self.show_all()

    def update_counts(self):
        total = self.con.execute("SELECT COUNT(*) FROM poems").fetchone()[0]
        actual = self.con.execute("SELECT COUNT(*) FROM poems WHERE title NOT LIKE '[%'").fetchone()[0]
        self.language_count.setText(f"Corpus: {total:,} records")
        self.status.setText(f"{actual:,} text records")

    def on_language_filter(self):
        lid = self.lang_filter.currentData()
        self.populate(language_id=lid)

    def language_clicked(self, item):
        self.lang_filter.blockSignals(True)
        idx = self.lang_filter.findData(item.data(Qt.UserRole))
        if idx >= 0: self.lang_filter.setCurrentIndex(idx)
        self.lang_filter.blockSignals(False)
        self.populate(language_id=item.data(Qt.UserRole))

    def populate(self, language_id=None, work_id=None, rows=None):
        self.works.clear()
        self.results.clear()
        self.current_rows = []

        if rows is not None:
            self.fill_results(rows)
            self.result_count.setText(f"{len(rows):,} results")
            return

        where=[]; params=[]
        if language_id:
            where.append("po.language_id=?"); params.append(language_id)
        if work_id:
            where.append("po.work_id=?"); params.append(work_id)
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        work_rows = self.con.execute(f"""
            SELECT w.work_id,w.title,COUNT(po.poem_id) n
            FROM works w LEFT JOIN poems po ON po.work_id=w.work_id
            {where_sql}
            GROUP BY w.work_id ORDER BY w.title
        """, params).fetchall()
        for r in work_rows:
            item=QListWidgetItem(f"{r['title']}  ({r['n']})")
            item.setData(Qt.UserRole,r["work_id"])
            self.works.addItem(item)

        rows2=self.con.execute(f"""
            SELECT po.poem_id,po.title,p.name poet,l.name language,w.title work
            FROM poems po
            JOIN poets p ON p.poet_id=po.poet_id
            JOIN languages l ON l.language_id=po.language_id
            LEFT JOIN works w ON w.work_id=po.work_id
            {where_sql}
            ORDER BY p.name, w.title, po.title
            LIMIT 3000
        """,params).fetchall()

        # Hide obvious structural markers from the main poem list without deleting
        # anything from the database.
        rows2=[r for r in rows2 if not is_structural(r["title"])]
        self.fill_results(rows2)
        self.result_count.setText(f"{len(rows2):,} poems")

    def work_clicked(self,item):
        # Determine language from selected language filter, if any.
        self.populate(work_id=item.data(Qt.UserRole))

    def fill_results(self, rows):
        self.results.clear()
        self.current_rows=list(rows)
        for r in rows:
            label=f"{r['title']}  —  {r['poet']}"
            item=QListWidgetItem(label)
            item.setData(Qt.UserRole,r["poem_id"])
            item.setToolTip(f"{r['poet']} · {r['work'] or 'Work not specified'}")
            self.results.addItem(item)

    def search_poems(self):
        q=self.search.text().strip()
        if not q:
            self.show_all(); return
        try:
            rows=self.con.execute("""
                SELECT po.poem_id,po.title,p.name poet,l.name language,w.title work
                FROM poems_fts f
                JOIN poems po ON po.poem_id=f.rowid
                JOIN poets p ON p.poet_id=po.poet_id
                JOIN languages l ON l.language_id=po.language_id
                LEFT JOIN works w ON w.work_id=po.work_id
                WHERE poems_fts MATCH ?
                ORDER BY rank LIMIT 1000
            """,(q,)).fetchall()
        except sqlite3.Error:
            pattern=f"%{q}%"
            rows=self.con.execute("""
                SELECT po.poem_id,po.title,p.name poet,l.name language,w.title work
                FROM poems po JOIN poets p ON p.poet_id=po.poet_id
                JOIN languages l ON l.language_id=po.language_id
                LEFT JOIN works w ON w.work_id=po.work_id
                WHERE po.title LIKE ? OR po.text LIKE ? OR p.name LIKE ?
                ORDER BY p.name,po.title LIMIT 1000
            """,(pattern,pattern,pattern)).fetchall()
        rows=[r for r in rows if not is_structural(r["title"])]
        self.works.clear()
        self.fill_results(rows)
        self.result_count.setText(f"{len(rows):,} search results")

    def clear_search(self):
        self.search.clear(); self.show_all()

    def show_all(self):
        self.lang_filter.blockSignals(True)
        self.lang_filter.setCurrentIndex(0)
        self.lang_filter.blockSignals(False)
        self.populate()

    def result_clicked(self,item):
        pid=item.data(Qt.UserRole)
        self.current_poem_id=pid
        r=self.con.execute("""
            SELECT po.*,p.name poet,l.name language,l.script,w.title work
            FROM poems po JOIN poets p ON p.poet_id=po.poet_id
            JOIN languages l ON l.language_id=po.language_id
            LEFT JOIN works w ON w.work_id=po.work_id
            WHERE po.poem_id=?
        """,(pid,)).fetchone()
        if not r: return

        self.info.setText(
            f"<b>{r['title']}</b><br>"
            f"<span style='color:#9aa7b8'>{r['poet']} · {r['language']}</span><br>"
            f"Work: {r['work'] or '—'} &nbsp; | &nbsp; Script: {r['script'] or '—'}"
        )

        raw=r["text"] or ""
        # Preserve stanza/line breaks. QTextBrowser will render plain text faithfully.
        self.reader.setPlainText(raw)
        font=QFont("Noto Serif",self.font_size)
        self.reader.setFont(font)
        self.bookmark_btn.setText("★ Bookmarked" if pid in self.bookmarks else "☆ Bookmark")
        self.reader.verticalScrollBar().setValue(0)

    def current_index(self):
        return self.results.currentRow()

    def select_index(self,i):
        if 0 <= i < self.results.count():
            self.results.setCurrentRow(i)
            self.result_clicked(self.results.item(i))

    def prev_poem(self): self.select_index(self.current_index()-1)
    def next_poem(self): self.select_index(self.current_index()+1)

    def copy_poem(self):
        if not self.current_poem_id: return
        r=self.con.execute("SELECT title,text FROM poems WHERE poem_id=?",(self.current_poem_id,)).fetchone()
        if r:
            QApplication.clipboard().setText(f"{r['title']}\n\n{r['text']}")

    def toggle_bookmark(self):
        if not self.current_poem_id: return
        if self.current_poem_id in self.bookmarks:
            self.bookmarks.remove(self.current_poem_id)
        else:
            self.bookmarks.add(self.current_poem_id)
        self.bookmark_btn.setText("★ Bookmarked" if self.current_poem_id in self.bookmarks else "☆ Bookmark")

    def change_font(self,d):
        self.font_size=max(11,min(30,self.font_size+d))
        self.reader.setFont(QFont("Noto Serif",self.font_size))

    def toggle_theme(self):
        self.dark=not self.dark
        self.apply_theme()

    def closeEvent(self,event):
        self.con.close()
        event.accept()

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName("JASS World Poetry Explorer")
    w=Explorer(); w.show()
    sys.exit(app.exec())
