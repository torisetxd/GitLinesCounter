import subprocess
import re
import argparse
from datetime import datetime
from typing import Tuple, Dict
import sys
from collections import defaultdict

class CommitStats:
    def __init__(self, hash: str, author: str, date: str, message: str, insertions: int, deletions: int):
        self.hash = hash
        self.author = author
        self.date = date
        self.message = message
        self.insertions = insertions
        self.deletions = deletions

def get_commit_stats(commit_hash: str) -> CommitStats:
    # Get commit details
    result = subprocess.run(
        ['git', 'show', '--stat', '--format=%H|%an|%ad|%s', '--date=short', commit_hash],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Parse commit details
    first_line = result.stdout.split('\n')[0]
    hash, author, date, message = first_line.split('|')
    
    # Parse insertions and deletions
    insertion_pattern = r'(\d+)\s+insertion'
    deletion_pattern = r'(\d+)\s+deletion'
    
    insertions = sum(int(match) for match in re.findall(insertion_pattern, result.stdout))
    deletions = sum(int(match) for match in re.findall(deletion_pattern, result.stdout))
    
    return CommitStats(hash, author, date, message, insertions, deletions)

def count_lines_in_repo(start_date: datetime, end_date: datetime, author: str = None) -> Tuple[Dict[str, int], Dict[str, CommitStats]]:
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    git_cmd = ['git', 'log', '--since', start_date_str, '--until', end_date_str, '--pretty=format:%H']
    if author:
        git_cmd.extend(['--author', author])
    
    result = subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stats_by_author = defaultdict(lambda: {'insertions': 0, 'deletions': 0, 'commits': 0})
    commit_details = {}
    
    total_commits = len(result.stdout.splitlines())
    for idx, commit_hash in enumerate(result.stdout.splitlines(), 1):
        # Show progress
        sys.stdout.write(f'\rAnalyzing commits... {idx}/{total_commits}')
        sys.stdout.flush()
        
        stats = get_commit_stats(commit_hash)
        commit_details[commit_hash] = stats
        
        stats_by_author[stats.author]['insertions'] += stats.insertions
        stats_by_author[stats.author]['deletions'] += stats.deletions
        stats_by_author[stats.author]['commits'] += 1
    
    print()  # New line after progress bar
    return stats_by_author, commit_details

def parse_args():
    parser = argparse.ArgumentParser(description="Count lines added and removed in a Git repo.")
    parser.add_argument('--start-date', type=str, help="Start date in YYYY-MM-DD format (optional)")
    parser.add_argument('--end-date', type=str, help="End date in YYYY-MM-DD format (optional)")
    parser.add_argument('--author', type=str, help="Filter by author (optional)")
    return parser.parse_args()

def print_separator(char='─', width=60):
    print(char * width)

def main():
    args = parse_args()
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        result = subprocess.run(
            ['git', 'log', '--reverse', '--pretty=format:%ad', '--date=short'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        start_date = datetime.strptime(result.stdout.splitlines()[0], "%Y-%m-%d")

    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    else:
        end_date = datetime.today()

    print_separator('═')
    print(f"Git Repository Analysis")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    if args.author:
        print(f"Author: {args.author}")
    print_separator()

    stats_by_author, commit_details = count_lines_in_repo(start_date, end_date, args.author)
    
    # Print stats for each author
    for author, stats in stats_by_author.items():
        print(f"\nAuthor: {author}")
        print_separator('─')
        print(f"Commits:        {stats['commits']:,}")
        print(f"Lines added:    +{stats['insertions']:,}")
        print(f"Lines removed:  -{stats['deletions']:,}")
        print(f"Lines changed:   {stats['insertions'] + stats['deletions']:,}")
        print(f"Net change:     {stats['insertions'] - stats['deletions']:+,}")
    
    # Print total stats if multiple authors
    if len(stats_by_author) > 1:
        total_insertions = sum(stats['insertions'] for stats in stats_by_author.values())
        total_deletions = sum(stats['deletions'] for stats in stats_by_author.values())
        total_commits = sum(stats['commits'] for stats in stats_by_author.values())
        
        print("\nTOTAL STATISTICS")
        print_separator('─')
        print(f"Total commits:  {total_commits:,}")
        print(f"Lines added:    +{total_insertions:,}")
        print(f"Lines removed:  -{total_deletions:,}")
        print(f"Lines changed:   {total_insertions + total_deletions:,}")
        print(f"Net change:     {total_insertions - total_deletions:+,}")
    
    print_separator('═')

if __name__ == "__main__":
    main()