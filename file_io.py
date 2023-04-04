import os
import os.path

import aiofiles

# Set a dedicated folder for file I/O
WORKING_DIR = "workspace"

if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)


def safe_join(base, *paths):
    new_path = os.path.join(base, *paths)
    norm_new_path = os.path.normpath(new_path)

    if os.path.commonprefix([base, norm_new_path]) != base:
        raise ValueError("Attempted to access outside of working directory.")

    return norm_new_path


async def read_file(filename):
    try:
        filepath = safe_join(WORKING_DIR, filename)
        async with aiofiles.open(filepath, "r") as f:
            content = await f.read()
        return content
    except Exception as e:
        return "Error: " + str(e)


async def write_to_file(filename, text):
    try:
        filepath = safe_join(WORKING_DIR, filename)
        async with aiofiles.open(filepath, "w") as f:
            await f.write(text)
        return "File written to successfully."
    except Exception as e:
        return "Error: " + str(e)


async def append_to_file(filename, text):
    try:
        filepath = safe_join(WORKING_DIR, filename)
        async with aiofiles.open(filepath, "a") as f:
            await f.write(text)
        return "Text appended successfully."
    except Exception as e:
        return "Error: " + str(e)


async def delete_file(filename):
    try:
        filepath = safe_join(WORKING_DIR, filename)
        os.remove(filepath)
        return "File deleted successfully."
    except Exception as e:
        return "Error: " + str(e)
