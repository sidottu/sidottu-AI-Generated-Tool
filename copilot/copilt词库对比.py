import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import chardet  # 确保已安装chardet库

def load_file(label):
    file_path = filedialog.askopenfilename()
    label.config(text=file_path)

def read_vocab(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)['encoding']
    
    vocab = {}
    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                vocab[parts[0]] = parts[1]
            elif len(parts) == 3:
                vocab[parts[0]] = parts[1]
    return vocab

def normalize_vocab(vocab):
    normalized = {}
    for k, v in vocab.items():
        if k in normalized and v not in normalized[k]:
            normalized[k].append(v)
        else:
            normalized[k] = [v]
    return normalized

def compare_vocab(old_vocab, new_vocab):
    normalized_old = normalize_vocab(old_vocab)
    normalized_new = normalize_vocab(new_vocab)
    
    added = {k: v for k, v in normalized_new.items() if k not in normalized_old}
    removed = {k: v for k, v in normalized_old.items() if k not in normalized_new}
    changed = {k: (normalized_old[k], v) for k, v in normalized_new.items() if k in normalized_old and sorted(normalized_old[k]) != sorted(v)}
    return added, removed, changed

def compare_and_display():
    old_file = old_vocab_label.cget("text")
    new_file = new_vocab_label.cget("text")
    
    if not old_file or not new_file:
        messagebox.showwarning("文件未选择", "请先选择旧词库和新词库文件。")
        return
    
    old_vocab = read_vocab(old_file)
    new_vocab = read_vocab(new_file)
    added, removed, changed = compare_vocab(old_vocab, new_vocab)
    
    display_results(added, removed, changed)

def display_results(added, removed, changed):
    added_text_widget.config(state='normal')
    removed_text_widget.config(state='normal')
    changed_text_widget.config(state='normal')
    new_vocab_text_widget.config(state='normal')
    old_vocab_text_widget.config(state='normal')

    added_text_widget.delete('1.0', tk.END)
    removed_text_widget.delete('1.0', tk.END)
    changed_text_widget.delete('1.0', tk.END)
    new_vocab_text_widget.delete('1.0', tk.END)
    old_vocab_text_widget.delete('1.0', tk.END)

    for k, v in added.items():
        added_text_widget.insert('end', f"{k}: {', '.join(v)}\n")
        new_vocab_text_widget.insert('end', f"新增 {k}: {', '.join(v)}\n")
    
    for k, v in removed.items():
        removed_text_widget.insert('end', f"{k}: {', '.join(v)}\n")
        old_vocab_text_widget.insert('end', f"删除 {k}: {', '.join(v)}\n")
    
    for k, (old_val, new_val) in changed.items():
        changed_text_widget.insert('end', f"{k}: {', '.join(old_val)} -> {', '.join(new_val)}\n")

    added_text_widget.config(state='disabled')
    removed_text_widget.config(state='disabled')
    changed_text_widget.config(state='disabled')
    new_vocab_text_widget.config(state='disabled')
    old_vocab_text_widget.config(state='disabled')

    notebook.tab(0, text=f"新增词汇 ({len(added)})")
    notebook.tab(1, text=f"删除词汇 ({len(removed)})")
    notebook.tab(2, text=f"修改词汇 ({len(changed)})")
    notebook.tab(3, text=f"新词库")
    notebook.tab(4, text=f"旧词库")

def search_word():
    search_term = search_entry.get()
    for text_widget in [added_text_widget, removed_text_widget, changed_text_widget, new_vocab_text_widget, old_vocab_text_widget]:
        text_widget.tag_remove('highlight', '1.0', tk.END)
        if search_term:
            start_pos = text_widget.search(search_term, '1.0', tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                text_widget.tag_add('highlight', start_pos, end_pos)
                text_widget.tag_config('highlight', background='yellow')
                text_widget.see(start_pos)

root = tk.Tk()
root.title("词库对比工具")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# 文件选择部分
file_frame = ttk.Frame(main_frame)
file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

# 旧词库文件选择
ttk.Label(file_frame, text="选择旧词库文件:").grid(row=0, column=0, padx=10, pady=5)
old_vocab_label = ttk.Label(file_frame, text="", width=40)
old_vocab_label.grid(row=0, column=1, padx=10, pady=5)
ttk.Button(file_frame, text="浏览", command=lambda: load_file(old_vocab_label)).grid(row=0, column=2, padx=10, pady=5)

# 新词库文件选择
ttk.Label(file_frame, text="选择新词库文件:").grid(row=1, column=0, padx=10, pady=5)
new_vocab_label = ttk.Label(file_frame, text="", width=40)
new_vocab_label.grid(row=1, column=1, padx=10, pady=5)
ttk.Button(file_frame, text="浏览", command=lambda: load_file(new_vocab_label)).grid(row=1, column=2, padx=10, pady=5)

# 结果显示部分
notebook = ttk.Notebook(main_frame)
notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
main_frame.rowconfigure(2, weight=1)

# Scrollable frames for results
def create_scrollable_text(parent):
    frame = ttk.Frame(parent)
    text_widget = tk.Text(frame, wrap='word')
    text_widget.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    
    text_widget.config(yscrollcommand=scrollbar.set)
    return frame, text_widget

added_frame, added_text_widget = create_scrollable_text(notebook)
notebook.add(added_frame, text="新增词汇")

removed_frame, removed_text_widget = create_scrollable_text(notebook)
notebook.add(removed_frame, text="删除词汇")

changed_frame, changed_text_widget = create_scrollable_text(notebook)
notebook.add(changed_frame, text="修改词汇")

new_vocab_frame, new_vocab_text_widget = create_scrollable_text(notebook)
notebook.add(new_vocab_frame, text="新词库")

old_vocab_frame, old_vocab_text_widget = create_scrollable_text(notebook)
notebook.add(old_vocab_frame, text="旧词库")

# 对比并显示结果标签放在最右边
compare_tab_frame = ttk.Frame(notebook)
notebook.add(compare_tab_frame, text="对比并显示结果")
notebook.bind("<<NotebookTabChanged>>", lambda e: compare_and_display() if notebook.tab(notebook.select(), "text") == "对比并显示结果" else None)

# 查找功能
search_frame = ttk.Frame(main_frame)
search_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
ttk.Label(search_frame, text="查找词汇:").pack(side="left")
search_entry = ttk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True, padx=5)
ttk.Button(search_frame, text="查找", command=search_word).pack(side="left")

root.mainloop()
