"""
Simple CLI helpers to sanity-check Jarvix browser routing and planning.

Run from repo root:
    python -m scripts.test_browser_flows
"""

from jarvix.core.keyword_matcher import match_command
from jarvix.core.goal_planner import plan_goal


def show_match(text: str) -> None:
    print(f"INPUT : {text}")
    cmd = match_command(text)
    print(f"OUTPUT: {cmd}")
    print("-" * 40)


def show_plan(goal: str) -> None:
    print(f"GOAL  : {goal}")
    plan = plan_goal(goal)
    print(f"PLAN  : {plan.goal}")
    print("STEPS :")
    for i, s in enumerate(plan.steps, 1):
        print(f"  {i}. {s.action} {s.params}")
    print("=" * 40)


def main() -> None:
    # Keyword routing checks
    show_match("/browse amazon.in and search best gaming laptop")
    show_match("/browse amazon.in")
    show_match("open amazon and search iphone 15")

    # Planner checks (pattern-based, no LLM)
    show_plan("open amazon.in and search best gaming laptop")
    show_plan("search iphone 15 on amazon.in")
    show_plan("find price of macbook air on amazon")


if __name__ == "__main__":
    main()

