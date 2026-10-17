
import math
import sys
from dataclasses import dataclass
from functools import lru_cache

THRESHOLD = 0.75
LOW_LIMIT = 0.85
MED_LIMIT = 0.50


@dataclass
class Student:
    name: str
    attended: int
    held: int
    remaining: int
    p_attend: float

    @property
    def total(self):
        return self.held + self.remaining


# Basic calculations
def current_percentage(s):
    return s.attended / s.held if s.held > 0 else 0.0


def classes_needed(s):
    return max(0, math.ceil(THRESHOLD * s.total - s.attended))


def safe_bunks(s):
    need = classes_needed(s)
    return max(0, s.remaining - need) if need <= s.remaining else 0


# Minimax bounds
def best_case(s):
    return (s.attended + s.remaining) / s.total


def worst_case(s):
    return s.attended / s.total


# Expectimax calculation
def expectimax_success(s):
    total = s.total
    p = s.p_attend

    @lru_cache(maxsize=None)
    def E(att, left):
        if left == 0:
            return 1.0 if att / total >= THRESHOLD else 0.0

        # Impossible to reach 75%
        if (att + left) / total < THRESHOLD:
            return 0.0

        # Already guaranteed to meet 75%
        if att / total >= THRESHOLD:
            return 1.0

        return (
            p * E(att + 1, left - 1)
            + (1 - p) * E(att, left - 1)
        )

    return E(s.attended, s.remaining)


# Risk classification
def classify(prob, best):
    if best < THRESHOLD:
        return "CRITICAL"
    if prob >= LOW_LIMIT:
        return "LOW RISK"
    if prob >= MED_LIMIT:
        return "MEDIUM RISK"
    return "HIGH RISK"


# Recommendations
def advice(category, s):
    need = classes_needed(s)

    if category == "CRITICAL":
        return (
            "Cannot reach 75% even with full attendance. "
            "Meet your mentor to discuss available options."
        )

    if category == "HIGH RISK":
        return (
            f"Attend at least {need} of {s.remaining} "
            "remaining classes. Seek guidance."
        )

    if category == "MEDIUM RISK":
        return (
            f"Attend {need} classes and avoid more than "
            f"{safe_bunks(s)} absences."
        )

    return (
        f"Low risk. You can miss up to {safe_bunks(s)} "
        "classes mathematically, but regular attendance is advised."
    )


# Sample student data
def sample_students():
    return [
        Student("Arun", 62, 70, 30, 0.90),
        Student("Bhavana", 48, 65, 35, 0.80),
        Student("Charan", 40, 66, 34, 0.75),
        Student("Divya", 55, 60, 40, 0.95),
        Student("Elango", 30, 62, 38, 0.70),
        Student("Farah", 45, 55, 45, 0.60),
    ]


# Read student data from keyboard
def read_students():
    n = int(input("Number of students: "))
    data = []

    for i in range(n):
        print(f"\nStudent {i + 1}")

        name = input("Name: ")
        att = int(input("Classes attended so far: "))
        held = int(input("Classes held so far: "))
        rem = int(input("Classes remaining: "))
        p = float(input("Probability of attending (0-1): "))

        if (
            held <= 0
            or rem < 0
            or att < 0
            or att > held
            or not 0 <= p <= 1
        ):
            print("Invalid data, skipping this student.")
            continue

        data.append(Student(name, att, held, rem, p))

    return data


# Analyse all students
def analyse(students):
    results = []

    for s in students:
        prob = expectimax_success(s)
        best = best_case(s)
        category = classify(prob, best)

        results.append((s, prob, best, category))

    return results


# Display report
def print_table(results):
    print("\n" + "=" * 92)
    print("ATTENDANCE RISK PREDICTION REPORT (75%)")
    print("=" * 92)

    print(
        f"{'Student':<10}{'Curr%':>8}{'Need':>10}"
        f"{'Best%':>9}{'Worst%':>10}"
        f"{'P(Safe)':>10}{'Risk%':>9}  Category"
    )
    print("-" * 92)

    for s, prob, best, cat in results:
        need = f"{classes_needed(s)}/{s.remaining}"

        print(
            f"{s.name:<10}"
            f"{100 * current_percentage(s):8.2f}"
            f"{need:>10}"
            f"{100 * best:9.2f}"
            f"{100 * worst_case(s):10.2f}"
            f"{prob:10.4f}"
            f"{100 * (1 - prob):9.2f}  {cat}"
        )


# Display recommendations
def print_advice(results):
    print("\n" + "=" * 92)
    print("RECOMMENDATIONS")
    print("=" * 92)

    for s, prob, best, cat in results:
        print(f"{s.name:<10} [{cat}] {advice(cat, s)}")


# Display summary
def print_summary(results):
    counts = {
        "LOW RISK": 0,
        "MEDIUM RISK": 0,
        "HIGH RISK": 0,
        "CRITICAL": 0,
    }

    for _, _, _, cat in results:
        counts[cat] += 1

    print("\n" + "=" * 92)
    print("SUMMARY")
    print("=" * 92)

    for category, count in counts.items():
        print(f"{category:<12}: {count}")

    if results:
        highest = max(results, key=lambda r: 1 - r[1])
        print(
            f"Highest risk student: {highest[0].name} "
            f"({100 * (1 - highest[1]):.2f}%)"
        )


# Main function
def main():
    students = (
        read_students()
        if "--input" in sys.argv
        else sample_students()
    )

    if not students:
        print("No valid student records available.")
        return

    results = analyse(students)
    print_table(results)
    print_advice(results)
    print_summary(results)


if __name__ == "__main__":
    main()
