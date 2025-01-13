import os
import csv
import asyncio
import aiofiles
from asyncio.exceptions import TimeoutError
from pref_voting_methods import create_profile, run_voting_methods

# File paths
data_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/civs_results_test.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/civs'

error_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/civs_error_test.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/civs_processed_test.txt'

all_data = []

def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 5 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False

async def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    try:
        # Timeout for the processing task
        await asyncio.wait_for(create_and_process(full_path, filename), timeout=10)
    except TimeoutError:
        print(f"Processing {filename} timed out.")
        async with aiofiles.open(error_file, "a") as ef:
            await ef.write(f"{filename}, ")
    except Exception as e:
        print(f"An error occurred while processing {filename}: {e}")
        async with aiofiles.open(error_file, "a") as ef:
            await ef.write(f"{filename}, ")

async def create_and_process(full_path, filename):
    profile, file_path, candidates_with_indices = create_profile(full_path)
    data = run_voting_methods(profile, file_path, candidates_with_indices)
    all_data.append(data)
    print(data, "\n")

    # Write results to data file
    async with aiofiles.open(data_file, mode='a', newline='') as file:
        writer = csv.writer(await file.__aenter__())
        keys = all_data[0].keys()
        row = [data.get(key, '') for key in keys]
        writer.writerow(row)

    # Write to processed file
    async with aiofiles.open(processed_file, "a") as ef:
        await ef.write(f"{filename}, ")

# async def read_processed():
#     processed_files = []

#     try:
#         async with aiofiles.open(error_file, 'r') as file:
#             content = await file.read()
#             processed_files += [file.strip() for file in content.split(',') if file.strip()]

#         async with aiofiles.open(processed_file, 'r') as file:
#             content = await file.read()
#             processed_files += [file.strip() for file in content.split(',') if file.strip()]
#     except FileNotFoundError:
#         print("Processed files not found.")

#     return set(processed_files)

async def main():
    # processed_files = await read_processed()

    tasks = []
    semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent tasks

    async def semaphore_wrapper(full_path, filename):
        async with semaphore:
            await process_file(full_path, filename)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith(('.blt', '.csv', '.txt')):
                # if filename not in processed_files:
                full_path = os.path.join(dirpath, filename)

                if file_less_than_3mb(full_path):
                    tasks.append(semaphore_wrapper(full_path, filename))
                else:
                    print(f"File {filename} is larger than 3MB, skipping.")
                # else:
                #     print("Already processed", filename)

    # Use return_exceptions=True to handle errors gracefully
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions after processing
    for result, task in zip(results, tasks):
        if isinstance(result, Exception):
            print(f"Task failed with error: {result}")

if __name__ == '__main__':
    asyncio.run(main())