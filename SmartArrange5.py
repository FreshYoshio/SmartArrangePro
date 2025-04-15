import os
import shutil
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import sys
import time
import threading
from PIL import Image, ImageTk
import webbrowser

# ========== GENİŞLETİLMİŞ SABİTLER ==========
EXTENSION_FOLDERS = {
    # Dokümanlar
    '.pdf': 'PDFs', '.doc': 'Word', '.docx': 'Word', '.txt': 'Text', 
    '.rtf': 'Text', '.odt': 'OpenOffice', '.xls': 'Excel', '.xlsx': 'Excel',
    '.ppt': 'PowerPoint', '.pptx': 'PowerPoint', '.csv': 'Data',
    
    # Görseller
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images',
    '.bmp': 'Images', '.svg': 'Vector', '.webp': 'Images', '.tiff': 'Images',
    '.psd': 'Photoshop', '.ai': 'Illustrator',
    
    # Videolar
    '.mp4': 'Videos', '.mov': 'Videos', '.avi': 'Videos', '.mkv': 'Videos',
    '.flv': 'Videos', '.wmv': 'Videos', '.mpeg': 'Videos', '.webm': 'Videos',
    
    # Sesler
    '.mp3': 'Audio', '.wav': 'Audio', '.ogg': 'Audio', '.m4a': 'Audio',
    '.flac': 'Audio', '.aac': 'Audio', '.wma': 'Audio',
    
    # Arşivler
    '.zip': 'Archives', '.rar': 'Archives', '.7z': 'Archives', '.tar': 'Archives',
    '.gz': 'Archives', '.bz2': 'Archives', '.iso': 'Disk Images',
    
    # Programlar
    '.exe': 'Executables', '.msi': 'Installers', '.dmg': 'Mac Installers',
    '.pkg': 'Mac Installers', '.deb': 'Linux Packages', '.rpm': 'Linux Packages',
    
    # Kodlar
    '.py': 'Python', '.js': 'JavaScript', '.html': 'Web', '.css': 'Web',
    '.php': 'PHP', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'Headers',
    '.json': 'JSON', '.xml': 'XML', '.sql': 'SQL', '.sh': 'Shell Scripts'
}

COLOR_THEMES = {
    "Dark": {
        "bg": "#2d2d2d", "primary": "#3c3f41", "secondary": "#4e5254",
        "accent": "#5294e2", "text": "#ffffff", "success": "#5cb85c",
        "warning": "#f0ad4e", "danger": "#d9534f", "highlight": "#e67e22"
    },
    "Light": {
        "bg": "#f5f5f5", "primary": "#ffffff", "secondary": "#e0e0e0",
        "accent": "#4285f4", "text": "#333333", "success": "#34a853",
        "warning": "#fbbc05", "danger": "#ea4335", "highlight": "#ff6d01"
    },
    "Ocean": {
        "bg": "#263238", "primary": "#37474f", "secondary": "#455a64",
        "accent": "#80deea", "text": "#cfd8dc", "success": "#81c784",
        "warning": "#ffb74d", "danger": "#e57373", "highlight": "#64b5f6"
    }
}

STYLE = {
    "font": ("Segoe UI", 10), "title_font": ("Segoe UI", 12, "bold"),
    "large_font": ("Segoe UI", 14), "mono_font": ("Consolas", 10),
    "button_padx": 12, "button_pady": 8, "entry_width": 25
}

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tip_window, text=self.text, justify="left",
                        background="#ffffe0", relief="solid", borderwidth=1,
                        font=("Segoe UI", 9))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ========== GELİŞMİŞ DOSYA İŞLEMLERİ ==========
