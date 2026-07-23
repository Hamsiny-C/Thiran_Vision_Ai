from ai.process_image import process_image
from ai.process_video import process_video
from ai.camera import start_camera


def show_menu():
    while True:
        print("\n==============================")
        print("THIRAN VISION AI")
        print("==============================")
        print("1. Image Detection")
        print("2. Video Detection")
        print("3. Live Camera")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            process_image()

        elif choice == "2":
            process_video()

        elif choice == "3":
            start_camera()

        elif choice == "4":
            print("Program closed.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    show_menu() 