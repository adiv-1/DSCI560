# Install dependencies as needed:
# pip install kagglehub[pandas-datasets] python-dotenv
import os
from dotenv import load_dotenv
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Load environment variables (adjust path if needed)
load_dotenv("lab2.env")  # Assuming lab2.env is in the same directory as the script; update path if necessary

# Set Kaggle credentials from .env
os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")

# Set the path to the file you'd like to load (must have a valid extension)
file_path = "career_path.csv"  # Replace with the exact file name from the dataset, e.g., "data.csv"

# Load the latest version
try:
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "ministerjohn/career-path-prediction-for-different-fields",  # Verify this ID on Kaggle
        file_path,
        # Provide any additional arguments like sql_query or pandas_kwargs. See the documentation:
        # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
    )
    print("First 5 records:", df.head())

    # Save to data folder (adjust path as needed)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")  # One level up from src
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "career_path.csv")  # Shorter name as requested
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}")

except Exception as e:
    print(f"Error loading dataset: {e}. Check the dataset ID, file path, and Kaggle credentials.")