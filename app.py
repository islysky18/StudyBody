import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st

load_dotenv()

client = openai.OpenAI()

model = "gpt-4o"


# Step 1. create a vector store and upload a file to OpenAI embeddings ===
# rb => binary reading
vector_store = client.beta.vector_stores.create(name="CryptoCurrency")

filepath = 'cryptocurrency.pdf'

# file_stream = [open(path, "rb") for path in filepath]
file_stream = [open(filepath, "rb")]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_stream
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

# assistant = client.beta.assistants.update(
#   assistant_id=assistant.id,
#   tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
# )

# Upload the user provided file to OpenAI(this also work but the file does not link to the assistant, just store in the Vector Store)
# file_object = client.files.create(file=open(filepath, "rb"),
#                                   purpose="assistants")




# Step 2 - Create an assistant
assistant = client.beta.assistants.create(
    name="Study Buddy",
    instructions="""You are a helpful study assistant who knows a lot about understanding research papers.
    Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
    Cross-reference information for additional insights and answer related questions comprehensively.
    Analyze the papers, noting strengths and limitations.
    Respond to queries effectively, incorporating feedback to enhance your accuracy.
    Handle data securely and update your knowledge base with the latest research.
    Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
    Maintain a feedback loop for continuous improvement and user support.
    Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible and comprehensible.""",
    tools=[{"type": "file_search"}],
    model=model,
)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# === Get assistant ID
assis_id = assistant.id
print(assis_id)

# === Hardcoded ids to be used once the first code run is done and the assistant was created
# thread_id = ""
# assis_id = ""





# === Step 3. Create a Thread
message = "What is mining?"

thread = client.beta.threads.create()
thread_id = thread.id
print(thread_id)

# === Run The Assistant

run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assis_id,
    instructions="Please address the user as Bruce"
)

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

#=== Run it
wait_for_run_completion(
    client=client,
    thread_id=thread_id,
    run_id=run.id
    )

# === Check the Run Steps - LOGS ===
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Run Steps --> {run_steps.data[0]}")