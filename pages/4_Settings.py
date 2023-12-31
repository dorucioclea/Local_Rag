import os
import yaml
import streamlit as st


def read_yaml():
    if os.path.isfile("config_real.yaml"):
        config_file = "config_real.yaml"
    else:
        config_file = "config.yaml"

    with open(config_file, 'r') as file:
        return yaml.load(file, Loader=yaml.Loader)


def display_settings(settings):
    db_settings = {}
    model_settings = {}
    not_display_settings = {}
    settings_not_display = ["doc_text_table", "paragraph_table", "vector_dim", "temp_doc_storage", "stream"]
    db_settings_list = ["database_name", "db_port", "host", "user", "password"]
    model_settings_list = ["model_name", "ollama_api_url", "embedding_batches", "temperature"]

    # Split settings into categories
    for key, value in settings.items():
        if key in db_settings_list:
            db_settings[key] = value
        elif key in model_settings_list:
            model_settings[key] = value
        elif key in settings_not_display:
            not_display_settings[key] = value

    # Function to convert to int if possible
    def to_int_if_possible(value):
        try:
            return int(value)
        except ValueError:
            return value

    st.subheader("Database Settings")
    edited_db_settings = {k: to_int_if_possible(st.text_input(k, str(v))) for k, v in db_settings.items()}

    st.subheader("Model Settings")
    edited_model_settings = {k: to_int_if_possible(st.text_input(k, str(v))) for k, v in model_settings.items()}

    # Combine all settings, prioritizing edited values
    combined_settings = {**not_display_settings, **edited_db_settings, **edited_model_settings}

    return combined_settings


def write_yaml(data):
    if os.path.isfile("config_real.yaml"):
        config_file = "config_real.yaml"
    else:
        config_file = "config.yaml"

    with open(config_file, 'w') as file:
        yaml.dump(data, file, Dumper=yaml.Dumper)


st.title("Settings")
st.write("Edit the settings for your database and your model to use.")

settings = read_yaml()
edited_settings = display_settings(settings)

if st.button("Save Changes"):
    write_yaml(edited_settings)
    st.success("Settings updated!")
