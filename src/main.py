"""main script"""

from parser import Parse


def show_menu():
    """Menu print"""
    print("\n=== MENU ===")
    print("9 — Parse another club")
    print("0 — Reset to original dataframe")
    print("1 — Sort by deltaVal ASC")
    print("2 — Sort by deltaVal DESC")
    print("3 — Sort by deltaPercent ASC")
    print("4 — Sort by deltaPercent DESC")
    print("q — Quit")
    print("============")


def main():
    """Application entry point."""
    team_url = input("Input club's URL from Transfermarkt : ")
    print("Please wait a second before data scraping")

    team_instance = Parse(team_url)
    team_instance.check_team_status()
    team_instance.list_of_team_members()
    team_instance.get_player_data_api()

    while True:
        show_menu()
        choice = input("Select option: ").strip()

        if choice.lower() in ["q", "й"]:
            print("Thx for usage!")
            break

        if choice in [str(x) for x in range(0, 5)]:
            team_instance.work_with_pl_dict(choice)
            team_instance.print_markdown_table()
        elif choice in "9":
            return "Restart"

        print("Unknown option. Try again.")
    return True


if __name__ == "__main__":
    while True:
        resMain = main()

        if resMain == "Restart":
            print("\n====\n")
            continue

        break
