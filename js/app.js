'use strict';

angular.module('caaRadio', ['ngRoute', 'caaRadioServices']).
    config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/latest-songs', {templateUrl: 'partials/latest-songs.html', controller: LatestSongsListCtrl}).
        otherwise({redirectTo: '/latest-songs'});
}]);
