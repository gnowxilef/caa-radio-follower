'use strict';

var poop;
function LatestSongsListCtrl($scope, LatestSongs){
    $scope.songs = [];

    // inital populating of list of songs
    LatestSongs.get({}, function(latestSongs){
        $scope.songs = latestSongs.songs;
    });
}
