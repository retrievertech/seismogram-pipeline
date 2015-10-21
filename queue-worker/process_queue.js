var Queue = require('firebase-queue'),
    Firebase = require("firebase"),
    exec = require("child_process").exec,
    rootRef = require("./rootRef");

// post machine presence to firebase
require("./presence");

var queueRef = rootRef.child("queue");
var queue = new Queue(queueRef, function(data, progress, resolve, reject) {
  // Read and process task data 
  console.log(data);
 
  // Do some work 
  progress(50);
 
  // Finish the task asynchronously 
  setTimeout(function() {
    resolve();
  }, 1000);
});

// exec(command, {maxBuffer: 1024 * 1000}, function(err, stdout, stderr) {
//   if (err) {
//     console.log(stdout);
//     console.log(stderr);
//     res.status(503).send({error: err.message});
//   } else {
//     console.timeEnd("running assignment...");
//     var assign = fs.readFileSync(path + "/assignments.json");
//     res.send(assign);
//   }
// });

// var writeLog = function(filename, logContents) {
//   if (!fs.existsSync(logPath)) {
//     fs.mkdirSync(logPath);
//   }

//   var path = logPath + "/" + filename + ".txt";

//   fs.writeFile(path, logContents, function(err) {
//     if (err) {
//       console.log("error writing to log", filename, err);
//     }
//   });
// };

// router.get("/start/:filename", function(req, res) {
//   var filename = req.params.filename;
//   var path = diskCache.localPath(filename);

//   // return immediately
//   res.send({ ok: 1 });

//   diskCache.ensureFileIsLocal(filename, function() {
//     process.chdir(pipelinePath);

//     var command = "sh get_all_metadata_s3.sh " + filename + " " + escape(path);

//     if (process.env.NODE_ENV !== "production") {
//       command += " dev";
//     }

//     exec(command, function(err, stdout, stderr) {
//       var log = "== stdout ==\n";
//       log += stdout;
//       log += "\n== stderr ==\n";
//       log += stderr;

//       if (err) {
//         setStatus(filename, status.failed);
//       }

//       console.log(log);
//       writeLog(filename, log);
//     });
//   });
// });
