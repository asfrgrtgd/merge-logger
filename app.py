import os
import sys
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

def get_application_path():
  if getattr(sys, 'frozen', False):
    return os.path.dirname(sys.executable)
  else:
    return os.path.dirname(os.path.abspath(__file__))

def process_file(file_path):
  try:
    df = pd.read_csv(file_path, delimiter=';')
  except Exception as e:
    print(e)
    return
  filtered_df = df[df['looted_by__guild'] == 'Smurfing Monkeys']
  base_name = os.path.splitext(os.path.basename(file_path))[0]
  program_dir = get_application_path()
  output_folder = os.path.join(program_dir, base_name)
  os.makedirs(output_folder, exist_ok=True)
  output_file_name = base_name + "_formatted.txt"
  output_file_path = os.path.join(output_folder, output_file_name)
  try:
    filtered_df.to_csv(output_file_path, index=False, sep=';')
    print(output_file_path)
  except Exception as e:
    print(e)

def get_first_timestamp_of_formatted_txt(formatted_file_path):
  try:
    df = pd.read_csv(formatted_file_path, delimiter=';')
  except Exception as e:
    print(e)
    return None
  if df.empty:
    return None
  timestamp_str = df.iloc[0]['timestamp_utc']
  try:
    if '.' in timestamp_str:
      parts = timestamp_str.split('.')
      timestamp_str = parts[0] + 'Z'
    loot_dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
    return loot_dt
  except ValueError as e:
    print(e)
    return None

def filter_pasted_text_by_timestamp(pasted_text, loot_dt):
  lines = pasted_text.strip().splitlines()
  valid_lines = []
  header_line = '"Date"\t"Player"\t"Item"\t"Enchantment"\t"Quality"\t"Amount"'
  for line in lines:
    line = line.strip()
    if not line:
      continue
    if line == header_line:
      continue
    parts = line.split('\t')
    if len(parts) == 1:
      parts = line.split('    ')
    parts = [p.strip().strip('"') for p in parts if p.strip()]
    if not parts:
      continue
    datetime_str = parts[0]
    try:
      dt = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
    except ValueError:
      continue
    if dt >= loot_dt:
      valid_lines.append(line)
  return valid_lines

def create_merged_donatelog(valid_lines, output_folder):
  merged_file_path = os.path.join(output_folder, "merged_donatelog.txt")
  try:
    with open(merged_file_path, 'w', encoding='utf-8') as f:
      for line in valid_lines:
        f.write(line + "\n")
    print(merged_file_path)
  except Exception as e:
    print(e)

def ask_user_to_paste_and_process(loot_dt, output_folder):
  root = tk.Tk()
  root.withdraw()
  win = tk.Toplevel(root)
  win.title("Paste New Text")
  label = tk.Label(win, text="Please paste the donation log.")
  label.pack(padx=10, pady=5)
  text_area = scrolledtext.ScrolledText(win, width=80, height=20)
  text_area.pack(padx=10, pady=5)
  def on_submit():
    pasted_text = text_area.get("1.0", tk.END)
    if not pasted_text.strip():
      messagebox.showerror("Error", "Empty")
      return
    valid_lines = filter_pasted_text_by_timestamp(pasted_text, loot_dt)
    if not valid_lines:
      messagebox.showinfo("Result", "No valid lines")
      return
    create_merged_donatelog(valid_lines, output_folder)
    messagebox.showinfo("Done", "created")
    win.destroy()
    root.destroy()
    sys.exit(0)
  btn = tk.Button(win, text="Process Pasted Content", command=on_submit)
  btn.pack(pady=10)
  win.mainloop()

def main():
  root = tk.Tk()
  root.withdraw()
  file_path = filedialog.askopenfilename(
    title="Select the file",
    filetypes=[("CSV and Text files", "*.csv *.txt"), ("All files", "*.*")]
  )
  if not file_path:
    print("No file selected.")
    sys.exit(1)
  process_file(file_path)
  base_name = os.path.splitext(os.path.basename(file_path))[0]
  program_dir = get_application_path()
  output_folder = os.path.join(program_dir, base_name)
  formatted_file_path = os.path.join(output_folder, base_name + "_formatted.txt")
  loot_dt = get_first_timestamp_of_formatted_txt(formatted_file_path)
  if loot_dt is None:
    sys.exit(0)
  ask_user_to_paste_and_process(loot_dt, output_folder)

if __name__ == "__main__":
  main()
