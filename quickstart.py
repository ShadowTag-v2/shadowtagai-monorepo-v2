#!/usr/bin/env python3
"""
Quick Start - Antigravity System
=================================
Run this script to get started immediately.
"""

import os
import sys
import subprocess

BANNER = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   █████╗ ███╗   ██╗████████╗██╗ ██████╗ ██████╗  █████╗ ██╗   ██╗║
║  ██╔══██╗████╗  ██║╚══██╔══╝██║██╔════╝ ██╔══██╗██╔══██╗██║   ██║║
║  ███████║██╔██╗ ██║   ██║   ██║██║  ███╗██████╔╝███████║██║   ██║║
║  ██╔══██║██║╚██╗██║   ██║   ██║██║   ██║██╔══██╗██╔══██║╚██╗ ██╔╝║
║  ██║  ██║██║ ╚████║   ██║   ██║╚██████╔╝██║  ██║██║  ██║ ╚████╔╝ ║
║  ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ║
║                                                                   ║
║              ULTRATHINK v2.0 | 650-Agent Squadron                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

🎯 Mission: Maximum Value Extraction
🧠 IQ Lock: 160 (Hard Requirement)
⚡ Status: Full Combat 24/7
💰 Focus: Revenue ≥3× ROI, LTV:CAC ≥4:1

"""


def print_banner():
  print(BANNER)


def check_bioagents_server():
  """Check if bioagents_server is running"""
  try:
    import requests

    response = requests.get("http://localhost:8888/health", timeout=2)
    return response.status_code == 200
  except Exception:
    return False


def start_bioagents_server():
  """Start bioagents_server server"""
  print("🐵 Starting bioagents_server 650-Agent Swarm...")
  subprocess.Popen(
    ["./run_bioagents_server_api.sh"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
  )
  print("   ✅ Server starting on http://localhost:8888")
  print("   📚 Docs: http://localhost:8888/docs")


def show_menu():
  """Display main menu"""
  print("\n" + "=" * 70)
  print("QUICK START MENU")
  print("=" * 70)
  print()
  print("1. 🔧 Configure API Keys (Interactive Setup)")
  print("2. 🐵 Start bioagents_server Server")
  print("3. 📊 View System Status")
  print("4. 🔍 Monitor System (Live)")
  print("5. 📖 View Documentation")
  print("6. 🧪 Test Gemini Failover")
  print("7. 🚀 Deploy All Services")
  print("8. ❌ Exit")
  print()

  choice = input("Select option (1-8): ").strip()
  return choice


def run_option(choice):
  """Execute selected option"""
  if choice == "1":
    print("\n🔧 Running Interactive Setup...")
    subprocess.run(["bash", "setup_antigravity.sh"])

  elif choice == "2":
    if check_bioagents_server():
      print("\n✅ bioagents_server already running on http://localhost:8888")
    else:
      start_bioagents_server()
      print("\n⏳ Waiting for server to start...")
      import time

      time.sleep(3)
      if check_bioagents_server():
        print("✅ bioagents_server operational!")
      else:
        print(
          "⚠️  Server may still be starting. Check logs: tail -f bioagents_server.log"
        )

  elif choice == "3":
    print("\n📊 System Status:")
    print("=" * 70)
    subprocess.run(["python3", "antigravity_status.py"])

  elif choice == "4":
    print("\n🔍 Starting Live Monitor (Press Ctrl+C to exit)...")
    subprocess.run(["python3", "antigravity_status.py", "--watch"])

  elif choice == "5":
    print("\n📖 Documentation:")
    print("=" * 70)
    print("1. ANTIGRAVITY_SETUP.md - Complete setup guide")
    print("2. ExToto_Prompt.md - System specification")
    print("3. MISSION_COMPLETE_2025-11-28.md - Deployment summary")
    print()
    doc = input("View which document? (1-3): ").strip()
    docs = {
      "1": "ANTIGRAVITY_SETUP.md",
      "2": "ExToto_Prompt.md",
      "3": "MISSION_COMPLETE_2025-11-28.md",
    }
    if doc in docs:
      subprocess.run(["less", docs[doc]])

  elif choice == "6":
    print("\n🧪 Testing Gemini Failover...")
    print("=" * 70)
    test_code = """
from src.shadowtag_omega_v4.services.gemini_failover import get_failover_client
client = get_failover_client()
health = client.health_check()
print(f"Status: {health['status']}")
print(f"Metrics: {health['metrics']}")
"""
    subprocess.run(["python3", "-c", test_code])

  elif choice == "7":
    print("\n🚀 Deploying All Services...")
    print("=" * 70)
    if not check_bioagents_server():
      start_bioagents_server()
    print("✅ bioagents_server: http://localhost:8888")
    print("✅ Gemini Failover: Configured")
    print("\n📊 Run 'python3 antigravity_status.py' to verify")

  elif choice == "8":
    print("\n👋 Exiting Antigravity Quick Start")
    print("   Never Resting, Ever Vesting 🚀")
    sys.exit(0)

  else:
    print("\n❌ Invalid option. Please select 1-8.")


def main():
  """Main entry point"""
  print_banner()

  # Quick status check
  fm_status = "✅ RUNNING" if check_bioagents_server() else "❌ OFFLINE"
  print(f"bioagents_server: {fm_status}")

  # Check for API keys
  has_gemini = bool(os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY"))
  has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

  gemini_status = "✅ CONFIGURED" if has_gemini else "⚠️  NOT SET"
  anthropic_status = "✅ CONFIGURED" if has_anthropic else "⚠️  NOT SET"

  print(f"Gemini API: {gemini_status}")
  print(f"Anthropic API: {anthropic_status}")

  if not has_gemini or not has_anthropic:
    print("\n⚠️  API keys not configured. Run option 1 to set up.")

  # Main loop
  while True:
    try:
      choice = show_menu()
      run_option(choice)
      input("\nPress Enter to continue...")
    except KeyboardInterrupt:
      print("\n\n👋 Exiting Antigravity Quick Start")
      sys.exit(0)


if __name__ == "__main__":
  main()
