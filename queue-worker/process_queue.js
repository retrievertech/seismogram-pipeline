var Queue = require('firebase-queue'),
    Firebase = require("firebase"),
    exec = require("child_process").exec,
    fs = require("fs");

// post machine presence to firebase
require("./presence");

var rootRef = require("./rootRef");
var status = require("./status");
var logPath = __dirname + "/logs";

var queueRef = rootRef.child("queue");
var queue = new Queue(queueRef, function(data, progress, resolve, reject) {
  // Read and process task data 
  console.log(data);
 
  var filename = data.filename;

  processSeismo(filename, function(err) {
    if (err) {
      setStatus(filename, status.failed);
      reject(err);
      return;
    }
    resolve();
  });
});

var processSeismo = function(filename, callback) {  
  var command = "sh process_task.sh " + filename;

  // if (process.env.NODE_ENV !== "production") {
  //   command += " dev";
  // }

  exec(command, function(err, stdout, stderr) {
    var log = "== stdout ==\n";
    log += stdout;
    log += "\n== stderr ==\n";
    log += stderr;

    console.log(log);
    writeLog(filename, log);

    callback(err);
  });
}

var writeLog = function(filename, logContents) {
  if (!fs.existsSync(logPath)) {
    fs.mkdirSync(logPath);
  }

  var path = logPath + "/" + filename + ".txt";

  fs.writeFile(path, logContents, function(err) {
    if (err) {
      console.log("error writing to log", filename, err);
      return;
    }
    uploadLog(filename, path);
  });
};

var uploadLog = function(filename, path) {
  var command = "sh copy_to_s3.sh " + filename + " " + path + " logs";
  console.log(command);
  exec(command, function(err) {
    if (err) {
      console.log("error copying log to s3", err);
      return;
    }
  });
}

var setStatus = function(filename, status) {
  var command = "sh set_seismo_status.sh " + filename + " " + status;
  console.log(command);
  exec(command, function(err) {
    if (err) {
      console.log("error setting seismo status", err);
      return;
    }
  });
}
