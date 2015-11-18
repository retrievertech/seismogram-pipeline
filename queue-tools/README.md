`prepare_queue.js` - Makes sure the spec for the firebase queue is in place, and posts a list of filenames to the queue.

`spawn_instances.py` - Launches EC2 machines (normal pricing) with the user data contained in `user_data.sh`.

`update_instance.sh` - SSHs into an ec2 instance, and git pulls to update the seismogram-pipeline repo. Used by `update_instances.py`.

`update_instances.py` - Calls `update_instance.sh` for every running ec2 instance.

`user_data.sh` - This script needs to be called by every ec2 instance on boot. It updates the seismogram-pipeline repo and, importantly, starts the `process_queue.js` script.

`gather_stats.js` - Fetches the stats.json files for a list of seismograms, and combines them into a single json.

`get_filtered_filenames.sh` - Filters the list of seismograms that exist on s3, and writes the filtered list to `filtered_files.txt`.

`select_random_files.py` - Samples a number of lines from a file at random. Useful for getting random subsets of filenames for testing.

`root_ref.js` - The root firebase reference used by `prepare_queue.js`. Duplicate of `queue-worker/root_ref.js`.
