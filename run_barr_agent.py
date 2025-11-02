#!/usr/bin/env python3
"""
Run Barr Agent: Interactive CLI for flexible assistant search by any column
"""
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from systems.barr.agents import create_barr_agents
from systems.barr.tasks import BarrTasks
from crewai import Crew

load_dotenv()

def main():
    print("\n=== Barr Assistant Search Agent ===")
    print("Cari asisten berdasarkan kolom apapun (initial, name, location, major, position, dst)")
    print("Ketik 'exit' untuk keluar.\n")

    agents = create_barr_agents()
    query_agent = agents["query_agent"]
    formatting_agent = agents["formatting_agent"]

    tasks = BarrTasks()

    while True:
        user_query = input("\n🔎 Masukkan pertanyaan/cari asisten: ").strip()
        if user_query.lower() in ["exit", "quit", "keluar"]:
            print("\n👋 Bye!")
            break
        if not user_query:
            continue

        # Create tasks
        query_task = tasks.query_database(query_agent, user_query)
        format_task = tasks.format_results(formatting_agent, [query_task])

        # Create and run crew
        crew = Crew(
            agents=[query_agent, formatting_agent],
            tasks=[query_task, format_task],
            verbose=2
        )

        print("\n⏳ Memproses...")
        result = crew.kickoff()
        print("\n=== HASIL PENCARIAN ===")
        print(result)
        print("======================\n")

if __name__ == "__main__":
    main()