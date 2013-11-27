'use strict';

var poop;
function LatestSongsListCtrl($scope, $interval, LatestSongs){
    var maxTimestamp;
    $scope.songs = [];

    // inital populating of list of songs
    LatestSongs.get({}, function(latestSongs){
        $scope.songs = latestSongs.songs;

        // the most recent played song is first
        if(latestSongs.songs.length > 0){
            maxTimestamp = latestSongs.songs[0].timestamp;
        }
    });

    var periodicallyFetchSongs = $interval(function(){
        LatestSongs.get({}, function(latestSongs){
            var song;
            var newSongs = [];

            for(var i=0, l=latestSongs.songs.length; i < l; i++){
                song = latestSongs.songs[i];
                if(song.timestamp > maxTimestamp){
                    newSongs.push(song); // append song to newSongs
                } else {
                    break; // every song after this has already been seen
                }
            }

            if(newSongs.length > 0){
                $scope.songs = newSongs.concat($scope.songs);
                //console.log(new Date() + " - Added " + newSongs.length + " songs");

                maxTimestamp = newSongs[0].timestamp;
                //console.log("New maxTimestamp is now " + maxTimestamp);
            }
        });
    }, 30 * 1000);
}
