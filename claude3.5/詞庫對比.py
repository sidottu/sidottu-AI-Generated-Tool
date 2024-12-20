import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import chardet  # 自动检测文件编码

def read_vocab(file_path):
    vocab = {}
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        with open(file_path, 'r', encoding=encoding) as file:
            for line in file:
                if line.startswith('#'):
                    continue
                parts = line.strip().split()
                if len(parts) >= 2:
                    word, code = parts[0], parts[1]
                    vocab[word] = code
                elif len(parts) == 1:
                    word, code = parts[0], ''
                    vocab[word] = code
    except Exception as e:
        messagebox.showerror("错误", f"读取文件失败: {e}")
    return vocab

def compare_vocab(old_vocab, new_vocab):
    added = {k: new_vocab[k] for k in new_vocab if k not in old_vocab}
    removed = {k: old_vocab[k] for k in old_vocab if k not in new_vocab}
    changed = {k: (old_vocab[k], new_vocab[k]) for k in new_vocab if k in old_vocab and old_vocab[k] != new_vocab[k]}
    return added, removed, changed

def load_file(label):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        label.config(text=file_path)

def search_word(event=None):
    search_term = search_entry.get()
    for text_widget in [added_text, removed_text, changed_text, old_vocab_text, new_vocab_text]:
        text_widget.tag_remove('highlight', '1.0', tk.END)
        if search_term:
            start_pos = text_widget.search(search_term, '1.0', tk.END)
            while start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                text_widget.tag_add('highlight', start_pos, end_pos)
                text_widget.tag_config('highlight', background='yellow')
                text_widget.see(start_pos)
                start_pos = text_widget.search(search_term, end_pos, tk.END)

def display_results(added, removed, changed, old_vocab, new_vocab):
    # 清空之前的结果
    for widget in notebook.winfo_children():
        widget.destroy()

    global added_text, removed_text, changed_text, old_vocab_text, new_vocab_text

    # Frame for added words
    added_frame = ttk.Frame(notebook)
    notebook.add(added_frame, text=f"新增词汇 ({len(added)})")
    added_text = create_scrollable_text(added_frame)
    for k, v in added.items():
        added_text.insert('end', f"{k}: {v}\n")
    added_text.config(state='disabled')
    
    # Frame for removed words
    removed_frame = ttk.Frame(notebook)
    notebook.add(removed_frame, text=f"删除词汇 ({len(removed)})")
    removed_text = create_scrollable_text(removed_frame)
    for k, v in removed.items():
        removed_text.insert('end', f"{k}: {v}\n")
    removed_text.config(state='disabled')

    # Frame for changed words
    changed_frame = ttk.Frame(notebook)
    notebook.add(changed_frame, text=f"修改词汇 ({len(changed)})")
    changed_text = create_scrollable_text(changed_frame)
    for k, (old_val, new_val) in changed.items():
        changed_text.insert('end', f"{k}: {old_val} -> {new_val}\n")
    changed_text.config(state='disabled')

    # Frame for old vocab
    old_vocab_frame = ttk.Frame(notebook)
    notebook.add(old_vocab_frame, text=f"旧词库 ({len(old_vocab)})")
    old_vocab_text = create_scrollable_text(old_vocab_frame)
    for k, v in old_vocab.items():
        old_vocab_text.insert('end', f"{k}: {v}\n")
    old_vocab_text.config(state='disabled')
    
    # Frame for new vocab
    new_vocab_frame = ttk.Frame(notebook)
    notebook.add(new_vocab_frame, text=f"新词库 ({len(new_vocab)})")
    new_vocab_text = create_scrollable_text(new_vocab_frame)
    for k, v in new_vocab.items():
        new_vocab_text.insert('end', f"{k}: {v}\n")
    new_vocab_text.config(state='disabled')

def create_scrollable_text(parent):
    text_frame = ttk.Frame(parent)
    text_frame.pack(expand=True, fill='both')

    text_widget = tk.Text(text_frame, wrap='word')
    text_widget.pack(side='left', expand=True, fill='both')

    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    scrollbar.pack(side='right', fill='y')

    text_widget.configure(yscrollcommand=scrollbar.set)
    
    return text_widget

def compare_and_display():
    old_vocab_file = old_vocab_label.cget("text")
    new_vocab_file = new_vocab_label.cget("text")

    if not old_vocab_file or not new_vocab_file:
        messagebox.showwarning("文件未选择", "请先选择旧词库和新词库文件。")
        return

    old_vocab = read_vocab(old_vocab_file)
    new_vocab = read_vocab(new_vocab_file)
    # 处理词汇在前或编码在前的情况
    old_vocab.update({v: k for k, v in old_vocab.items() if v not in old_vocab})
    new_vocab.update({v: k for k, v in new_vocab.items() if v not in new_vocab})
    added, removed, changed = compare_vocab(old_vocab, new_vocab)

    display_results(added, removed, changed, old_vocab, new_vocab)

# 创建主窗口
root = tk.Tk()
root.title("词库对比工具")
root.geometry("800x600")

# 文件选择框
file_frame = ttk.Frame(root, padding="10")
file_frame.pack(fill='x', padx=10, pady=5)

tk.Label(file_frame, text="选择旧词库文件:").grid(row=0, column=0, padx=5, pady=5)
old_vocab_label = tk.Label(file_frame, text="", width=50, anchor="w", relief="sunken")
old_vocab_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(file_frame, text="浏览", command=lambda: load_file(old_vocab_label)).grid(row=0, column=2, padx=5, pady=5)

tk.Label(file_frame, text="选择新词库文件:").grid(row=1, column=0, padx=5, pady=5)
new_vocab_label = tk.Label(file_frame, text="", width=50, anchor="w", relief="sunken")
new_vocab_label.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(file_frame, text="浏览", command=lambda: load_file(new_vocab_label)).grid(row=1, column=2, padx=5, pady=5)

# 配置列的权重
file_frame.grid_columnconfigure(1, weight=1)

# 结果显示区域
result_frame = ttk.Frame(root, padding="10")
result_frame.pack(expand=True, fill='both', padx=10, pady=5)

# 标签页显示区域
notebook_frame = ttk.Frame(result_frame)
notebook_frame.pack(fill='both', expand=True)

notebook = ttk.Notebook(notebook_frame)
notebook.pack(side='left', fill='both', expand=True)

# Search functionality
global search_entry
search_frame = ttk.Frame(root, padding="10")
search_frame.pack(fill='x', padx=10, pady=5)

tk.Label(search_frame, text="查找词汇:").grid(row=0, column=0, padx=5, pady=5)
search_entry = tk.Entry(search_frame)
search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(search_frame, text="查找", command=search_word).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(search_frame, text="结果显示", command=compare_and_display).grid(row=0, column=3, padx=5, pady=5)
search_entry.bind('<Return>', search_word)

# 配置search_frame的列权重
search_frame.grid_columnconfigure(1, weight=1)

# 运行主循环
root.mainloop()
