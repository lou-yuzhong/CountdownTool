import customtkinter as ctk
import threading
import time
import json
import os
from datetime import datetime, timedelta
import winsound
import tkinter.messagebox as messagebox
from PIL import Image, ImageDraw
import io

# 配置文件路径
CONFIG_FILE = "countdown_config.json"
HISTORY_FILE = "countdown_history.json"
STOPWATCH_HISTORY_FILE = "stopwatch_history.json"

class CountdownTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Windows 桌面倒计时工具 V2")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        
        # 布局配置
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 左侧边栏（倒计时任务管理）
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # 侧边栏标题
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="倒计时任务", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 任务列表
        self.task_list = ctk.CTkScrollableFrame(self.sidebar_frame, width=220, height=300)
        self.task_list.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # 添加任务按钮
        self.add_task_btn = ctk.CTkButton(self.sidebar_frame, text="添加倒计时", command=self.add_task)
        self.add_task_btn.grid(row=2, column=0, padx=20, pady=10)

        # 历史记录按钮
        self.history_btn = ctk.CTkButton(self.sidebar_frame, text="查看历史记录", command=self.show_history)
        self.history_btn.grid(row=3, column=0, padx=20, pady=10)

        # 秒表按钮
        self.stopwatch_btn = ctk.CTkButton(self.sidebar_frame, text="秒表功能", command=self.switch_to_stopwatch)
        self.stopwatch_btn.grid(row=4, column=0, padx=20, pady=10)

        # 倒计时按钮
        self.countdown_btn = ctk.CTkButton(self.sidebar_frame, text="倒计时功能", command=self.switch_to_countdown, state="disabled")
        self.countdown_btn.grid(row=5, column=0, padx=20, pady=10)

        # 右侧主界面（大型倒计时显示）
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 当前时间显示
        self.current_time_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=24))
        self.current_time_label.grid(row=0, column=0, padx=20, pady=10)

        # 大型倒计时显示
        self.countdown_display = ctk.CTkLabel(self.main_frame, text="00:00:00", font=ctk.CTkFont(size=120, weight="bold"))
        self.countdown_display.grid(row=1, column=0, padx=20, pady=20)

        # 任务名称显示
        self.task_name_label = ctk.CTkLabel(self.main_frame, text="无活动任务", font=ctk.CTkFont(size=32))
        self.task_name_label.grid(row=2, column=0, padx=20, pady=10)

        # 控制按钮
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.grid(row=3, column=0, padx=20, pady=20)

        self.start_btn = ctk.CTkButton(self.control_frame, text="开始", command=self.start_countdown, width=100)
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.pause_btn = ctk.CTkButton(self.control_frame, text="暂停", command=self.pause_countdown, width=100)
        self.pause_btn.grid(row=0, column=1, padx=10, pady=10)

        self.reset_btn = ctk.CTkButton(self.control_frame, text="重置", command=self.reset_countdown, width=100)
        self.reset_btn.grid(row=0, column=2, padx=10, pady=10)

        # 秒表相关控件
        self.stopwatch_display = ctk.CTkLabel(self.main_frame, text="00:00:00", font=ctk.CTkFont(size=120, weight="bold"))
        self.stopwatch_display.grid(row=1, column=0, padx=20, pady=20)
        self.stopwatch_display.grid_remove()  # 初始隐藏

        self.stopwatch_label = ctk.CTkLabel(self.main_frame, text="秒表模式", font=ctk.CTkFont(size=32))
        self.stopwatch_label.grid(row=2, column=0, padx=20, pady=10)
        self.stopwatch_label.grid_remove()  # 初始隐藏

        self.stopwatch_control_frame = ctk.CTkFrame(self.main_frame)
        self.stopwatch_control_frame.grid(row=3, column=0, padx=20, pady=20)
        
        self.stopwatch_start_btn = ctk.CTkButton(self.stopwatch_control_frame, text="开始", command=self.start_stopwatch, width=100)
        self.stopwatch_start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.stopwatch_pause_btn = ctk.CTkButton(self.stopwatch_control_frame, text="暂停", command=self.pause_stopwatch, width=100)
        self.stopwatch_pause_btn.grid(row=0, column=1, padx=10, pady=10)

        self.stopwatch_reset_btn = ctk.CTkButton(self.stopwatch_control_frame, text="重置", command=self.reset_stopwatch, width=100)
        self.stopwatch_reset_btn.grid(row=0, column=2, padx=10, pady=10)

        self.stopwatch_record_btn = ctk.CTkButton(self.stopwatch_control_frame, text="记录", command=self.record_stopwatch, width=100)
        self.stopwatch_record_btn.grid(row=0, column=3, padx=10, pady=10)

        self.stopwatch_control_frame.grid_remove()  # 初始隐藏

        # 秒表记录列表
        self.stopwatch_records_frame = ctk.CTkScrollableFrame(self.main_frame, width=600, height=150)
        self.stopwatch_records_frame.grid(row=4, column=0, padx=20, pady=10)
        self.stopwatch_records_frame.grid_remove()  # 初始隐藏

        # 数据结构
        self.tasks = []
        self.current_task = None
        self.is_running = False
        self.remaining_time = 0
        self.start_time = 0
        
        # 秒表数据
        self.stopwatch_running = False
        self.stopwatch_start_time = 0
        self.stopwatch_elapsed = 0
        self.stopwatch_records = []
        
        # 系统托盘相关
        self.tray_icon = None
        self.tray_thread = None

        # 加载配置
        self.load_config()

        # 更新当前时间
        self.update_current_time()

        # 初始化任务列表
        self.update_task_list()

        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """窗口关闭时最小化到系统托盘"""
        self.withdraw()  # 隐藏窗口而不是关闭
        
        # 保存当前任务状态
        if self.current_task:
            for task in self.tasks:
                if task["id"] == self.current_task["id"]:
                    task["remaining_seconds"] = self.remaining_time
                    break
            self.save_config()
        
        # 如果倒计时正在运行，显示托盘图标
        if self.is_running or self.stopwatch_running:
            self.show_tray_icon()

    def show_tray_icon(self):
        """显示系统托盘图标"""
        try:
            import pystray
            
            # 创建图标图像
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.rectangle([10, 10, 54, 54], fill='lightblue', outline='white', width=3)
            draw.text((20, 25), "⏰", fill='black')
            
            def on_show(icon, item):
                """显示主窗口"""
                self.after(0, self.restore_from_tray)
                icon.stop()
            
            def on_quit(icon, item):
                """退出程序"""
                self.after(0, self.exit_app)
                icon.stop()
            
            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", on_show, default=True),
                pystray.MenuItem("退出程序", on_quit)
            )
            
            self.tray_icon = pystray.Icon("CountdownTool", image, "倒计时运行中", menu)
            
            # 在新线程中运行托盘
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"系统托盘功能不可用：{e}")
            # 如果托盘功能不可用，直接退出
            self.exit_app()

    def restore_from_tray(self):
        """从系统托盘恢复窗口"""
        self.after(0, lambda: (self.deiconify(), self.focus_force()))

    def exit_app(self):
        """完全退出程序"""
        # 保存状态
        if self.current_task:
            for task in self.tasks:
                if task["id"] == self.current_task["id"]:
                    task["remaining_seconds"] = self.remaining_time
                    break
            self.save_config()
        
        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()
        
        self.destroy()

    def update_current_time(self):
        """更新当前时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.configure(text=current_time)
        self.after(1000, self.update_current_time)

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                try:
                    self.tasks = json.load(f)
                except:
                    self.tasks = []
        else:
            self.tasks = []

    def save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """加载历史记录"""
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        else:
            return []

    def save_history(self, history):
        """保存历史记录"""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_stopwatch_history(self):
        """加载秒表历史记录"""
        if os.path.exists(STOPWATCH_HISTORY_FILE):
            with open(STOPWATCH_HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return []
        else:
            return []

    def save_stopwatch_history(self, history):
        """保存秒表历史记录"""
        with open(STOPWATCH_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def add_task(self):
        """添加新倒计时任务"""
        # 创建添加任务窗口
        add_window = ctk.CTkToplevel(self)
        add_window.title("添加倒计时任务")
        add_window.geometry("400x300")
        add_window.transient(self)
        add_window.grab_set()

        # 任务名称
        ctk.CTkLabel(add_window, text="任务名称:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        task_name_entry = ctk.CTkEntry(add_window, width=200)
        task_name_entry.grid(row=0, column=1, padx=20, pady=10)

        # 小时
        ctk.CTkLabel(add_window, text="小时:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        hours_entry = ctk.CTkEntry(add_window, width=50)
        hours_entry.grid(row=1, column=1, padx=20, pady=10)
        ctk.CTkLabel(add_window, text="分钟:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        minutes_entry = ctk.CTkEntry(add_window, width=50)
        minutes_entry.grid(row=2, column=1, padx=20, pady=10)

        # 秒数
        ctk.CTkLabel(add_window, text="秒数:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        seconds_entry = ctk.CTkEntry(add_window, width=50)
        seconds_entry.grid(row=3, column=1, padx=20, pady=10)

        # 确认按钮
        def confirm_add():
            name = task_name_entry.get()
            try:
                hours = int(hours_entry.get()) if hours_entry.get() else 0
                minutes = int(minutes_entry.get()) if minutes_entry.get() else 0
                seconds = int(seconds_entry.get()) if seconds_entry.get() else 0
                total_seconds = hours * 3600 + minutes * 60 + seconds
                
                if total_seconds <= 0:
                    messagebox.showinfo("错误", "时间必须大于 0")
                    return

                if not name:
                    messagebox.showinfo("错误", "请输入任务名称")
                    return

                # 添加任务
                task = {
                    "id": len(self.tasks) + 1,
                    "name": name,
                    "total_seconds": total_seconds,
                    "remaining_seconds": total_seconds,
                    "created_at": datetime.now().isoformat()
                }
                self.tasks.append(task)
                self.save_config()
                self.update_task_list()
                add_window.destroy()
            except ValueError:
                messagebox.showinfo("错误", "请输入有效的数字")

        ctk.CTkButton(add_window, text="确认添加", command=confirm_add).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    def edit_task(self, task):
        """编辑任务"""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("编辑倒计时任务")
        edit_window.geometry("400x300")
        edit_window.transient(self)
        edit_window.grab_set()

        # 任务名称
        ctk.CTkLabel(edit_window, text="任务名称:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        task_name_entry = ctk.CTkEntry(edit_window, width=200)
        task_name_entry.grid(row=0, column=1, padx=20, pady=10)
        task_name_entry.insert(0, task["name"])

        # 小时
        ctk.CTkLabel(edit_window, text="小时:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        hours_entry = ctk.CTkEntry(edit_window, width=50)
        hours_entry.grid(row=1, column=1, padx=20, pady=10)
        ctk.CTkLabel(edit_window, text="分钟:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        minutes_entry = ctk.CTkEntry(edit_window, width=50)
        minutes_entry.grid(row=2, column=1, padx=20, pady=10)

        # 秒数
        ctk.CTkLabel(edit_window, text="秒数:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        seconds_entry = ctk.CTkEntry(edit_window, width=50)
        seconds_entry.grid(row=3, column=1, padx=20, pady=10)

        # 确认按钮
        def confirm_edit():
            name = task_name_entry.get()
            try:
                hours = int(hours_entry.get()) if hours_entry.get() else 0
                minutes = int(minutes_entry.get()) if minutes_entry.get() else 0
                seconds = int(seconds_entry.get()) if seconds_entry.get() else 0
                total_seconds = hours * 3600 + minutes * 60 + seconds
                
                if total_seconds <= 0:
                    messagebox.showinfo("错误", "时间必须大于 0")
                    return

                if not name:
                    messagebox.showinfo("错误", "请输入任务名称")
                    return

                # 更新任务
                for t in self.tasks:
                    if t["id"] == task["id"]:
                        t["name"] = name
                        t["total_seconds"] = total_seconds
                        t["remaining_seconds"] = total_seconds
                        break
                
                self.save_config()
                self.update_task_list()
                
                # 如果当前任务被编辑，更新显示
                if self.current_task and self.current_task["id"] == task["id"]:
                    self.current_task = t
                    self.remaining_time = total_seconds
                    self.task_name_label.configure(text=name)
                    self.update_countdown_display()
                
                edit_window.destroy()
            except ValueError:
                messagebox.showinfo("错误", "请输入有效的数字")

        ctk.CTkButton(edit_window, text="确认修改", command=confirm_edit).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    def delete_task(self, task):
        """删除任务"""
        if messagebox.askyesno("确认删除", f"确定要删除任务 '{task['name']}' 吗？"):
            # 从列表中移除任务
            self.tasks = [t for t in self.tasks if t["id"] != task["id"]]
            self.save_config()
            self.update_task_list()
            
            # 如果删除的是当前任务，重置显示
            if self.current_task and self.current_task["id"] == task["id"]:
                self.current_task = None
                self.remaining_time = 0
                self.is_running = False
                self.task_name_label.configure(text="无活动任务")
                self.update_countdown_display()

    def update_task_list(self):
        """更新任务列表"""
        # 清空现有任务
        for widget in self.task_list.winfo_children():
            widget.destroy()

        # 添加任务到列表
        for task in self.tasks:
            task_frame = ctk.CTkFrame(self.task_list, width=200)
            task_frame.pack(pady=5, fill="x")

            task_label = ctk.CTkLabel(task_frame, text=task["name"], width=100, anchor="w")
            task_label.pack(side="left", padx=5, pady=5)

            # 选择按钮
            select_btn = ctk.CTkButton(task_frame, text="选择", width=50, command=lambda t=task: self.select_task(t))
            select_btn.pack(side="right", padx=2, pady=5)

            # 编辑按钮
            edit_btn = ctk.CTkButton(task_frame, text="编辑", width=50, command=lambda t=task: self.edit_task(t))
            edit_btn.pack(side="right", padx=2, pady=5)

            # 删除按钮
            delete_btn = ctk.CTkButton(task_frame, text="删除", width=50, command=lambda t=task: self.delete_task(t))
            delete_btn.pack(side="right", padx=2, pady=5)

    def select_task(self, task):
        """选择任务"""
        # 保存当前任务状态
        if self.current_task:
            for t in self.tasks:
                if t["id"] == self.current_task["id"]:
                    t["remaining_seconds"] = self.remaining_time
                    break
        
        self.current_task = task
        self.remaining_time = task["remaining_seconds"]
        self.task_name_label.configure(text=task["name"])
        self.update_countdown_display()

    def update_countdown_display(self):
        """更新倒计时显示"""
        if self.remaining_time > 0:
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = "00:00:00"
        self.countdown_display.configure(text=time_str)

    def start_countdown(self):
        """开始倒计时"""
        if not self.current_task:
            messagebox.showinfo("提示", "请先选择一个任务")
            return

        if not self.is_running:
            self.is_running = True
            self.start_time = time.time() - (self.current_task["total_seconds"] - self.remaining_time)
            threading.Thread(target=self.countdown_thread, daemon=False).start()

    def pause_countdown(self):
        """暂停倒计时"""
        self.is_running = False

    def reset_countdown(self):
        """重置倒计时"""
        self.is_running = False
        if self.current_task:
            self.remaining_time = self.current_task["total_seconds"]
            self.update_countdown_display()

    def countdown_thread(self):
        """倒计时线程"""
        while self.is_running and self.remaining_time > 0:
            elapsed = time.time() - self.start_time
            self.remaining_time = max(0, self.current_task["total_seconds"] - int(elapsed))
            self.update_countdown_display()
            time.sleep(1)

        if self.remaining_time == 0 and self.current_task:
            # 倒计时结束，发出提醒
            try:
                winsound.Beep(1000, 1000)
            except:
                pass
            
            # 如果窗口隐藏了，显示托盘通知
            if not self.winfo_viewable():
                try:
                    import plyer
                    plyer.notification.notify(
                        title="倒计时结束",
                        message=f"任务 '{self.current_task['name']}' 已完成！",
                        timeout=10
                    )
                except:
                    pass
            else:
                messagebox.showinfo("倒计时结束", f"任务 '{self.current_task['name']}' 已完成！")

            # 记录历史
            history = self.load_history()
            history_entry = {
                "task_name": self.current_task["name"],
                "duration": self.current_task["total_seconds"],
                "completed_at": datetime.now().isoformat()
            }
            history.append(history_entry)
            self.save_history(history)

            # 重置任务
            self.remaining_time = self.current_task["total_seconds"]
            self.update_countdown_display()
            self.is_running = False

    def show_history(self):
        """显示历史记录"""
        history = self.load_history()
        stopwatch_history = self.load_stopwatch_history()
        
        if not history and not stopwatch_history:
            messagebox.showinfo("历史记录", "暂无历史记录")
            return

        # 创建历史记录窗口
        history_window = ctk.CTkToplevel(self)
        history_window.title("历史记录")
        history_window.geometry("800x600")
        history_window.transient(self)
        history_window.grab_set()

        # 按日期分组历史记录
        all_history = []
        
        # 添加倒计时历史
        for entry in history:
            all_history.append({
                "type": "countdown",
                "task_name": entry.get("task_name", "未知任务"),
                "duration": entry.get("duration", 0),
                "completed_at": entry.get("completed_at", datetime.now().isoformat())
            })
        
        # 添加秒表历史
        for entry in stopwatch_history:
            all_history.append({
                "type": "stopwatch",
                "task_name": entry.get("task_name", "秒表计时"),
                "duration": entry.get("duration", 0),
                "completed_at": entry.get("completed_at", datetime.now().isoformat())
            })

        # 按日期分组
        history_by_date = {}
        for entry in all_history:
            date = datetime.fromisoformat(entry['completed_at']).strftime("%Y-%m-%d")
            if date not in history_by_date:
                history_by_date[date] = []
            history_by_date[date].append(entry)

        # 计算每天的总学习时间
        daily_totals = {}
        for date, entries in history_by_date.items():
            total_seconds = sum(entry['duration'] for entry in entries)
            daily_totals[date] = total_seconds

        # 历史记录列表
        history_list = ctk.CTkScrollableFrame(history_window, width=750, height=450)
        history_list.pack(padx=20, pady=20, fill="both", expand=True)

        # 添加日期分组和统计
        for date in sorted(history_by_date.keys(), reverse=True):  # 最新的日期在前面
            # 日期标题
            date_frame = ctk.CTkFrame(history_list, width=700)
            date_frame.pack(pady=10, fill="x")
            
            # 计算当天总时间
            total_seconds = daily_totals[date]
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            total_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            date_label = ctk.CTkLabel(date_frame, text=f"日期：{date} (总计时时间：{total_str})", font=ctk.CTkFont(weight="bold"))
            date_label.pack(padx=10, pady=5, anchor="w")

            # 添加当天的历史记录
            for entry in reversed(history_by_date[date]):  # 当天最新的记录在前面
                entry_frame = ctk.CTkFrame(history_list, width=650)
                entry_frame.pack(pady=3, fill="x", padx=20)

                # 任务类型和名称
                type_text = "倒计时" if entry['type'] == "countdown" else "秒表"
                task_label = ctk.CTkLabel(entry_frame, text=f"{type_text}：{entry['task_name']}", width=250, anchor="w")
                task_label.pack(side="left", padx=10, pady=3)

                # 持续时间
                duration = entry['duration']
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                duration_label = ctk.CTkLabel(entry_frame, text=f"时长：{duration_str}", width=150, anchor="w")
                duration_label.pack(side="left", padx=10, pady=3)

                # 完成时间
                completed_at = datetime.fromisoformat(entry['completed_at']).strftime("%H:%M:%S")
                time_label = ctk.CTkLabel(entry_frame, text=f"完成：{completed_at}", width=150, anchor="w")
                time_label.pack(side="left", padx=10, pady=3)

    def switch_to_stopwatch(self):
        """切换到秒表模式"""
        # 隐藏倒计时相关控件
        self.countdown_display.grid_remove()
        self.task_name_label.grid_remove()
        self.control_frame.grid_remove()
        
        # 显示秒表相关控件
        self.stopwatch_display.grid()
        self.stopwatch_label.grid()
        self.stopwatch_control_frame.grid()
        self.stopwatch_records_frame.grid()
        
        # 更新按钮状态
        self.stopwatch_btn.configure(state="disabled")
        self.countdown_btn.configure(state="normal")
        
        # 重置秒表显示
        self.update_stopwatch_display()
        self.update_stopwatch_records()

    def switch_to_countdown(self):
        """切换到倒计时模式"""
        # 隐藏秒表相关控件
        self.stopwatch_display.grid_remove()
        self.stopwatch_label.grid_remove()
        self.stopwatch_control_frame.grid_remove()
        self.stopwatch_records_frame.grid_remove()
        
        # 显示倒计时相关控件
        self.countdown_display.grid()
        self.task_name_label.grid()
        self.control_frame.grid()
        
        # 更新按钮状态
        self.stopwatch_btn.configure(state="normal")
        self.countdown_btn.configure(state="disabled")
        
        # 重置倒计时显示
        if self.current_task:
            self.remaining_time = self.current_task["remaining_seconds"]
            self.task_name_label.configure(text=self.current_task["name"])
        else:
            self.task_name_label.configure(text="无活动任务")
        self.update_countdown_display()

    def update_stopwatch_display(self):
        """更新秒表显示"""
        elapsed = self.stopwatch_elapsed
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.stopwatch_display.configure(text=time_str)

    def start_stopwatch(self):
        """开始秒表"""
        if not self.stopwatch_running:
            self.stopwatch_running = True
            self.stopwatch_start_time = time.time() - self.stopwatch_elapsed
            threading.Thread(target=self.stopwatch_thread, daemon=False).start()

    def pause_stopwatch(self):
        """暂停秒表"""
        self.stopwatch_running = False

    def reset_stopwatch(self):
        """重置秒表"""
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0
        self.stopwatch_records = []
        self.update_stopwatch_display()
        self.update_stopwatch_records()

    def record_stopwatch(self):
        """记录秒表时间"""
        if self.stopwatch_elapsed > 0:
            record = {
                "time": self.stopwatch_elapsed,
                "timestamp": datetime.now().isoformat()
            }
            self.stopwatch_records.append(record)
            self.update_stopwatch_records()

    def stopwatch_thread(self):
        """秒表线程"""
        while self.stopwatch_running:
            self.stopwatch_elapsed = int(time.time() - self.stopwatch_start_time)
            self.update_stopwatch_display()
            time.sleep(1)

    def update_stopwatch_records(self):
        """更新秒表记录列表"""
        # 清空现有记录
        for widget in self.stopwatch_records_frame.winfo_children():
            widget.destroy()
        
        # 添加记录
        for i, record in enumerate(self.stopwatch_records, 1):
            record_frame = ctk.CTkFrame(self.stopwatch_records_frame, width=550)
            record_frame.pack(pady=3, fill="x")
            
            record_num_label = ctk.CTkLabel(record_frame, text=f"记录 {i}", width=80, anchor="w")
            record_num_label.pack(side="left", padx=10, pady=3)
            
            elapsed = record["time"]
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            time_label = ctk.CTkLabel(record_frame, text=f"时间：{time_str}", width=150, anchor="w")
            time_label.pack(side="left", padx=10, pady=3)
            
            timestamp = datetime.fromisoformat(record["timestamp"]).strftime("%H:%M:%S")
            timestamp_label = ctk.CTkLabel(record_frame, text=f"时间：{timestamp}", width=150, anchor="w")
            timestamp_label.pack(side="left", padx=10, pady=3)
            
            # 保存按钮
            save_btn = ctk.CTkButton(record_frame, text="保存", width=60, command=lambda r=record: self.save_stopwatch_record(r))
            save_btn.pack(side="right", padx=5, pady=3)

    def save_stopwatch_record(self, record):
        """保存秒表记录"""
        # 创建保存窗口
        save_window = ctk.CTkToplevel(self)
        save_window.title("保存秒表记录")
        save_window.geometry("300x150")
        save_window.transient(self)
        save_window.grab_set()
        
        # 任务名称
        ctk.CTkLabel(save_window, text="记录名称:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        task_name_entry = ctk.CTkEntry(save_window, width=150)
        task_name_entry.grid(row=0, column=1, padx=20, pady=10)
        task_name_entry.insert(0, "秒表记录")
        
        # 确认按钮
        def confirm_save():
            name = task_name_entry.get()
            if not name:
                name = "秒表记录"
            
            # 保存到历史
            history = self.load_stopwatch_history()
            history_entry = {
                "task_name": name,
                "duration": record["time"],
                "completed_at": datetime.now().isoformat()
            }
            history.append(history_entry)
            self.save_stopwatch_history(history)
            
            messagebox.showinfo("成功", "记录已保存到历史")
            save_window.destroy()
        
        ctk.CTkButton(save_window, text="保存", command=confirm_save).grid(row=1, column=0, columnspan=2, padx=20, pady=20)

if __name__ == "__main__":
    app = CountdownTool()
    app.mainloop()
