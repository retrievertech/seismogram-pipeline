var Queue = require('firebase-queue'),
    Firebase = require("firebase"),
    mkdirp = require('mkdirp'),
    exec = require("child_process").exec,
    fs = require("fs");

// post machine presence to firebase
require("./presence");

var rootRef = require("./rootRef");
var status = require("./status");
var logPath = __dirname + "/logs";

var queueRef = rootRef.child("queue");
var opts = { specId: "seismoSpec" };
var queue = new Queue(queueRef, opts, function(data, progress, resolve, reject) {
  console.log("received new job:");
  console.log(data);

  var filename = data.filename;
  processSeismo(filename, function(err) {
    if (err) {
      console.log("failed to process "+filename+"; marking job rejected");
      setStatus(filename, status.failed);
      reject(err);
      return;
    }
    console.log("successfully processed "+filename+"; marking job resolved");
    resolve();
  });
});

var processSeismo = function(filename, callback) {  
  var command = "sh process_task.sh " + filename;

  console.log(command);
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
  var seismoLogPath = logPath + "/" + filename;

  if (!fs.existsSync(seismoLogPath)) {
    mkdirp.sync(seismoLogPath);
  }

  var path = seismoLogPath + "/log.txt";

  fs.writeFile(path, logContents, function(err) {
    if (err) {
      console.log("error writing to log", filename, err);
      return;
    }
    uploadLog(filename, seismoLogPath);
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

process.on('SIGINT', function() {
  console.log('Starting queue shutdown');
  queue.shutdown().then(function() {
    console.log('Finished queue shutdown');
    process.exit(0);
  });
});
