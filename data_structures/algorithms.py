"""
Searching and Sorting Algorithms for Flight Directory Management
Demonstrates:
  - Linear Search: Sequential O(n) element-by-element inspection.
  - Binary Search: Divide-and-conquer O(log n) search on a sorted flight list.
  - Bubble Sort: O(n^2) iterative adjacent comparison and swapping.
  - Selection Sort: O(n^2) minimum element selection and placement.
Includes detailed metrics (comparison count, swap count, passes) for viva defense.
"""

def linear_search_flight(flights, target_flight_id):
    """
    Performs Linear Search to find a flight by its Flight ID.
    Time Complexity:
      - Best Case: O(1) (found at index 0)
      - Worst Case: O(n) (element at last index or not present)
      - Average Case: O(n)
    """
    target = str(target_flight_id).strip().upper()
    comparisons = 0

    for index, flight in enumerate(flights):
        comparisons += 1
        if str(flight.get("flight_id", "")).upper() == target:
            return {
                "found": True,
                "flight": flight,
                "index": index,
                "comparisons": comparisons,
                "algorithm": "Linear Search"
            }

    return {
        "found": False,
        "flight": None,
        "index": -1,
        "comparisons": comparisons,
        "algorithm": "Linear Search"
    }


def binary_search_flight(sorted_flights, target_flight_id):
    """
    Performs Binary Search on a list sorted by flight_id.
    Time Complexity:
      - Best Case: O(1) (target is at mid on first check)
      - Worst/Average Case: O(log n)
    Requires: The input list MUST be sorted by flight_id.
    """
    target = str(target_flight_id).strip().upper()
    low = 0
    high = len(sorted_flights) - 1
    comparisons = 0
    steps = []

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_flight = sorted_flights[mid]
        mid_id = str(mid_flight.get("flight_id", "")).upper()

        steps.append({
            "step": comparisons,
            "low": low,
            "mid": mid,
            "high": high,
            "mid_id": mid_id
        })

        if mid_id == target:
            return {
                "found": True,
                "flight": mid_flight,
                "index": mid,
                "comparisons": comparisons,
                "steps": steps,
                "algorithm": "Binary Search"
            }
        elif mid_id < target:
            low = mid + 1
        else:
            high = mid - 1

    return {
        "found": False,
        "flight": None,
        "index": -1,
        "comparisons": comparisons,
        "steps": steps,
        "algorithm": "Binary Search"
    }


def bubble_sort_flights(flights, key="fare", ascending=True):
    """
    Sorts a flight list using the classic Bubble Sort algorithm.
    Time Complexity:
      - Best Case: O(n) (with early-exit sorted flag)
      - Worst/Average Case: O(n^2)
    Space Complexity: O(1) auxiliary space (in-place)
    """
    # Create a shallow copy of the list so original order isn't permanently altered
    arr = [dict(item) for item in flights]
    n = len(arr)
    comparisons = 0
    swaps = 0
    passes = 0

    for i in range(n):
        swapped = False
        passes += 1
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = arr[j].get(key)
            val_b = arr[j + 1].get(key)

            # Compare based on order
            should_swap = (val_a > val_b) if ascending else (val_a < val_b)

            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True

        if not swapped:
            # Optimization: If no two elements were swapped in this pass, array is sorted
            break

    return {
        "sorted_flights": arr,
        "comparisons": comparisons,
        "swaps": swaps,
        "passes": passes,
        "sorted_by": key,
        "order": "Ascending" if ascending else "Descending",
        "algorithm": "Bubble Sort"
    }


def selection_sort_flights(flights, key="fare", ascending=True):
    """
    Sorts a flight list using Selection Sort.
    Time Complexity: O(n^2) in all cases (Best, Average, Worst).
    Space Complexity: O(1) auxiliary space.
    """
    arr = [dict(item) for item in flights]
    n = len(arr)
    comparisons = 0
    swaps = 0

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            val_curr = arr[j].get(key)
            val_target = arr[target_idx].get(key)

            is_better = (val_curr < val_target) if ascending else (val_curr > val_target)
            if is_better:
                target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            swaps += 1

    return {
        "sorted_flights": arr,
        "comparisons": comparisons,
        "swaps": swaps,
        "passes": n,
        "sorted_by": key,
        "order": "Ascending" if ascending else "Descending",
        "algorithm": "Selection Sort"
    }
