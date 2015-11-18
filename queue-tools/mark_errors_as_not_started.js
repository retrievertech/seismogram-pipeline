// Mark all errored queue items as not started by
// replacing `_state: error` with `_state: null`.

var async = require("async");

var funcs = [];
var queueRef = require("./root_ref").child("queue");

console.log("Fetching tasks data...");
queueRef.child("tasks").once("value", function(snap) {
  console.log("Received tasks data.");

  snap.forEach(function(taskSnap) {
    if (taskSnap.val()._state === "error") {
      funcs.push(markAsNotStarted(taskSnap));
    }
  });

  console.log("Marking", funcs.length, "tasks as not started.");

  async.parallel(funcs, function(err, results) {
    if (err) {
      console.log(err);
    } else {
      console.log("Done.");
      process.exit();
    }
  });
});

function markAsNotStarted(taskSnap) {
  return function(cb) {
    console.log("Marking", taskSnap.val().filename, "as not started.");
    taskSnap.ref().child("_state").remove(cb);
  }
}