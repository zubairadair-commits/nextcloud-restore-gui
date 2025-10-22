#!/usr/bin/env python3
"""
Visual demonstration of Docker startup improvements.
Shows the difference between old blocking behavior and new non-blocking behavior.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

def demo_old_blocking_behavior():
    """Demonstrates the old blocking behavior (freezes UI)"""
    root = tk.Tk()
    root.title("OLD BEHAVIOR - UI Freezes During Docker Startup")
    root.geometry("600x400")
    
    # Header
    header = tk.Label(
        root, 
        text="❌ OLD BLOCKING BEHAVIOR",
        font=("Arial", 16, "bold"),
        bg="#e74c3c",
        fg="white",
        pady=10
    )
    header.pack(fill="x")
    
    # Status label
    status_label = tk.Label(
        root,
        text="Ready to start Docker",
        font=("Arial", 12),
        pady=20
    )
    status_label.pack()
    
    # Info text
    info_text = tk.Text(root, height=8, width=60, wrap="word")
    info_text.pack(pady=10, padx=20)
    info_text.insert("1.0", """Issues with OLD behavior:
    
1. UI FREEZES when you click "Start Docker"
2. Window shows "Not Responding" in title bar
3. Progress bar doesn't animate
4. You can't click any buttons
5. Docker Desktop window pops up
6. Bad user experience - looks like app crashed

Try clicking "Start Docker" below and watch the UI freeze!
""")
    info_text.config(state="disabled")
    
    # Progress bar
    progress = ttk.Progressbar(root, mode="indeterminate", length=400)
    progress.pack(pady=10)
    progress.start(10)  # Start animation
    
    # Counter to show UI is responsive
    counter_label = tk.Label(root, text="UI Updates: 0", font=("Arial", 10))
    counter_label.pack()
    
    counter = [0]
    def update_counter():
        """This will STOP updating when UI freezes"""
        counter[0] += 1
        counter_label.config(text=f"UI Updates: {counter[0]} (updating means UI is responsive)")
        root.after(100, update_counter)
    
    update_counter()
    
    def start_docker_blocking():
        """Simulates OLD blocking behavior - FREEZES UI"""
        status_label.config(text="🐳 Starting Docker... (UI FREEZING NOW)", fg="red")
        root.update_idletasks()
        
        # THIS BLOCKS THE UI - BAD!
        for i in range(10):
            time.sleep(1)  # Simulates Docker startup time
            status_label.config(text=f"🐳 Starting Docker... {i+1}s elapsed (FROZEN)")
            root.update_idletasks()  # Doesn't help - UI still frozen
        
        status_label.config(text="✓ Docker started (finally!)", fg="green")
    
    # Start button
    start_btn = tk.Button(
        root,
        text="Start Docker (OLD WAY - Will Freeze UI!)",
        font=("Arial", 12, "bold"),
        bg="#e74c3c",
        fg="white",
        pady=10,
        command=start_docker_blocking
    )
    start_btn.pack(pady=10)
    
    root.mainloop()

def demo_new_nonblocking_behavior():
    """Demonstrates the new non-blocking behavior (UI stays responsive)"""
    root = tk.Tk()
    root.title("NEW BEHAVIOR - UI Remains Responsive During Docker Startup")
    root.geometry("600x450")
    
    # Header
    header = tk.Label(
        root, 
        text="✅ NEW NON-BLOCKING BEHAVIOR",
        font=("Arial", 16, "bold"),
        bg="#27ae60",
        fg="white",
        pady=10
    )
    header.pack(fill="x")
    
    # Status label
    status_label = tk.Label(
        root,
        text="Ready to start Docker",
        font=("Arial", 12),
        pady=20
    )
    status_label.pack()
    
    # Info text
    info_text = tk.Text(root, height=10, width=60, wrap="word")
    info_text.pack(pady=10, padx=20)
    info_text.insert("1.0", """Benefits of NEW behavior:

1. UI NEVER FREEZES - always responsive
2. Live progress updates every second
3. Progress bar keeps animating smoothly
4. You can click other buttons during startup
5. Docker starts silently in background (no window)
6. Professional user experience

