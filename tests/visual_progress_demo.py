#!/usr/bin/env python3
"""
Visual test to demonstrate the enhanced extraction progress UI.
This creates a visual representation of how the progress bar updates.
"""

import sys
import time
import os

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()

def demo_old_approach():
    """Demonstrate old batch-based progress updates"""
    print("\n" + "="*70)
    print("OLD APPROACH: Batch updates (batch_size=50)")
    print("="*70)
    print("Progress bar jumps in large steps, updates only every 50 files\n")
    
    total_files = 150
    batch_size = 50
    
    for i in range(0, total_files + 1, batch_size):
        current = min(i, total_files)
        print_progress_bar(current, total_files, 
                          prefix=f'Extracting', 
                          suffix=f'Files: {current}/{total_files} | Current: file_{current}.txt',
                          length=40)
        time.sleep(0.3)  # Simulate time between updates
    
    print("\n⚠️  Large gaps between updates - user sees 3 jumps instead of smooth progress")

def demo_new_approach():
    """Demonstrate new real-time progress updates"""
    print("\n" + "="*70)
    print("NEW APPROACH: Real-time updates (batch_size=1) - Like 7-Zip")
    print("="*70)
    print("Shows 'Preparing extraction...' immediately, then smooth continuous progress\n")
    
    # Show immediate feedback
    print("⏳ Preparing extraction...")
    print("   Opening archive and reading file list...")
    time.sleep(0.5)
    print()
    
    total_files = 150
    
    # Show progress for every file (in demo, show every 5th to keep it readable)
    for i in range(1, total_files + 1):
        # In real implementation, this updates for EVERY file
        # In demo, we show every 5th to keep console readable
        if i % 5 == 0 or i == total_files:
            elapsed = i * 0.02  # Simulated elapsed time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_files - i) / rate if rate > 0 else 0
            
            print_progress_bar(i, total_files, 
                              prefix=f'Extracting', 
                              suffix=f'Files: {i}/{total_files} | Rate: {rate:.0f} files/s | Est: {remaining:.1f}s | Current: file_{i}.txt',
                              length=40)
            time.sleep(0.02)  # Simulate extraction time
    
    print("\n✅ Smooth, continuous progress - user sees every file being extracted")

def demo_comparison():
    """Show side-by-side comparison"""
    print("\n" + "="*70)
    print("VISUAL COMPARISON")
    print("="*70)
    
    print("\n┌─────────────────────────────────────────────────────────────────┐")
    print("│ OLD APPROACH (batch_size=50)                                    │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print("│                                                                 │")
    print("│  [                                        ]   0%                │")
    print("│                                                                 │")
    print("│  ... long pause ...                                             │")
    print("│                                                                 │")
    print("│  [█████████████                           ]  33%                │")
    print("│                                                                 │")
    print("│  ... long pause ...                                             │")
    print("│                                                                 │")
    print("│  [██████████████████████████              ]  67%                │")
    print("│                                                                 │")
    print("│  ... long pause ...                                             │")
    print("│                                                                 │")
    print("│  [████████████████████████████████████████] 100%                │")
    print("│                                                                 │")
    print("│  ⚠️  User sees 3-4 large jumps, may think app is frozen         │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    print("\n┌─────────────────────────────────────────────────────────────────┐")
    print("│ NEW APPROACH (batch_size=1) - Like 7-Zip                       │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print("│                                                                 │")
    print("│  ⏳ Preparing extraction... (shows immediately!)                 │")
    print("│                                                                 │")
    print("│  [█                                       ]   1% | file_1.txt   │")
    print("│  [██                                      ]   5% | file_5.txt   │")
    print("│  [████                                    ]  10% | file_10.txt  │")
    print("│  [██████                                  ]  15% | file_15.txt  │")
    print("│  [████████                                ]  20% | file_20.txt  │")
    print("│  [██████████                              ]  25% | file_25.txt  │")
    print("│  ... (progress bar moves continuously) ...                      │")
    print("│  [████████████████████████████████████████] 100% | file_150.txt │")
    print("│                                                                 │")
    print("│  ✅ Smooth continuous progress, user sees every file            │")
    print("└─────────────────────────────────────────────────────────────────┘")

def main():
    """Run visual demonstration"""
    print("="*70)
    print("Enhanced Extraction Progress UI - Visual Demonstration")
    print("="*70)
    print()
    print("This demonstrates the difference between the old batch-based updates")
    print("and the new real-time updates (like 7-Zip).")
    
    # Show old approach
    demo_old_approach()
    
    # Show new approach
    demo_new_approach()
    
    # Show comparison
    demo_comparison()
    
    print("\n" + "="*70)
    print("Key Improvements Summary")
    print("="*70)
    print()
    print("1. ⚡ Real-time updates: Progress bar moves for EVERY file")
    print("2. 🎯 Immediate feedback: 'Preparing extraction...' shown instantly")
    print("3. 🔒 Thread-safe: Uses Tkinter's after() method")
    print("4. 🚫 No throttling: No artificial delays")
    print("5. 📊 Live info: File count, rate, elapsed time, estimates")
    print()
    print("✅ Result: Professional, responsive UI just like 7-Zip!")

if __name__ == '__main__':
    main()
