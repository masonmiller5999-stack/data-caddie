#!/usr/bin/env python3
"""Fantasy Golf Optimizer - Splash Sports League

Run weekly to get pick recommendations.

Usage:
    python main.py              # This week's recommendation
    python main.py --season     # Full season optimization
    python main.py --pick NAME  # Record a pick
    python main.py --result NAME EARNINGS  # Record result
    python main.py --summary    # Season summary
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tabulate import tabulate

from data.schedule import get_current_tournament, get_upcoming_tournaments
from data.scraper import get_tournament_details
from data.odds import fetch_tournament_odds
from model.golfer_skill import get_skill_ratings
from model.course_fit import get_course_fit_scores
from model.field_strength import calculate_field_strength
from model.expected_value import calculate_ev_for_field
from optimizer.season_optimizer import optimize_season, get_save_vs_use_analysis
from optimizer.weekly_pick import (
    get_used_golfers, record_pick, record_result, get_season_summary
)


def print_header(text):
    width = 70
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def cmd_weekly(args):
    """Show this week's pick recommendation."""
    print_header("Fantasy Golf Optimizer")

    used = get_used_golfers()
    print(f"\nGolfers already used: {len(used)}")
    if used:
        print(f"  {', '.join(sorted(used))}")

    # Get current tournament
    print("\nLoading current tournament...")
    current = get_current_tournament()
    if not current:
        print("No current/upcoming tournament found.")
        return

    print(f"\nTournament: {current['name']}")
    print(f"Date: {current['start_date']}")
    print(f"Purse: ${current['purse']:,.0f}" if current['purse'] else "Purse: TBD")
    print(f"Major: {'Yes' if current['major'] else 'No'}")
    print(f"Field: {len(current.get('field', []))} players")

    if not current.get("purse"):
        print("\nPurse not available yet. Try again closer to the tournament.")
        return

    # Get skill ratings
    print("\nCalculating skill ratings...")
    skill_ratings = get_skill_ratings()

    # Field strength
    field = current.get("field", [])
    fs_score = calculate_field_strength(field, skill_ratings)
    print(f"Field Strength: {fs_score}/100")

    # Course fit
    print("Analyzing course history...")
    player_names = [p["player_name"] for p in field if p["player_name"] not in used]
    course_fits = get_course_fit_scores(current["name"], player_names)

    # Fetch betting odds for this tournament
    print("Fetching betting odds...")
    odds_data = fetch_tournament_odds(current["name"])
    if odds_data:
        print(f"Odds loaded: {len(odds_data)} players with market odds")
    else:
        print("No odds data available (model will use skill-only weights)")

    # Calculate EVs for all players
    print("Calculating expected values...")
    all_evs = calculate_ev_for_field(
        current["name"], current["purse"], field, skill_ratings,
        course_fits, fs_score, len(field), odds_data=odds_data
    )

    # Filter out used golfers
    available_evs = [ev for ev in all_evs if ev["player_name"] not in used]

    if not available_evs:
        print("\nNo available golfers in this field!")
        return

    # Top 10 picks
    top = available_evs[:10]

    print(f"\n{'TOP 10 PICKS (by Expected Value)':^70}")
    print("-" * 70)

    table_data = []
    for i, p in enumerate(top, 1):
        row = [
            i,
            p["player_name"],
            f"${p['ev']:,.0f}",
            f"{p['skill_score']:.0f}/100",
            p["form_label"],
            p["course_label"],
            p.get("odds", "—") or "—",
            f"{p['win_prob']:.1f}%",
            f"{p['make_cut_prob']:.0f}%",
        ]
        table_data.append(row)

    headers = ["#", "Golfer", "EV ($)", "Skill", "Form", "Course", "Odds", "Win%", "Cut%"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))

    # Season-aware recommendation
    print(f"\n{'SEASON-OPTIMAL RECOMMENDATION':^70}")
    print("=" * 70)

    # Count premium events remaining (purse > current * 1.5)
    from data.schedule import get_upcoming_tournaments
    future = get_upcoming_tournaments()
    current_purse = current.get("purse", 0) or 0
    is_premium_week = current_purse >= 15_000_000

    EXCLUDED_EVENTS = {"tour championship", "hero world challenge", "good good championship"}
    premium_events = [
        t for t in future
        if t["start_date"] > current["start_date"]
        and t["status"] != "STATUS_FINAL"
        and t["purse"] >= 15_000_000
        and not any(exc in t["name"].lower() for exc in EXCLUDED_EVENTS)
    ]
    major_events = [t for t in premium_events if t.get("major")]

    # Dynamic elite threshold: top N players = number of premium events
    # This ensures we always save enough elite golfers for premium weeks
    all_available = [ev for ev in all_evs if ev["player_name"] not in used]
    all_available.sort(key=lambda x: x["skill_score"], reverse=True)

    n_premium = len(premium_events)
    # Elite = top N players by skill, where N = premium events remaining
    # Use N+2 buffer so we have slight surplus (injuries, withdrawals)
    elite_pool_size = n_premium + 2
    elite_players = all_available[:elite_pool_size]
    elite_names = [p["player_name"] for p in elite_players]
    elite_threshold = elite_players[-1]["skill_score"] if elite_players else 80
    elite_count = len(elite_players)

    print(f"  Premium events remaining: {n_premium} "
          f"(incl. {len(major_events)} majors)")
    print(f"  Elite golfers reserved: top {elite_count} "
          f"(skill >= {elite_threshold:.1f})")

    if is_premium_week:
        # This IS a premium week — use your best available
        print(f"\n  THIS IS A PREMIUM WEEK (${current_purse:,.0f} purse)")
        print(f"  -> USE YOUR BEST: {top[0]['player_name']} (EV: ${top[0]['ev']:,.0f})")
        recommended_pick = top[0]
    elif elite_count > n_premium:
        # More elite golfers than premium events — can spend one this week
        surplus = elite_count - n_premium
        print(f"\n  You have {surplus} more elite golfers than premium events.")
        print(f"  Safe to use an elite player this week.\n")
        print(f"  -> USE: {top[0]['player_name']} (EV: ${top[0]['ev']:,.0f})")
        recommended_pick = top[0]
    else:
        # Save elites for premium events — use best mid-tier player
        print(f"\n  SAVE elite golfers for the {n_premium} premium events.")
        print(f"  Upcoming premium events:")
        for pe in premium_events[:5]:
            major_tag = " [MAJOR]" if pe.get("major") else ""
            print(f"    {pe['start_date']}  {pe['name'][:35]:<35} "
                  f"${pe['purse']:,.0f}{major_tag}")
        if len(premium_events) > 5:
            print(f"    ... and {len(premium_events) - 5} more")

        # Find best non-elite pick (not in the reserved pool)
        elite_name_set = set(elite_names)
        mid_tier = [p for p in available_evs if p["player_name"] not in elite_name_set]
        if mid_tier:
            recommended_pick = mid_tier[0]
            print(f"\n  SAVE: {', '.join(elite_names[:5])} ... (for premium weeks)")
            print(f"\n  -> USE THIS WEEK: {recommended_pick['player_name']} "
                  f"(EV: ${recommended_pick['ev']:,.0f}, "
                  f"Odds: {recommended_pick.get('odds', '—')})")
        else:
            recommended_pick = top[0]
            print(f"\n  -> USE: {top[0]['player_name']} (EV: ${top[0]['ev']:,.0f})")

    print()
    print(f"  >>> PICK: {recommended_pick['player_name']} "
          f"(EV: ${recommended_pick['ev']:,.0f}) <<<")
    print()


