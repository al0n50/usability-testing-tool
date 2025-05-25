import streamlit as st
import pandas as pd
import time
import os

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


# Utility: Save data to CSV
def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


# Utility: Load data from CSV
def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.set_page_config(page_title="Usability Testing Tool")
    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs([
        "Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"
    ])

    # -------------------- HOME TAB --------------------
    with home:
        st.header("Introduction")
        st.markdown("""
        Welcome to the Usability Testing Tool for HCI. This app automates usability testing. In this session, you will:
        1. Provide consent
        2. Complete a demographic questionnaire
        3. Perform a usability task
        4. Submit feedback through an exit questionnaire
        5. View an aggregated report

        ---
        """)

    # -------------------- CONSENT TAB --------------------
    with consent:
        st.header("Consent Form")
        st.markdown("""
        By participating in this usability test, you agree to the collection and use of your data for educational and analytical purposes. All data will remain confidential.
        """)

        consent_given = st.checkbox("I agree to participate in this usability test.")
        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                save_to_csv({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }, CONSENT_CSV)
                st.success("Consent recorded.")

    # -------------------- DEMOGRAPHICS TAB --------------------
    with demographics:
        st.header("Demographic Questionnaire")
        with st.form("demographic_form"):
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=10, max_value=100, step=1)
            occupation = st.text_input("Occupation")
            familiarity = st.radio(
                "How familiar are you with usability testing tools?",
                ["Not familiar", "Somewhat familiar", "Very familiar"]
            )

            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                save_to_csv({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name,
                    "age": age,
                    "occupation": occupation,
                    "familiarity": familiarity
                }, DEMOGRAPHIC_CSV)
                st.success("Demographic data saved.")

    # -------------------- TASK TAB --------------------
    with tasks:
        st.header("Task Page")
        selected_task = st.selectbox("Select Task", ["Task 1: Example Task"])
        st.markdown("**Task Description**: Perform the example task using the interface provided.")

        if st.button("Start Task Timer"):
            st.session_state["start_time"] = time.time()
            st.success("Task timer started.")

        if st.button("Stop Task Timer") and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_duration"] = duration
            st.success(f"Task duration recorded: {duration:.2f} seconds.")

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_duration", None)

            save_to_csv({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val if duration_val else "",
                "notes": notes
            }, TASK_CSV)

            st.success("Task performance data saved.")

            # Clear session state
            st.session_state.pop("start_time", None)
            st.session_state.pop("task_duration", None)

    # -------------------- EXIT QUESTIONNAIRE --------------------
    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            satisfaction = st.slider("Overall, how satisfied were you with the usability of the product?", 1, 5)
            difficulty = st.slider("How difficult was it to complete the task?", 1, 5)
            open_feedback = st.text_area("Additional feedback or suggestions")

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                save_to_csv({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "open_feedback": open_feedback
                }, EXIT_CSV)
                st.success("Exit questionnaire data saved.")

    # -------------------- REPORT TAB --------------------
    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")

        # Example of aggregated stats (for demonstration only)
        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")
            avg_satisfaction = exit_df["satisfaction"].mean()
            avg_difficulty = exit_df["difficulty"].mean()
            st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
            st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")

# Entry point
if __name__ == "__main__":
    main()
