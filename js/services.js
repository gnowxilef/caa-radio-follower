'use strict';

angular.module('caaRadioServices', ['ngResource']).
factory('LatestSongs', function($resource){
    return $resource('latest.json', {}, {
    });
});
