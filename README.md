# AeroStructures™ | Enterprise Flight Reservation & Airport Management System
### First Semester Data Structures Mini Project | BE Computer Engineering
**Savitribai Phule Pune University (SPPU)**  
**Sandip Institute of Engineering & Management (SIEM), Nashik-422213**

---

## ✈️ 1. Executive Project Overview

**AeroStructures™** is an enterprise-grade Flight Reservation & Airport Management System engineered to provide a cohesive, real-world application of core computer science data structures and fundamental algorithms.

Unlike disjointed classroom snippets, every single module in this system is mapped directly to a business requirement of a modern international airline while strictly implementing **raw, zero-dependency data structure logic**:
- **No external frameworks** (no Django, Flask, React, or jQuery).
- **No data structure shortcuts** (no `collections.deque`, no `queue.Queue`, no `heapq`, no built-in hash cheats).
- **Pure Python 3 standard library** HTTP backend + **Semantic HTML5 / Responsive Executive CSS3 / Vanilla JS** client.

---

## 📂 2. Clean Architecture & Directory Structure

The project strictly segregates raw data structures from application services and presentation layers so there is zero confusion during code inspection and viva examination:

```text
flight_management_system/
│
├── data_structures/                 # 100% PURE, RAW DATA STRUCTURES
│   ├── __init__.py                  # Package exports
│   ├── stack.py                     # Fixed-capacity Stack (Push, Pop, Peek, Overflow, Underflow)
│   ├── queue.py                     # Circular Queue with Modulo Buffer (FIFO)
│   ├── linked_list.py               # Singly Linked List (Node, Head, Pointers, Chaining)
│   ├── hash_table.py                # Modulo Hash Table (h = key % 7) with Chaining Collision Resolution
│   ├── graph.py                     # Adjacency List Graph + Breadth-First Search (BFS)
│   └── algorithms.py                # Linear & Binary Search, Bubble & Selection Sort
│
├── services/                        # BUSINESS & WORKFLOW ENGINE
│   ├── __init__.py
│   └── airport_service.py           # Domain service connecting operations to data structures
│
├── static/                          # RESPONSIVE ENTERPRISE FRONTEND
│   ├── css/
│   │   └── style.css                # Polished executive airline styling (Responsive Light Palette)
│   ├── js/
│   │   └── app.js                   # Client controller & Live Memory Inspector synchronization
│   └── index.html                   # Semantic HTML5 Cockpit layout
│
├── report/                          # SPPU UNIVERSITY REPORT DOCUMENTATION
│   └── Mini_Project_Report.md       # Complete 7-chapter project report formatted to SIEM template
│
├── app.py                           # Zero-dependency HTTP Server (Python http.server)
└── README.md                        # Documentation and Viva preparation guide
```

---

## 🧩 3. Data Structures & Algorithm Mapping

| Feature in System | Data Structure / Algorithm | Key Concepts & Mechanics | Viva Terminology |
| :--- | :--- | :--- | :--- |
| **Action History (Undo)** | **Fixed-Size Stack** (Cap: 5) | Fixed array simulation, `top = -1`, $O(1)$ push/pop | LIFO, `Push`, `Pop`, `Peek`, **Stack Overflow**, **Stack Underflow** |
| **Check-in Waitlist** | **Circular Queue** (Cap: 5) | Array buffer with modulo arithmetic `(rear + 1) % 5` | FIFO, `Enqueue`, `Dequeue`, `Front`, `Rear`, **Queue Overflow**, **Queue Underflow** |
| **Confirmed Manifest** | **Singly Linked List** | Explicit `Node(data, next)`, `head` pointer, dynamic linking | Nodes, Pointers, Dynamic Memory, Sequential Traversal, $O(1)$ Head Insertion |
| **PNR Ticket Lookup** | **Hash Table** (Cap: 7) | Modulo hashing $h(k) = (\sum c \cdot 31^i) \pmod 7$ + Separate Chaining | Direct Access $O(1)$, **Hash Function**, **Collision Resolution**, Load Factor |
| **Flight Route Network** | **Graph & BFS** | Adjacency List `{Airport: [Neighbors]}` + Queue BFS | Vertices, Edges, Adjacency List, **Breadth-First Search**, Shortest Path |
| **Flight Directory** | **Searching & Sorting** | Linear Search, Binary Search (on sorted array), Bubble & Selection Sort | Best/Worst Time Complexity, Key Comparisons, Passes, Swaps |

---

## 🚀 4. How to Run the Application

The system requires **Python 3.8+** with **zero `pip install` commands**:

1. Open your terminal or PowerShell.
2. Navigate to the project root directory:
   ```powershell
   cd d:\rahul\flight_management_system
   ```
3. Run the application:
   ```powershell
   python app.py
   ```
4. Open your web browser and navigate to:
   ```text
   http://localhost:8000/
   ```

---

## 🎯 5. How to Demonstrate Live During Viva

1. **Demonstrate Stack Overflow**:
   - In the booking form, click "Confirm Booking" 6 times consecutively.
   - Observe the **Live Memory Inspector** on the right: the 5 slots fill up, `Top Pointer` reaches index `4`, and an explicit crimson banner displays: **"🛑 STACK OVERFLOW! Capacity 5 reached"**.
2. **Demonstrate Stack Underflow**:
   - Click "Undo Last Action (Pop Stack)" until all 5 actions are reversed.
   - Click it once more when the stack is empty (`Top: -1`).
   - The toast notification immediately warns: **"⚠️ Stack Underflow! History stack is empty; nothing to undo."**
3. **Demonstrate Queue Overflow & Underflow**:
   - In the Waitlist Desk, click "Enqueue Waitlist (+)" 5 times until the 5 circular slots fill up. The 6th click triggers **"🛑 Queue Overflow!"**.
   - Click "Dequeue & Confirm (-)" until the waitlist reaches 0. Clicking once more triggers **"⚠️ Queue Underflow!"**.
4. **Demonstrate Hash Table Modulo & Collision**:
   - Look at the **Hash Table** panel in the inspector. Notice how tickets are placed in Slots `#0` through `#6`.
   - When multiple PNRs hash to the same bucket index, an orange badge appears: **"Collision (2)"** showing the linked chain.
5. **Demonstrate Graph BFS Shortest Path**:
   - In the Route Network card, select Origin **BOM (Mumbai)** and Destination **CCU (Kolkata)**.
   - Click "Compute Shortest Route (BFS)". The algorithm outputs the exact itinerary (`BOM ➔ DEL ➔ CCU`) with 2 flight legs and the level-by-level BFS traversal order.
6. **Demonstrate Searching & Sorting Benchmarks**:
   - Click "Fare (Bubble Sort)". The flight list sorts instantly, and the benchmark card displays: **Passes: 7, Comparisons: 21, Swaps: 12, Time Complexity: O(n²)**.
   - Search for `AI-101` with **Binary Search** and observe the $O(\log n)$ comparison count!

---

## 🎓 6. Academic Credits

- **Course**: Bachelor of Engineering (Computer Engineering)
- **University**: Savitribai Phule Pune University (SPPU)
- **Institute**: Sandip Institute of Engineering & Management (SIEM), Nashik
- **Subject**: Data Structures & Algorithms (Mini Project)
- **Academic Year**: 2026–2027