class FileOrganizer:
    @staticmethod
    def organize_files(folder_path, settings):
        counter = 0
        hash_seen = {}
        
        if settings['backup']:
            FileOrganizer.create_backup(folder_path)
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    result = FileOrganizer.process_file(file_path, folder_path, settings, hash_seen)
                    if result:
                        counter += 1
        
        return counter

    @staticmethod
    def process_file(file_path, base_folder, settings, hash_seen):
        name, ext = os.path.splitext(os.path.basename(file_path))
        ext = ext.lower()
        
        # Uzantı filtresi
        if settings['extensions'] and ext not in settings['extensions']:
            return False
        
        # Kopya kontrolü
        if settings['duplicate_check']:
            if FileOrganizer.is_duplicate(file_path, hash_seen):
                FileOrganizer.move_to_folder(file_path, base_folder, "Duplicates")
                return False
        
        # Boyut kontrolü
        if settings['size_threshold'] > 0:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb >= settings['size_threshold']:
                FileOrganizer.move_to_folder(file_path, base_folder, 
                                           f"Large_Files_{settings['size_threshold']}MB+")
                return False
        
        # Özel sınıflandırma
        if settings['advanced_classify']:
            classification = FileOrganizer.classify_file(file_path, name)
            if classification:
                FileOrganizer.move_to_folder(file_path, base_folder, classification)
                return True
        
        # Uzantıya göre klasör
        folder_name = EXTENSION_FOLDERS.get(ext, "Other")
        target_folder = os.path.join(base_folder, folder_name)
        
        # Tarih klasörü
        if settings['use_date_folders']:
            date_str = FileOrganizer.get_file_date(file_path)
            target_folder = os.path.join(target_folder, date_str)
        
        os.makedirs(target_folder, exist_ok=True)
        
        # Yeniden adlandırma
        new_name = FileOrganizer.rename_file(name, ext, counter=hash_seen.get('counter', 0), 
                                            mode=settings['rename_mode'])
        target_path = os.path.join(target_folder, new_name)
        
        # Taşıma işlemi
        if os.path.exists(target_path):
            FileOrganizer.handle_duplicate(file_path, target_folder)
        else:
            shutil.move(file_path, target_path)
        
        return True

    @staticmethod
    def create_backup(folder_path):
        backup_folder = os.path.join(folder_path, "Backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(backup_folder, exist_ok=True)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                shutil.copy2(item_path, backup_folder)

    @staticmethod
    def is_duplicate(file_path, hash_seen):
        file_hash = FileOrganizer.get_file_hash(file_path)
        if file_hash in hash_seen:
            return True
        hash_seen[file_hash] = True
        return False

    @staticmethod
    def move_to_folder(file_path, base_folder, folder_name):
        target_folder = os.path.join(base_folder, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        shutil.move(file_path, os.path.join(target_folder, os.path.basename(file_path)))

    @staticmethod
    def classify_file(file_path, filename):
        filename_lower = filename.lower()
        if any(tag in filename_lower for tag in ['final', 'completed']):
            return "Final_Versions"
        elif any(tag in filename_lower for tag in ['draft', 'temp']):
            return "Drafts"
        elif any(tag in filename_lower for tag in ['screenshot', 'scrnsht']):
            return "Screenshots"
        return None

    @staticmethod
    def rename_file(name, ext, counter=0, mode="none"):
        if mode == "auto":
            return f"{name.replace(' ', '_').lower()}_{counter}{ext}"
        elif mode == "clean":
            return f"{name.strip()}{ext}"
        return f"{name}{ext}"

    @staticmethod
    def get_file_date(file_path):
        try:
            timestamp = os.path.getmtime(file_path)
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        except:
            return "Unknown_Date"

    @staticmethod
    def get_file_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def handle_duplicate(file_path, target_folder):
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        counter = 1
        while True:
            new_name = f"{name}_{counter}{ext}"
            new_path = os.path.join(target_folder, new_name)
            if not os.path.exists(new_path):
                shutil.move(file_path, new_path)
                break
            counter += 1

# ========== GELİŞMİŞ ARAYÜZ BİLEŞENLERİ ==========
class SettingsWizard(tk.Toplevel):
    def __init__(self, parent, initial_settings):
        super().__init__(parent)
        self.title("SmartArrange Pro - Gelişmiş Ayarlar")
        self.geometry("700x550")
        self.resizable(False, False)
        self.settings = initial_settings.copy()
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_style()
        
        self.create_widgets()
        self.load_initial_settings()
    
    def configure_style(self):
        theme = COLOR_THEMES["Dark"]
        self.style.configure(".", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TButton", padding=6, font=STYLE["font"])
        self.style.configure("TCheckbutton", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TRadiobutton", background=theme["bg"], foreground=theme["text"])
        self.style.map("TButton",
                      background=[("active", theme["secondary"]), ("!disabled", theme["primary"])],
                      foreground=[("active", theme["text"]), ("!disabled", theme["text"])])
    
    def create_widgets(self):
        # Notebook (Sekmeler)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Genel Ayarlar Sekmesi
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="Genel Ayarlar")
        self.create_general_tab(general_frame)
        
        # Gelişmiş Sekme
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Gelişmiş")
        self.create_advanced_tab(advanced_frame)
        
        # Butonlar
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="İptal", command=self.destroy).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Uygula", command=self.apply_settings).pack(side="right", padx=5)
    
    def create_general_tab(self, parent):
        # Uzantı Seçimi
        ext_frame = ttk.LabelFrame(parent, text="Dosya Türleri", padding=10)
        ext_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.ext_vars = {}
        for i, ext in enumerate(EXTENSION_FOLDERS):
            var = tk.BooleanVar()
            self.ext_vars[ext] = var
            cb = ttk.Checkbutton(ext_frame, text=ext, variable=var)
            cb.grid(row=i//4, column=i%4, sticky="w", padx=5, pady=2)
        
        # Diğer Genel Ayarlar
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill="x", pady=10)
        
        self.use_date = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Tarihe göre klasörle", variable=self.use_date).pack(anchor="w")
        
        self.size_threshold_var = tk.IntVar()
        ttk.Label(options_frame, text="Büyük dosya eşiği (MB):").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.size_threshold_var, width=5).pack(anchor="w")
    
    def create_advanced_tab(self, parent):
        # Yeniden Adlandırma
        rename_frame = ttk.LabelFrame(parent, text="Yeniden Adlandırma", padding=10)
        rename_frame.pack(fill="x", padx=5, pady=5)
        
        self.rename_mode = tk.StringVar()
        ttk.Radiobutton(rename_frame, text="Adlandırma yapma", variable=self.rename_mode, value="none").pack(anchor="w")
        ttk.Radiobutton(rename_frame, text="Otomatik adlandır", variable=self.rename_mode, value="auto").pack(anchor="w")
        ttk.Radiobutton(rename_frame, text="Temizle", variable=self.rename_mode, value="clean").pack(anchor="w")
        
        # Gelişmiş Özellikler
        adv_frame = ttk.LabelFrame(parent, text="Gelişmiş Özellikler", padding=10)
        adv_frame.pack(fill="x", padx=5, pady=5)
        
        self.backup_var = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Yedekleme yap", variable=self.backup_var).pack(anchor="w")
        
        self.duplicate_var = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Kopya kontrolü", variable=self.duplicate_var).pack(anchor="w")
        
        self.advanced_classify_var = tk.BooleanVar()
        ttk.Checkbutton(adv_frame, text="Gelişmiş sınıflandırma", variable=self.advanced_classify_var).pack(anchor="w")
    
    def load_initial_settings(self):
        # Uzantılar
        for ext, var in self.ext_vars.items():
            var.set(ext in self.settings['extensions'])
        
        # Diğer ayarlar
        self.use_date.set(self.settings['use_date_folders'])
        self.size_threshold_var.set(self.settings['size_threshold'])
        self.rename_mode.set(self.settings['rename_mode'])
        self.backup_var.set(self.settings['backup'])
        self.duplicate_var.set(self.settings['duplicate_check'])
        self.advanced_classify_var.set(self.settings['advanced_classify'])
    
    def apply_settings(self):
        # Uzantılar
        self.settings['extensions'] = [ext for ext, var in self.ext_vars.items() if var.get()]
        
        # Diğer ayarlar
        self.settings.update({
            'use_date_folders': self.use_date.get(),
            'size_threshold': self.size_threshold_var.get(),
            'rename_mode': self.rename_mode.get(),
            'backup': self.backup_var.get(),
            'duplicate_check': self.duplicate_var.get(),
            'advanced_classify': self.advanced_classify_var.get()
        })
        
        self.destroy()

# ========== ANA UYGULAMA ==========
class SmartArrangePro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartArrange Pro 2.0")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # Varsayılan ayarlar
        self.settings = {
            'extensions': list(EXTENSION_FOLDERS.keys()),
            'use_date_folders': True,
            'size_threshold': 10,
            'rename_mode': "none",
            'backup': True,
            'duplicate_check': True,
            'advanced_classify': False
        }
        
        # Temayı ayarla
        self.current_theme = "Dark"
        self.set_theme()
        
        # Arayüzü oluştur
        self.create_widgets()
    
    def set_theme(self):
        theme = COLOR_THEMES[self.current_theme]
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Genel stil ayarları
        self.configure(bg=theme["bg"])
        self.style.configure(".", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TLabel", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TButton", padding=6, font=STYLE["font"])
        self.style.configure("TEntry", fieldbackground=theme["primary"], foreground=theme["text"])
        self.style.configure("TCombobox", fieldbackground=theme["primary"], foreground=theme["text"])
        self.style.configure("TCheckbutton", background=theme["bg"], foreground=theme["text"])
        self.style.configure("TRadiobutton", background=theme["bg"], foreground=theme["text"])
        
        # Buton haritaları
        self.style.map("TButton",
                      background=[("active", theme["secondary"]), ("!disabled", theme["primary"])],
                      foreground=[("active", theme["text"]), ("!disabled", theme["text"])])
    
    def create_widgets(self):
        # Başlık Çubuğu
        self.create_header()
        
        # Ana İçerik
        self.create_main_content()
        
        # Durum Çubuğu
        self.create_status_bar()
    
    def create_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Logo ve Başlık
        logo_label = ttk.Label(header_frame, text="📂", font=("Segoe UI", 24))
        logo_label.pack(side="left", padx=5)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", fill="y")
        
        ttk.Label(title_frame, text="SmartArrange Pro", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(title_frame, text="Profesyonel Dosya Organizasyon Sistemi", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        # Araç Butonları
        tool_frame = ttk.Frame(header_frame)
        tool_frame.pack(side="right")
        
        ttk.Button(tool_frame, text="⚙️", width=3, command=self.open_settings).pack(side="left", padx=2)
        ttk.Button(tool_frame, text="?", width=3, command=self.show_help).pack(side="left", padx=2)
    
    def create_main_content(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sol Panel - Klasör Seçimi ve İşlemler
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)
        
        self.create_folder_controls(left_frame)
        self.create_quick_actions(left_frame)
        
        # Sağ Panel - Ön İzleme
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.create_preview_panel(right_frame)
    
    def create_folder_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Klasör Yönetimi", padding=10)
        frame.pack(fill="x", pady=5)
        
        # Klasör Seçimi
        ttk.Button(frame, text="Klasör Seç", command=self.select_folder).pack(fill="x", pady=5)
        
        self.folder_path_var = tk.StringVar()
        folder_entry = ttk.Entry(frame, textvariable=self.folder_path_var, state="readonly")
        folder_entry.pack(fill="x", pady=5)
        
        # Hızlı Erişim
        ttk.Label(frame, text="Hızlı Erişim:").pack(anchor="w", pady=(10, 0))
        quick_access_frame = ttk.Frame(frame)
        quick_access_frame.pack(fill="x", pady=5)
        
        self.quick_folders = ["Belgeler", "Masaüstü", "İndirilenler"]
        for folder in self.quick_folders:
            ttk.Button(quick_access_frame, text=folder, command=lambda f=folder: self.set_quick_folder(f),
                      style="Small.TButton").pack(side="left", padx=2, fill="x", expand=True)
    
    def create_quick_actions(self, parent):
        frame = ttk.LabelFrame(parent, text="Hızlı İşlemler", padding=10)
        frame.pack(fill="x", pady=5)
        
        ttk.Button(frame, text="Düzenlemeyi Başlat", command=self.start_organizing,
                  style="Accent.TButton").pack(fill="x", pady=5)
        
        ttk.Button(frame, text="Klasörü Düzleştir", command=self.flatten_folder).pack(fill="x", pady=5)
        
        ttk.Button(frame, text="Önizlemeyi Yenile", command=self.refresh_preview).pack(fill="x", pady=5)
        
        # İstatistikler
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill="x", pady=(10, 0))
        
        self.file_count_var = tk.StringVar(value="Dosya: 0")
        ttk.Label(stats_frame, textvariable=self.file_count_var).pack(side="left")
        
        self.folder_count_var = tk.StringVar(value="Klasör: 0")
        ttk.Label(stats_frame, textvariable=self.folder_count_var).pack(side="right")
    
    def create_preview_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Dosya Önizleme", padding=10)
        frame.pack(fill="both", expand=True)
        
        # Araç Çubuğu
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(fill="x", pady=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        search_entry.bind("<KeyRelease>", self.filter_preview)
        
        ttk.Button(toolbar_frame, text="Ara", style="Small.TButton").pack(side="left")
        
        # Önizleme Listesi
        self.preview_listbox = tk.Listbox(frame, bg=COLOR_THEMES[self.current_theme]["primary"],
                                        fg=COLOR_THEMES[self.current_theme]["text"],
                                        font=STYLE["mono_font"], selectbackground=COLOR_THEMES[self.current_theme]["accent"],
                                        selectforeground=COLOR_THEMES[self.current_theme]["text"], borderwidth=0)
        self.preview_listbox.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        self.preview_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.preview_listbox.yview)
        
        # Bağlam Menüsü
        self.create_context_menu()
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Aç", command=self.open_selected_file)
        self.context_menu.add_command(label="Klasörü Aç", command=self.open_containing_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Yeniden Adlandır", command=self.rename_file)
        self.context_menu.add_command(label="Sil", command=self.delete_file)
        
        self.preview_listbox.bind("<Button-3>", self.show_context_menu)
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Hazır")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")
        
        ttk.Label(status_frame, text="SmartArrange Pro 2.0").pack(side="right")
    
    # ========== İŞLEVLER ==========
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_var.set(folder_path)
            self.update_preview()
    
    def set_quick_folder(self, folder_name):
        special_folders = {
            "Belgeler": os.path.expanduser("~/Documents"),
            "Masaüstü": os.path.expanduser("~/Desktop"),
            "İndirilenler": os.path.expanduser("~/Downloads")
        }
        
        if folder_name in special_folders:
            self.folder_path_var.set(special_folders[folder_name])
            self.update_preview()
    
    def update_preview(self):
        folder_path = self.folder_path_var.get()
        if folder_path and os.path.isdir(folder_path):
            self.preview_listbox.delete(0, tk.END)
            for item in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, item)):
                    self.preview_listbox.insert(tk.END, item)
            
            self.update_stats()
    
    def update_stats(self):
        folder_path = self.folder_path_var.get()
        if folder_path and os.path.isdir(folder_path):
            file_count = sum(1 for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))
            dir_count = sum(1 for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)))
            
            self.file_count_var.set(f"Dosya: {file_count}")
            self.folder_count_var.set(f"Klasör: {dir_count}")
    
    def filter_preview(self, event=None):
        query = self.search_var.get().lower()
        folder_path = self.folder_path_var.get()
        
        if not folder_path:
            return
        
        self.preview_listbox.delete(0, tk.END)
        for item in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, item)) and query in item.lower():
                self.preview_listbox.insert(tk.END, item)
    
    def start_organizing(self):
        folder_path = self.folder_path_var.get()
        if folder_path and os.path.isdir(folder_path):
            try:
                count = FileOrganizer.organize_files(folder_path, self.settings)
                messagebox.showinfo("Başarılı", f"{count} dosya başarıyla düzenlendi!")
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Hata", f"Düzenleme sırasında hata oluştu:\n{str(e)}")
    
    def flatten_folder(self):
        folder_path = self.folder_path_var.get()
        if folder_path and os.path.isdir(folder_path):
            try:
                FileOrganizer.flatten_directory(folder_path)
                messagebox.showinfo("Başarılı", "Klasör başarıyla düzleştirildi!")
                self.update_preview()
            except Exception as e:
                messagebox.showerror("Hata", f"Düzleştirme sırasında hata oluştu:\n{str(e)}")
    
    def refresh_preview(self):
        self.update_preview()
    
    def open_settings(self):
        SettingsWizard(self, self.settings)
    
    def show_help(self):
        webbrowser.open("https://example.com/smartarrange-help")
    
    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def open_selected_file(self):
        selected = self.preview_listbox.curselection()
        if selected:
            file_name = self.preview_listbox.get(selected[0])
            file_path = os.path.join(self.folder_path_var.get(), file_name)
            try:
                os.startfile(file_path)
            except:
                messagebox.showerror("Hata", "Dosya açılamadı!")
    
    def open_containing_folder(self):
        selected = self.preview_listbox.curselection()
        if selected:
            file_name = self.preview_listbox.get(selected[0])
            file_path = os.path.join(self.folder_path_var.get(), file_name)
            try:
                os.startfile(os.path.dirname(file_path))
            except:
                messagebox.showerror("Hata", "Klasör açılamadı!")
    
    def rename_file(self):
        selected = self.preview_listbox.curselection()
        if selected:
            old_name = self.preview_listbox.get(selected[0])
            old_path = os.path.join(self.folder_path_var.get(), old_name)
            
            new_name = simpledialog.askstring("Yeniden Adlandır", "Yeni dosya adı:", initialvalue=old_name)
            if new_name and new_name != old_name:
                try:
                    new_path = os.path.join(self.folder_path_var.get(), new_name)
                    os.rename(old_path, new_path)
                    self.update_preview()
                except Exception as e:
                    messagebox.showerror("Hata", f"Yeniden adlandırma başarısız:\n{str(e)}")
    
    def delete_file(self):
        selected = self.preview_listbox.curselection()
        if selected:
            file_name = self.preview_listbox.get(selected[0])
            file_path = os.path.join(self.folder_path_var.get(), file_name)
            
            if messagebox.askyesno("Onay", f"'{file_name}' silinsin mi?"):
                try:
                    os.remove(file_path)
                    self.update_preview()
                except Exception as e:
                    messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{str(e)}")

if __name__ == "__main__":
    app = SmartArrangePro()
    app.mainloop()