def cmd_season(args):
    """Run full season optimization."""
    print_header("Season Optimization")

    used = get_used_golfers()
    print(f"\nGolfers used: {len(used)}")

    print("\nRunning season optimizer (this may take a minute)...")
    result = optimize_season(used, top_n_golfers=40, max_tournaments=15)

    if not result["assignments"]:
        print("No assignments found.")
        return

    print(f"\nProjected Total Season EV: ${result['total_ev']:,.0f}")
    print(f"\nOptimal Assignments (next {len(result['assignments'])} tournaments):")
    print("-" * 70)

    table_data = []
    for a in result["assignments"]:
        table_data.append([
            a["tournament_date"],
            a["tournament"][:30],
            f"${a['tournament_purse']:,.0f}" if a["tournament_purse"] else "TBD",
            a["golfer"],
            f"${a['ev']:,.0f}",
        ])

    headers = ["Date", "Tournament", "Purse", "Golfer", "EV ($)"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))

    if result["this_week"]:
        tw = result["this_week"]
        print(f"\n{'THIS WEEK':^70}")
        print("-" * 70)
        print(f"  Tournament: {tw['tournament']}")
        print(f"  Optimal Pick: {tw['optimal_pick']} (EV: ${tw['optimal_ev']:,.0f})")


def cmd_pick(args):
    """Record a pick."""
    golfer_name = " ".join(args.name)
    current = get_current_tournament()
    tournament_name = current["name"] if current else "Unknown"

    record_pick(golfer_name, tournament_name)
    print(f"\nRecorded: {golfer_name} for {tournament_name}")


