// usage:
// node prepare_queue.js < file_list.txt
//
// description:
// ensures the seismoSpec is in Firebase as
// described below, and adds a task to the queue
// for each line of file_list.txt

var es = require('event-stream');
var async = require("async");

var rootRef = require("./root_ref");
var specsRef = rootRef.child("queue/specs");
var tasksRef = rootRef.child("queue/tasks");

var seismoSpec = {
  "start_state": null, // use this spec for all tasks
  "in_progress_state": "in_progress",
  "finished_state": "complete",
  "error_state": "error",
  "timeout": 1000*60*30, // 30 minutes
  "retries": 0 // don't retry
};

function postTask(filename, callback) {
  tasksRef.push({ "filename": filename }, function(err) {
    callback(err);
  });
}

function postTasks(err, filenames) {
  console.log("Posting "+filenames.length+" tasks...");

  async.each(filenames, postTask, function(err) {
    if (err) {
      console.log(err);
    }
    console.log("Done.")
    process.exit();
  });
}

function filterEmptyStrings(data) {
  if (data === "") return;
  return data;
};

specsRef.child("seismoSpec").set(seismoSpec, function() {
  var inStream = process.stdin
    .pipe(es.split())
    .pipe(es.mapSync(filterEmptyStrings))
    .pipe(es.writeArray(postTasks));
});
