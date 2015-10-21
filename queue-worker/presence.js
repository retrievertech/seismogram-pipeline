var metadata = require('node-ec2-metadata');
var rootRef = require("./rootRef");

var amOnline = rootRef.child(".info/connected");

// see https://www.firebase.com/blog/2013-06-17-howto-build-a-presence-system.html
var instanceId,
    presenceRef;

metadata.getMetadataForInstance('instance-id')
  .then(function(id) {
    instanceId = id;
    presenceRef = rootRef.child("machines_online/"+id);
    connect();
  })
  .fail(function(error) {
    // do something?
  });

function connect() {
  amOnline.on('value', function(snap) {
    if (snap.val()) {
      presenceRef.onDisconnect().remove();
      presenceRef.set(true);
    }
  });
}