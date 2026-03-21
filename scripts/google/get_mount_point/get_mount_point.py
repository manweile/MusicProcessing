import psutil
import os


def get_mount_point_psutil(file_path):
    file_path = os.path.realpath(file_path)
    for partition in psutil.disk_partitions(all=True):
        if file_path.startswith(partition.mountpoint):
            return partition.mountpoint
    return None


# Example usage
file_path = os.path.join("D", "MusicProcessing", "src", "generated_files", "Music")
# file_path = "/path/to/your/file.txt" # Replace with your file path
mount_point = get_mount_point_psutil(file_path)
if mount_point:
    print(f"The mount point for '{file_path}' is: {mount_point}")
else:
    print(f"Could not determine mount point for '{file_path}'")