def cmd_result(args):
    """Record a result."""
    golfer_name = args.golfer
    earnings = float(args.earnings)
    current = get_current_tournament()
    tournament_name = current["name"] if current else "Unknown"

    record_result(golfer_name, tournament_name, earnings)
    print(f"\nRecorded: {golfer_name} earned ${earnings:,.0f} at {tournament_name}")


def cmd_summary(args):
    """Show season summary."""
    print_header("Season Summary")

    summary = get_season_summary()
    used = get_used_golfers()

    print(f"\nTotal Earnings: ${summary['total_earnings']:,.0f}")
    print(f"Picks Made: {len(used)}")
    print(f"Results Recorded: {summary['completed']}")

    if summary["picks"]:
        print(f"\n{'PICK HISTORY':^70}")
        print("-" * 70)
        table_data = []
        for p in summary["picks"]:
            earnings_str = f"${p['earnings']:,.0f}" if p['earnings'] is not None else "Pending"
            table_data.append([p["tournament"], p["golfer"], earnings_str])
        headers = ["Tournament", "Golfer", "Earnings"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))

    # Show remaining schedule preview
    print(f"\n{'UPCOMING TOURNAMENTS':^70}")
    print("-" * 70)
    upcoming = get_upcoming_tournaments()
    upcoming_active = [t for t in upcoming if t["status"] != "STATUS_FINAL"]
    for t in upcoming_active[:8]:
        purse_str = f"${t['purse']:,.0f}" if t['purse'] else "TBD"
        major = " [MAJOR]" if t.get("major") else ""
        print(f"  {t['start_date']}  {t['name'][:35]:<35} {purse_str}{major}")


def main():
    parser = argparse.ArgumentParser(description="Fantasy Golf Optimizer")
    subparsers = parser.add_subparsers(dest="command")

    # Default (no subcommand) = weekly recommendation
    subparsers.add_parser("weekly", help="This week's recommendation")
    subparsers.add_parser("season", help="Full season optimization")

    pick_parser = subparsers.add_parser("pick", help="Record a pick")
    pick_parser.add_argument("name", nargs="+", help="Golfer name")

    result_parser = subparsers.add_parser("result", help="Record a result")
    result_parser.add_argument("golfer", help="Golfer name")
    result_parser.add_argument("earnings", help="Earnings amount")

    subparsers.add_parser("summary", help="Season summary")
    subparsers.add_parser("schedule", help="Show upcoming schedule with purses")

    args = parser.parse_args()

    commands = {
        "weekly": cmd_weekly,
        "season": cmd_season,
        "pick": cmd_pick,
        "result": cmd_result,
        "summary": cmd_summary,
        "schedule": cmd_summary,  # Reuse summary for schedule
        None: cmd_weekly,  # Default
    }

    handler = commands.get(args.command, cmd_weekly)
    handler(args)


if __name__ == "__main__":
    main()
