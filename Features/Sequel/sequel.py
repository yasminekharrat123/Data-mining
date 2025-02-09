import pandas as pd
import csv
import re
import time
import google.generativeai as genai
import os

os.environ["GEMINI_API_KEY"] = ""

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# models = genai.list_models()
# for model in models:
#     print(model)

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2,
    "response_mime_type": "text/plain",
}

system_prompt = """
   A sequel is a movie that continues or expands upon the events, characters, or storylines of a previous movie, though it doesn't necessarily have to follow the events chronologically. It may explore past, present, or future events of the same universe or involve the same characters in different circumstances.

    You're going to be given a movie name:
    Output YES if the movie is a sequel.
    Output NO if the movie is not a sequel.
    Output UNKNOWN if you're not sure.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction=system_prompt,
)

chat_session = model.start_chat()

input_file = "whats_left.tsv"  
output_file = "sequel5.tsv"
fail_log = "failed_sequel4.txt"

df = pd.read_csv(input_file, delimiter="\t", encoding="utf-8")

failures = []


with open(output_file, "a", encoding="utf-8", newline="") as result_file, open(fail_log, "a", encoding="utf-8") as fail_file:
    writer = csv.writer(result_file, delimiter="\t")
    writer.writerow(["tconst", "Title", "Year", "Response"])

    for index, row in df.iterrows():
        title = row["primaryTitle"]
        year = row["startYear"]
        imdb_id = row["tconst"]
        formatted_title = f"{title} ({year})"

        try:
            print(f"Processing:{index} : {formatted_title}")
            response = chat_session.send_message(formatted_title)
            clean_response = re.sub(r'[\r\n]+', ' ', response.text).strip().strip('"')
            print(clean_response)
            writer.writerow([imdb_id, title, year, clean_response])
            result_file.flush()

        except Exception as e:
            failures.append(imdb_id)
            print(f"Failed to process: {formatted_title}: {str(e)}\n")
            fail_file.write(f"{imdb_id}\n")
            fail_file.flush()

        if (index + 1) % 10 == 0:
            time.sleep(60)

if failures:
    print(f"Failures logged in {fail_log}")
    print(f"Failed to process {len(failures)} rows.")
    print(failures)
else:
    print(f"All rows processed successfully. Results saved to {output_file}")
