`process_queue.js` - The queue processing entry-point and logic. Fetches a new task from the queue, calls the appropriate scripts to process a seismogram, and saves log files to S3.

`presence.js` - Required by `process_queue.js`. Makes sure that machines working on the queue make their presence known on firebase.

`root_ref.js` - The root firebase reference used by `presence.js` and `process_queue.js`. Duplicate of `queue-tools/root_ref.js`.

`status.js` - Status codes for processed seismos.

`package.json` - Node dependencies for `process_queue.js`.

TODO: A duplicate of `root_ref.js` is used by `queue-tools`. And a duplicate of `status.js` is used by the web app server. We need to figure out a way to handle these duplicates. Maybe by publishing a private npm package?
