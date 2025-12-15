from parser import Parse


def show_menu():
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
    teamURL = input("Input club's URL from Transfermarkt : ")

    teamInstance = Parse(teamURL)
    teamInstance.checkTeamStatus()
    teamInstance.listOfTeamMembers()
    teamInstance.getPlayerDataAPI()

    while True:
        show_menu()
        choice = input("Select option: ").strip()

        if choice.lower() in ["q", "й"]:
            print("Thx for usage!")
            break

        if choice in [str(x) for x in range(0, 5)]:
            teamInstance.workWithPlDict(choice)
            teamInstance.print_markdown_table()
        elif choice in "9":
            return "Restart"
        else:
            print("Unknown option. Try again.")

    return True


if __name__ == "__main__":
    while True:
        resMain = main()

        if resMain == "Restart":
            print("\n====\n")
            continue

        break
