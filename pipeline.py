import papermill as pm
import os
import sys

# Define the ordered list of notebooks to run
NOTEBOOKS_TO_RUN = [
    "0_create_new_bucket.ipynb",
    "1_scraping_articles.ipynb",
    "2_translation_into_english.ipynb",
    "3_sentiment_analysis.ipynb", 
    "4_sentiment_comparison.ipynb", 
    "5_key_phrases.ipynb"
]

# Define the folder where executed notebooks will be saved (for logging/debugging)
OUTPUT_FOLDER = "executed_notebooks"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("Starting AI Analysis Pipeline...")
print("-" * 30)

# Pipeline execution
try:
    for i, input_path in enumerate(NOTEBOOKS_TO_RUN):
        # Create an output path for the executed notebook
        output_path = os.path.join(OUTPUT_FOLDER, f"executed_{input_path}")
        
        step_name = input_path.split('_')[1].replace('.ipynb', '')
        
        print(f"\n[{i+1}/{len(NOTEBOOKS_TO_RUN)}] Running Step: {step_name.upper()} ({input_path})")
        
        # The output notebook will contain all cell outputs and errors
        pm.execute_notebook(
            input_path=input_path,
            output_path=output_path,
            # If any step needs parameters (like dates or source names), you can pass them here:
            parameters=dict(
                # Example: pipeline_start_time=time.time()
            )
        )
        print(f"✅ SUCCESS: Step {i+1} completed.")
        
    print("\n" + "=" * 40)
    print("✨ PIPELINE COMPLETE: All 5 notebooks executed successfully! ✨")
    print("Final results should be in your S3 bucket.")
    print("=" * 40)

except Exception as e:
    # If any notebook fails, papermill catches the error and stops the pipeline
    print("\n" + "=" * 40)
    print(f"❌ PIPELINE FAILED at step {i+1} ({input_path})")
    print(f"Error details: {e}")
    print("Check the generated file in the 'executed_notebooks' folder for details.")
    sys.exit(1)