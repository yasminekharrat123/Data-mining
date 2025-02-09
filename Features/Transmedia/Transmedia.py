
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
    Transmedia storytelling is a narrative technique in which a story is told across multiple platforms or media, with each medium offering a unique perspective and adding to the overall narrative. For example, a story might start as a movie, but then expand into books, games, comics, and other forms of media, with each medium contributing new and complementary parts of the storyline.

    Movie Adaptation is the process of reimagining a story from another medium, like a book or game, into a movie. It translates the original narrative into a cinematic format, often making changes to suit the visual and time-bound nature of film.

    You're going to be given a movie name:
    * Output YES if the movie is either an adaptation or transmedia storytelling
    * Output NO if the movie is not
    * Output UNKNOWN if you're not sure.
"""
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction=system_prompt,
)

chat_session = model.start_chat()


input_file = "final_movies_3_bf.tsv"  
output_file = "results.tsv"
fail_log = "failed_batches.txt"

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
            print(f"Processing: {formatted_title}")
            response = chat_session.send_message(formatted_title)
            clean_response = re.sub(r'[\r\n]+', ' ', response.text).strip().strip('"')
            print(clean_response)
            writer.writerow([imdb_id, title, year, clean_response])
            result_file.flush()

        except Exception as e:
            failures.append(index)
            fail_file.write(f"{imdb_id}")
            fail_file.flush()

        if (index + 1) % 10 == 0:
            time.sleep(60)

if failures:
    print(f"Failures logged in {fail_log}")
else:
    print(f"All rows processed successfully. Results saved to {output_file}")