Try clicking "Start Docker" below and notice the UI stays responsive!
You can even click the test button while Docker is starting!
""")
    info_text.config(state="disabled")
    
    # Progress bar
    progress = ttk.Progressbar(root, mode="indeterminate", length=400)
    progress.pack(pady=10)
    progress.start(10)  # Start animation
    
    # Counter to show UI is responsive
    counter_label = tk.Label(root, text="UI Updates: 0", font=("Arial", 10))
    counter_label.pack()
    
    counter = [0]
    def update_counter():
        """This keeps updating even during Docker startup"""
        counter[0] += 1
        counter_label.config(text=f"UI Updates: {counter[0]} (updating means UI is responsive)")
        root.after(100, update_counter)
    
    update_counter()
    
    def start_docker_nonblocking():
        """Simulates NEW non-blocking behavior - UI stays responsive"""
        status_label.config(text="🐳 Docker is starting in the background...", fg="blue")
        
        # Background thread - doesn't block UI!
        def docker_startup_thread():
            for i in range(10):
                time.sleep(1)  # Simulates Docker startup time
                # Update UI using after() for thread safety
                root.after(0, lambda e=i+1: status_label.config(
                    text=f"🐳 Docker is starting... {e} seconds elapsed",
                    fg="blue"
                ))
            
            # Success message
            root.after(0, lambda: status_label.config(
                text="✓ Docker started successfully! You can now proceed with backup or restore.",
                fg="green"
            ))
        
        # Start in background thread
        threading.Thread(target=docker_startup_thread, daemon=True).start()
    
    def test_button_click():
        """Test that buttons work during Docker startup"""
        status_label.config(text="Test button clicked! UI is responsive! 🎉", fg="purple")
        root.after(2000, lambda: status_label.config(text="Ready to start Docker", fg="black"))
    
    # Button frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    
    # Start button
    start_btn = tk.Button(
        button_frame,
        text="Start Docker (NEW WAY - Non-Blocking!)",
        font=("Arial", 12, "bold"),
        bg="#27ae60",
        fg="white",
        pady=10,
        command=start_docker_nonblocking
    )
    start_btn.pack(side="left", padx=5)
    
    # Test button
    test_btn = tk.Button(
        button_frame,
        text="Test UI Responsiveness",
        font=("Arial", 12),
        bg="#3498db",
        fg="white",
        pady=10,
        command=test_button_click
    )
    test_btn.pack(side="left", padx=5)
    
    root.mainloop()

def show_comparison():
    """Shows both behaviors side by side"""
    root = tk.Tk()
    root.title("Docker Startup Improvement Comparison")
    root.geometry("800x500")
    
    # Title
    title = tk.Label(
        root,
        text="Docker Startup UI Improvements",
        font=("Arial", 18, "bold"),
        pady=20
    )
    title.pack()
    
    # Description
    desc = tk.Label(
        root,
        text="Choose which behavior to demonstrate:",
        font=("Arial", 12),
        pady=10
    )
    desc.pack()
    
    # Comparison table
    comparison_frame = tk.Frame(root)
    comparison_frame.pack(pady=20)
    
    # Headers
    tk.Label(comparison_frame, text="Feature", font=("Arial", 11, "bold"), width=30, borderwidth=1, relief="solid").grid(row=0, column=0)
    tk.Label(comparison_frame, text="OLD (Blocking)", font=("Arial", 11, "bold"), width=20, bg="#e74c3c", fg="white", borderwidth=1, relief="solid").grid(row=0, column=1)
    tk.Label(comparison_frame, text="NEW (Non-Blocking)", font=("Arial", 11, "bold"), width=20, bg="#27ae60", fg="white", borderwidth=1, relief="solid").grid(row=0, column=2)
    
    # Rows
    features = [
        ("UI Responsive", "❌ Freezes", "✅ Always"),
        ("Progress Updates", "❌ None", "✅ Live (3s)"),
        ("User Can Interact", "❌ No", "✅ Yes"),
        ("Shows 'Not Responding'", "✅ Yes", "❌ No"),
        ("Docker Window Opens", "✅ Yes", "❌ No (Silent)"),
        ("Professional Experience", "❌ No", "✅ Yes"),
    ]
    
    for i, (feature, old, new) in enumerate(features, start=1):
        tk.Label(comparison_frame, text=feature, width=30, borderwidth=1, relief="solid").grid(row=i, column=0)
        tk.Label(comparison_frame, text=old, width=20, borderwidth=1, relief="solid").grid(row=i, column=1)
        tk.Label(comparison_frame, text=new, width=20, borderwidth=1, relief="solid").grid(row=i, column=2)
    
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    tk.Button(
        button_frame,
        text="Demo OLD Blocking Behavior",
        font=("Arial", 12, "bold"),
        bg="#e74c3c",
        fg="white",
        width=25,
        pady=10,
        command=lambda: [root.destroy(), demo_old_blocking_behavior()]
    ).pack(side="left", padx=10)
    
    tk.Button(
        button_frame,
        text="Demo NEW Non-Blocking Behavior",
        font=("Arial", 12, "bold"),
        bg="#27ae60",
        fg="white",
        width=25,
        pady=10,
        command=lambda: [root.destroy(), demo_new_nonblocking_behavior()]
    ).pack(side="left", padx=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("=" * 70)
    print("Docker Startup UI Improvement Demo")
    print("=" * 70)
    print("\nThis demo shows the improvements made to Docker startup behavior:")
    print("1. OLD behavior: UI freezes, shows 'Not Responding'")
    print("2. NEW behavior: UI stays responsive, live progress updates")
    print("\nLaunching comparison window...")
    print("=" * 70)
    
    show_comparison()
