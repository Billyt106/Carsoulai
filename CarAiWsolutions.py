import speech_recognition as sr
import openai
from gtts import gTTS
import os
import tempfile
import obd  

# Intialising everything here
api_key = "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"
recognizer = sr.Recognizer()
openai.api_key = api_key
connection = obd.OBD()

def output_response(assistant_response):
    if mode == "speak":
        speak_audio(assistant_response)
    else:
        print("\nAssistant:", assistant_response)

def respond_to_user_command(user_command):
    response = openai.Completion.create(
        model="gpt-4", 
        prompt=user_command,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def recognize_voice():
    with sr.Microphone() as source:
        print("Listening for a command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio).lower()
            print(f"You said: {user_input}")
            return user_input
        except sr.WaitTimeoutError:
            print("No speech detected. Please speak.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio. Please try again.")
            return None

def speak_audio(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + ".mp3")
        os.system(f"mpg123 {fp.name}.mp3")

def solai(dtc_codes):
    """Use the provided DTC codes to get potential solutions from GPT-4."""
    user_input = f"I have DTC codes {', '.join(dtc_codes)}. What could be the potential solutions?"
    response = respond_to_user_command(user_input)
    return response

def get_dtc_codes():
    try:
        cmd = obd.commands.GET_DTC
        response = connection.query(cmd)
        if response.value:
            dtc_codes = ", ".join(response.value)
            print(f"DTC codes found: {dtc_codes}")
            choice = input("Do you need GPT-4 help to find a potential solution for the DTC codes? (yes/no): ").lower()
            if choice == "yes":
                solution = solai(response.value)
                print("\nPotential Solution from GPT-4:\n", solution)
            return dtc_codes
        else:
            return "No DTC codes found."
    except Exception as e:
        return f"An error occurred: {e}"

def clear_dtc_codes():
    try:
        cmd = obd.commands.CLEAR_DTC
        response = connection.query(cmd)
        return "DTC codes cleared successfully!" if response.is_null() else "Failed to clear DTC codes."
    except Exception as e:
        return f"Error clearing DTC codes: {e}"

def get_engine_rpm():
    try:
        cmd = obd.commands.RPM
        response = connection.query(cmd)
        return f"Engine RPM: {response.value.magnitude} rpm"
    except Exception as e:  
        return f"Error fetching engine RPM: {e}"

def get_vehicle_speed():
    try:
        cmd = obd.commands.SPEED
        response = connection.query(cmd)
        return f"Vehicle Speed: {response.value.magnitude} km/h"
    except Exception as e:
        return f"Error fetching vehicle speed: {e}"

def get_coolant_temp():
    try:
        cmd = obd.commands.COOLANT_TEMP
        response = connection.query(cmd)
        return f"Coolant Temperature: {response.value.magnitude} °C"
    except Exception as e:
        return f"Error fetching coolant temperature: {e}"

def get_vehicle_info():
    try:
        cmd = obd.commands.VIN
        response = connection.query(cmd)
        return f"Vehicle Identification Number (VIN): {response.value}"
    except Exception as e:
        return f"Error fetching vehicle info: {e}"

def get_emission_readiness_status():
    try:
        cmd = obd.commands.GET_DTC
        response = connection.query(cmd)
        if response.is_null():
            return "No emission-related fault codes detected."
        return f"Emission-Related Fault Codes: {', '.join(response.value)}"
    except Exception as e:
        return f"Error fetching emission readiness status: {e}"

def get_freeze_frame_data():
    try:
        cmd = obd.commands.FREEZE_DTC
        response = connection.query(cmd)
        if response.is_null():
            return "No freeze frame data available."
        return f"Freeze Frame Data: {', '.join(response.value)}"
    except Exception as e:
        return f"Error fetching freeze frame data: {e}"
    
def set_mode():
    global mode
    print("Choose your preferred mode:")
    print("1. Voice")
    print("2. Text")
    preference = input("Select (1/2): ")

    if preference == "1":
        mode = "speak"
        print("Mode set to Voice!")
    elif preference == "2":
        mode = "text"
        print("Mode set to Text!")
    else:
        print("Invalid choice. Mode remains unchanged.")
        
def chat_with_gpt4():
    while True:
        if mode == "speak":
            user_input = recognize_voice()
            if not user_input:
                continue
        else:
            user_input = input("Your Command: ")

        response = respond_to_user_command(user_input)
        output_response(response)

        continue_chat = input("Continue chatting? (yes/no): ")
        if continue_chat.lower() != "yes":
            break
def mock_get_dtc_codes():
    """Mock function to simulate getting DTC codes without actually querying the OBD-II system."""
    mock_dtc_codes = ["P0300", "P0420", "P0171"]
    return mock_dtc_codes

def mock_respond_to_user_command(user_command):
    """Mock function to simulate getting a response from GPT-4 without actually querying it."""
    mock_solutions = {
        "P0300": "Random/Multiple Cylinder Misfire Detected. Potential solutions include checking the spark plugs, ignition coils, or fuel injectors for faults.",
        "P0420": "Catalyst System Efficiency Below Threshold. Potential solution could be replacing the catalytic converter or checking for exhaust leaks.",
        "P0171": "System Too Lean. Potential solutions include checking for vacuum leaks, faulty fuel injectors, or a failing oxygen sensor."
    }

    dtc_codes_mentioned = [code for code in mock_solutions if code in user_command]
    responses = [mock_solutions[code] for code in dtc_codes_mentioned]

    return "\n".join(responses)

def mock_test():
    print("Running mock test for DTC codes...")

    # Mock get DTC codes
    dtc_codes = mock_get_dtc_codes()
    print(f"Mock DTC codes obtained: {', '.join(dtc_codes)}")

    # Mock ask user for GPT-4 help
    choice = input("Do you need GPT-4 help to find a potential solution for the DTC codes? (yes/no): ").lower()

    if choice == "yes":
        user_input = f"I have DTC codes {', '.join(dtc_codes)}. What could be the potential solutions?"
        # Mock get solution from GPT-4
        solution = mock_respond_to_user_command(user_input)
        print("\nMock Potential Solution from GPT-4:\n", solution)
    else:
        print("Not using GPT-4 for solutions.")

def main_menu():
    global mode
    mode = "text"
    print("Welcome to CAR AI Powered by GPT-4 MENU")
    set_mode()

    while True:
        print("\nMENU")
        print("1. Chat with GPT-4")
        print("2. Get DTC Codes")
        print("3. Clear DTC Codes")
        print("4. Get Engine RPM")
        print("5. Get Vehicle Speed")
        print("6. Get Coolant Temperature")
        print("7. Get Vehicle Information")
        print("8. Get Emission Readiness Status")
        print("9. Get Freeze Frame Data")
        print("10. Change Mode (Current:", ("Voice" if mode == "speak" else "Text"), ")")
        print("11. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            chat_with_gpt4()
        elif choice == "2":
            output_response(get_dtc_codes())
        elif choice == "3":
            output_response(clear_dtc_codes())
        elif choice == "4":
            output_response(get_engine_rpm())
        elif choice == "5":
            output_response(get_vehicle_speed())
        elif choice == "6":
            output_response(get_coolant_temp())
        elif choice == "7":
            output_response(get_vehicle_info())
        elif choice == "8":
            output_response(get_emission_readiness_status())
        elif choice == "9":
            output_response(get_freeze_frame_data())
        elif choice == "10":
            set_mode()
        elif choice == "11":
            print("Exiting CarAI - POWERED BY GPT-4")
            break
        else:
            print("Invalid choice. Please select a valid option from the menu.")

main_menu()
mock_test()



