import os
from dotenv import load_dotenv
import kagglehub
from kagglehub import KaggleDatasetAdapter

load_dotenv("../lab2.env")

os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")

file_path = "career_path_in_all_field.csv"

try:
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "ministerjohn/career-path-prediction-for-different-fields",
        file_path,
    )
    print("First 5 records:", df.head())

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")  # One level up from src
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "career_path.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}")

except Exception as e:
    print(e)