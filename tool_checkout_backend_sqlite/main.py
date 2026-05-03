from tool_checkout.database import close_connection
from tool_checkout.database import initialize_database
from tool_checkout.services import AuthorizationError
from tool_checkout.services import BusinessRuleError
from tool_checkout.services import NotFoundError
from tool_checkout.services import ToolCheckoutService
from tool_checkout.tracking_service import TrackingError


# function to reset records used by the automatic demo
# this makes the demo easier to run more than once
def reset_demo_records(service, manager):
    if service.get_tool("T900") is not None:
        service.update_tool_status("T900", "Available", "None", "Warehouse", "Good")

        try:
            service.unassign_tracker_from_tool(manager, "T900")
        except (BusinessRuleError, AuthorizationError, NotFoundError, TrackingError):
            pass

    if service.get_tool("T001") is not None:
        service.update_tool_status("T001", "Available", "None", "Warehouse", "Good")

    if service.get_tool("T003") is not None:
        service.update_tool_status("T003", "Available", "None", "Warehouse", "Good")


# function to print one tool record
def print_tool(tool):
    print(
        tool["tool_id"],
        "|",
        tool["tool_name"],
        "|",
        tool["value_level"],
        "|",
        tool["tool_status"],
        "| Tracking Required:",
        tool["requires_tracking"],
        "| Tracker ID:",
        tool["assigned_tracker_id"],
    )


# function to show all tools
def show_all_tools(service):
    print("\n*** All Tools ***")
    tools = service.get_all_tools()

    for tool in tools:
        print_tool(tool)


# function to print tracking status for a tool
def print_tracking_status(service, manager, tool_id):
    status = service.get_tool_tracking_status(manager, tool_id)

    print("\n*** Tracking Status ***")
    print("Tool:", status["tool_id"], "-", status["tool_name"])
    print("Requires Tracking:", status["requires_tracking"])
    print("Tracker Code:", status["tracker_code"])
    print("Provider:", status["provider_name"])
    print("Tracker Status:", status["status"])
    print("Battery:", status["battery_level"])
    print("Latitude:", status["last_latitude"])
    print("Longitude:", status["last_longitude"])
    print("Last Location Time:", status["last_location_time"])
    print("Last Sync Time:", status["last_sync_time"])


# function to print tracking history for a tool
def print_tracking_history(service, manager, tool_id):
    history = service.get_tracking_history(manager, tool_id)

    print("\n*** Tracking History ***")

    if len(history) == 0:
        print("No tracking logs found.")
    else:
        for item in history:
            print(
                item["log_id"],
                "|",
                item["tracker_code"],
                "|",
                item["latitude"],
                item["longitude"],
                "| Battery:",
                item["battery_level"],
                "| Event:",
                item["event_type"],
                "|",
                item["recorded_at"],
            )


# function to run a short automatic backend demo
# this proves the backend works without any frontend
def run_automatic_demo(service):
    print("\n*** Automatic Backend Demo ***")

    worker = service.authenticate_user("U001", "1234")
    manager = service.authenticate_user("U002", "1234")

    reset_demo_records(service, manager)

    print("Logged in worker:", worker["user_name"])
    print("Logged in manager:", manager["user_name"])

    if service.get_tool("T900") is None:
        print(
            service.add_tool(
                manager,
                "T900",
                "Cinema Camera Package",
                "Video",
                "High Value",
                requires_tracking=True,
            )
        )
    else:
        print(service.mark_tool_as_high_value(manager, "T900", requires_tracking=True))

    if service.get_tracker_status(manager, "GPS-001") is None:
        print(
            service.create_tracker(
                manager,
                "GPS-001",
                "GPS/GNSS Cellular Asset Tracker",
                "Simulated GNSS Provider",
                "active",
                "Demo tracker for high-value equipment.",
            )
        )

    print("\nAttempt checkout before assigning tracker:")
    try:
        print(service.checkout_tool(worker, "T900", "Event Site A", manager["user_id"]))
    except (BusinessRuleError, AuthorizationError, NotFoundError, TrackingError) as error:
        print("Checkout blocked:", error)

    print("\nAssign tracker and try checkout again:")
    print(service.assign_tracker_to_tool(manager, "T900", "GPS-001"))
    print(service.checkout_tool(worker, "T900", "Event Site A", manager["user_id"]))

    print("\nSync latest tracker location:")
    sync_result = service.sync_tool_location(
        manager,
        "T900",
        event_type="under_investigation_check",
        notes="Demo sync for high-value equipment tracking.",
    )
    print("Tracker:", sync_result["tracker_code"])
    print("Latitude:", sync_result["latitude"])
    print("Longitude:", sync_result["longitude"])
    print("Battery:", sync_result["battery_level"])
    print("Last Sync:", sync_result["last_sync_time"])

    print_tracking_status(service, manager, "T900")
    print_tracking_history(service, manager, "T900")
    show_all_tools(service)


