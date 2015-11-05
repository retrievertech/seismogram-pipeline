`process_queue.js` - The queue processing entry-point and logic. Fetches a new task from the queue, calls the appropriate scripts to process a seismogram, and saves log files to S3.

`presence.js` - Required by `process_queue.js`. Makes sure that machines working on the queue make their presence known on firebase.

`rootRef.js` - The root firebase reference used by `presence.js` and `process_queue.js`.

`status.js` - Status codes for processed seismos.

`package.json` - Node dependencies for `process_queue.js`.
