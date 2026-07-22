"""Supervisor recommendation logic.

Kept as pure functions (no database or request objects) so they are trivial
to unit-test in isolation - which directly supports the Testing chapter.
"""


def normalise(term):
    """Lower-case and strip a topic term so comparisons ignore case/spacing."""
    return term.strip().lower()


def overlap_score(student_terms, staff_terms):
    """Return (score, sorted_shared_terms) for two collections of terms.

    The score is the number of distinct topics the student and staff member
    have in common, compared case-insensitively.
    """
    s_terms = {normalise(t) for t in student_terms if t and t.strip()}
    t_terms = {normalise(t) for t in staff_terms if t and t.strip()}
    shared = s_terms & t_terms
    return len(shared), sorted(shared)


def recommend_supervisors(student, staff_list):
    """Rank staff by how well their areas match the student's interests.

    Args:
        student: a User whose ``interests`` drive the match.
        staff_list: an iterable of staff User objects.

    Returns:
        A list of (staff, score, shared_terms) tuples with score > 0, sorted
        by score descending then staff name so ordering is deterministic.
    """
    student_terms = [i.name for i in student.interests]
    results = []
    for staff in staff_list:
        staff_terms = [a.name for a in staff.areas]
        score, shared = overlap_score(student_terms, staff_terms)
        if score > 0:
            results.append((staff, score, shared))
    results.sort(key=lambda row: (-row[1], row[0].name.lower()))
    return results
