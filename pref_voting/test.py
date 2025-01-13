import asyncio
import aiofiles
import os
from async_pref_voting_methods import create_profile, run_voting_methods
import csv

data_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/scottish_results_test.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/scotland/processed_data'

error_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/scottish_error_test.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/scottish_processed_test.txt'

# Assuming you have a process_file() function that processes each file asynchronously
async def process_file(full_path, filename, all_data, data_file, processed_file):
    print("RUNNING ", filename, "\n")
    
    # Assuming create_profile and run_voting_methods are async functions:
    print(full_path)
    profile, file_path, candidates_with_indices = await create_profile(full_path)
    data = await run_voting_methods(profile, file_path, candidates_with_indices)
    all_data.append(data)
    print(data, "\n")

    # Async file writing using aiofiles for the output CSV
    async with aiofiles.open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        keys = all_data[0].keys()
        row = [data.get(key, '') for key in keys]
        await asyncio.to_thread(writer.writerow, row)  # Use asyncio.to_thread for synchronous writer method

    # Async writing to processed file
    async with aiofiles.open(processed_file, mode="a") as ef:
        await ef.write(f"{filename}, ")


async def process_all_files(file_paths, data_file, processed_file):
    all_data = []
    
    # Create tasks for all files to process them concurrently
    tasks = [process_file(full_path, filename, all_data, data_file, processed_file) 
             for full_path, filename in file_paths]
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

# # Example usage:
async def main():
    input_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith(('.blt', '.csv', '.txt')):
                # if filename not in processed_files:
                full_path = os.path.join(dirpath, filename)
                input_files.append((full_path, filename))
        
    # Process all files asynchronously and write results to the output file
    # print(input_files)
    # await process_all_files(input_files, data_file, processed_file)

# Run the main function to start the process
asyncio.run(main())