# function to show the command line menu
def show_menu(current_user):
    print("\n*** Tool Checkout Backend Demo ***")
    print("Logged in as:", current_user["user_name"], "-", current_user["user_role"])
    print("1. View all tools")
    print("2. Checkout a tool")
    print("3. Return a tool")
    print("4. Verify kit")
    print("5. View checked out tools")
    print("6. View flagged and maintenance tools")
    print("7. View system history")
    print("8. Create GPS/GNSS tracker")
    print("9. Assign tracker to tool")
    print("10. Sync tool location")
    print("11. View tracking history")
    print("12. Quit")


# function to login for the command line demo
def login(service):
    print("\n*** Login ***")
    print("Sample users: U001 Worker, U002 Manager, U003 Warehouse Staff, U004 Administrator")
    print("Sample password: 1234")

    user_id = input("Enter User ID: ")
    password = input("Enter Password: ")
    return service.authenticate_user(user_id, password)


# function to run the interactive command line demo
def run_cli_demo(service):
    try:
        current_user = login(service)
    except (BusinessRuleError, AuthorizationError, NotFoundError, TrackingError) as error:
        print("Login failed:", error)
        return

    while True:
        show_menu(current_user)
        choice = input("Select an option: ")

        try:
            if choice == "1":
                show_all_tools(service)
            elif choice == "2":
                tool_id = input("Enter Tool ID: ")
                location = input("Enter Location: ")
                manager_id = input("Enter Manager ID if high value, otherwise leave blank: ")
                print(service.checkout_tool(current_user, tool_id, location, manager_id))
            elif choice == "3":
                tool_id = input("Enter Tool ID: ")
                condition = input("Enter Condition (Good/Damaged): ")
                print(service.return_tool(current_user, tool_id, condition))
            elif choice == "4":
                kit_id = input("Enter Kit ID: ")
                result = service.verify_kit(current_user, kit_id)
                print("Kit:", result["kit_name"])

                for tool in result["tools"]:
                    print(tool["tool_id"], "-", tool["tool_name"], "-", tool["status"])

                if result["all_available"]:
                    print("Kit is ready for dispatch.")
                else:
                    print("Kit is not ready. Some tools are unavailable.")
            elif choice == "5":
                checked_out_tools = service.get_checked_out_tools()

                if len(checked_out_tools) == 0:
                    print("No tools are currently checked out.")
                else:
                    for tool in checked_out_tools:
                        print(
                            tool["tool_id"],
                            "|",
                            tool["tool_name"],
                            "| Borrowed By:",
                            tool["borrowed_by"],
                            "| Location:",
                            tool["tool_location"],
                        )
            elif choice == "6":
                flagged_tools = service.get_flagged_and_maintenance_tools()

                if len(flagged_tools) == 0:
                    print("No flagged or maintenance tools found.")
                else:
                    for tool in flagged_tools:
                        print(
                            tool["tool_id"],
                            "|",
                            tool["tool_name"],
                            "|",
                            tool["tool_status"],
                            "| Condition:",
                            tool["tool_condition"],
                        )
            elif choice == "7":
                history = service.get_history(current_user)

                for item in history:
                    print(item["history_id"], "|", item["action_date"], "|", item["action_text"])
            elif choice == "8":
                tracker_code = input("Enter Tracker Code: ")
                provider_name = input("Enter Provider Name: ")
                print(
                    service.create_tracker(
                        current_user,
                        tracker_code,
                        "GPS/GNSS Cellular Asset Tracker",
                        provider_name,
                        "active",
                        "Created from CLI demo.",
                    )
                )
            elif choice == "9":
                tool_id = input("Enter Tool ID: ")
                tracker_code = input("Enter Tracker Code: ")
                print(service.assign_tracker_to_tool(current_user, tool_id, tracker_code))
            elif choice == "10":
                tool_id = input("Enter Tool ID: ")
                result = service.sync_tool_location(
                    current_user,
                    tool_id,
                    event_type="manual_sync",
                    notes="Manual CLI tracking check.",
                )
                print("Latitude:", result["latitude"])
                print("Longitude:", result["longitude"])
                print("Battery:", result["battery_level"])
                print("Last Sync:", result["last_sync_time"])
            elif choice == "11":
                tool_id = input("Enter Tool ID: ")
                print_tracking_history(service, current_user, tool_id)
            elif choice == "12":
                service.logout_user(current_user)
                print("Goodbye!")
                break
            else:
                print("Sorry, invalid option. Please try again.")
        except (BusinessRuleError, AuthorizationError, NotFoundError, TrackingError) as error:
            print("Error:", error)


# main function of the program
def main():
    connection = initialize_database()
    service = ToolCheckoutService(connection)

    try:
        print("1. Run automatic backend demo")
        print("2. Run interactive CLI demo")
        choice = input("Select an option: ")

        if choice == "1":
            run_automatic_demo(service)
        elif choice == "2":
            run_cli_demo(service)
        else:
            print("Sorry, invalid option.")
    finally:
        close_connection(connection)


# the program starts here by calling the main function
if __name__ == "__main__":
    main()
